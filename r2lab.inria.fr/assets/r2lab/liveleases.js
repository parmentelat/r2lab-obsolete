// -*- js-indent-level:4 -*-

/* for eslint */
/*global $ moment io*/
/*global PersistentSlices sidecar_url r2lab_accounts post_xhttp_django*/

"use strict";

////////// provide for array.has()
if (!Array.prototype.has) {
  Array.prototype.has = function(needle) {
      return this.indexOf(needle>=0);
  }
}

let liveleases_options = {

    // set to 'book' for the BOOK page
    mode : 'run',

    // these properties in the fullCalendar object will
    // be traced when debug is set to true
    trace_events : [
	// 'select', 'drop', 'eventDrop', 'eventDragStart', 'eventResize',
	//'eventRender', 'eventMouseover', 'eventMouseout', 
    ],
    debug : true,
}


function liveleases_debug(...args) {
    if (liveleases_options.debug)
	console.log(...args);
}


////////////////////////////////////////
// what we call **slots** are the events attached in the fullCalendar() plugin
// https://fullcalendar.io/docs/event_data/Event_Object/
// they are also called 'client events' 
// https://fullcalendar.io/docs/event_data/clientEvents/
// they have
// (*) visible attributes like 'title', 'start' and 'end'
// (*) they also have a hidden 'id' field, that can be used to
// refer to them from the outside
////
// now the other way around, leases are managed in the API
// they have a slicename, and valid_from valid_until times
// and they have a uuid, that is the internal API lease_id
////
// refreshFromApiLeases's job is to reconcile
// (*) the currently displayed slots (displayed_slots), 
// (*) with what comes in from the API (confirmed_slots)
// 
// whenever a displayed_slot has a uuid, it is used to map it
// to the API (e.g. for tracking updates)
// when it's not the case, it is a newly created slot
// which has been displayed during the short amount of time
// when we're waiting for the API to confirm its creation
// for this we use the slot's id, that is just made of
// title + start + end
////

class LiveLeases {

    constructor(domid, r2lab_accounts) {
	// this.domid is the id of the DOM element that serves 
	// as the basis for fullCalendar
	// typically in our case liveleases_container
	this.domid = domid;

	////////////////////////////////////////
	this.persistent_slices   = new PersistentSlices(r2lab_accounts, 'r2lab');

	this.textcolor_regular   = 'white';
	this.textcolor_pending   = 'black';
	this.textcolor_removing  = 'red';
	
	this.socket              = io.connect(sidecar_url);
	this.dragging            = false;

	this.initial_duration    = 60;
	this.minimal_duration    = 10;
	
    }

    // propagate fullCalendar call to the right jquery element
    fullCalendar(...args) {
	return $(`#${this.domid}`).fullCalendar(...args);
    }

    buildCalendar() {
	let liveleases = this;
	let today  = moment().format("YYYY-MM-DD");
	let showAt = moment().subtract(1, 'hour').format("HH:mm");
	let run_mode = liveleases_options.mode == 'run';
	console.log(`liveleases - sidecar_url = ${sidecar_url}`);
    
	// helpers for popover area 
	let hh_mm = function(date) {
	    return moment(date).format("HH:mm");
	}
	let pretty_content = function(event) {
	    return `${hh_mm(event.start._d)}-${hh_mm(event.end._d)}`;
	};
	
	// the view types that are not read-only
	this.active_views = [
	    'agendaDay', // run mode
	    'agendaOneDay', 'agendaThreeDays', 'agendaWeek',
	];
	
	// Create the calendar
	let calendar_args = {
	    header:
	    run_mode
		? false
		: {
		    left: 'prev,next today',
		    center: 'title',
		    right: 'agendaOneDay,agendaThreeDays,agendaWeek,month,listMonth,listYear',
		},
	    
	    views:
	    run_mode
		? {}
	    : {
		agendaOneDay: {
		    type: 'agenda',
		    duration: { days: 1},
		    buttonText: 'day',
		},
		agendaThreeDays: {
		    type: 'agenda',
		    duration: { days: 3 },
		    buttonText: '3 days'
		},
		agendaWeek: {
		    type: 'agenda',
		    duration: { days: 7 },
		    buttonText: 'week'
		},
		month: {
		    type: 'agenda',
		    duration: { months: 1},
		    buttonText: 'month',
		    selectable: false,
		    editable: false,
		    droppable: false,
		    dblclick: false,
		},
		listMonth: {
		    buttonText: 'list/month',
		},
		listYear: {
		    buttonText: 'list/year',
		}
		    
		
	    },
	    defaultView: run_mode ? 'agendaDay' : 'agendaThreeDays',
	    height: run_mode ? 455 : 2800,
	    contentHeight: run_mode ? undefined : 800,
	    ////////////////////
	    slotDuration: run_mode ? "01:00:00" : "00:10:00",
	    forceEventDuration: true,
	    timezone: 'local',
	    defaultDate: today,
	    selectHelper: false,
	    overlap: false,
	    selectable: true,
	    editable: true,
	    allDaySlot: false,
	    droppable: true,
	    nowIndicator: true,
	    scrollTime: showAt,
	    //Events
	    // this is fired when a selection is made
	    select: function(start, end/*, event, view*/) {
		liveleases.interactiveSelect(start, end);
	    },

	    // this allows things to be dropped onto the calendar
	    drop: function(date/*, event, view*/) {
		let dom = this;
		liveleases.interactiveDrop(dom, date);
	    },

	    // this happens when the event is dragged moved and dropped
	    eventDrop: function(event, delta, revertFunc) {
		liveleases.interactiveEventDrop(event, delta, revertFunc);
	    },
	    // this fires when one event starts to be dragged
	    eventDragStart: function(/*event, jsEvent, ui, view*/) {
		liveleases.dragging = true;
	    },

	    // this fires when one event starts to be dragged
	    eventDragStop: function(/*event, jsEvent, ui, view*/) {
		liveleases.dragging = false;
	    },

	    // this fires when an event is rendered
	    eventRender: function(event, element) {

		$(element).popover({
		    title: event.title,
		    content: pretty_content(event),
		    html: true,
		    placement: 'auto',
		    trigger: 'hover',
		    delay: {"show": 500 }});
		
		// when removing a lease
		// if it's entirely in the past : refuse to remove
		// if it's entirely in the future : delete completely
		// if in the middle : then we want to
		// (*) free the testbed immediately
		// (*) but still keep track of that activity
		// so we try to resize the slot so that it remains in the history
		// but still is out of the way
		element.bind('dblclick', function() {
		    liveleases.interactiveRemove(event, element);
		})
	    },

	    // eventClick: function(event, jsEvent, view) {
	    //   $(this).popover('show');
	    // },
	    
	    //eventMouseover: function(event, jsEvent, view) {
	    //$(this).popover('show');
	    //},
	    
	    eventMouseout: function(/*event, jsEvent, view*/) {
		$(this).popover('hide');
	    },

	    // this is fired when an event is resized
	    eventResize: function(event/*, jsEvent, ui, view, revertFunc*/) {
		liveleases.interactiveResize(event);
	    },

	    // events from Json file
	    events: [],
	};
	// for debugging only
	calendar_args = this.decorate_traced_event(calendar_args);
	
	this.fullCalendar(calendar_args);
    }

    // for debugging: trace events mentioned in  this.trace_events
    decorate_traced_event(calendar_args) {
	let trace_function = function(f) {
	    let wrapped = function(...args) {
		liveleases_debug(`entering calendar ${f.name}`);
		let result = f(...args);
		liveleases_debug(`exiting calendar ${f.name} ->`, result);
		return result;
	    }
	    return wrapped;
	}
	for (let prop of liveleases_options.trace_events) {
	    if ( ! (prop in calendar_args)) {
		liveleases_debug(`liveleases: trace_events: ignoring undefined prop ${prop}`);
	    } else {
		calendar_args[prop] = trace_function(calendar_args[prop])
	    }
	}
	return calendar_args;
    }

    isReadOnlyView() {
	let view = this.fullCalendar('getView').type;
	if (! this.active_views.has(view)) {
	    this.showMessage(`view ${view} is read only`);
	    return true;
	}
    }

    ////////////////////
    // click in the calendar - requires a current slice
    interactiveSelect(start, end) {
	liveleases_debug(`start ${start} - end ${end}`);

	let current_title = this.getCurrentSliceName();
	if ( ! current_title) {
	    this.showMessage("No selected slice..");
	    return;
	}
	
	if (this.isPastDate(end)) {
	    this.fullCalendar('unselect');
	    this.showMessage('This timeslot is in the past!');
	    return;
	}

	[start, end] = this.adaptStartEnd(start, end);
	
	let slot = {
	    title: this.pendingName(current_title),
	    start: start,
	    end: end,
	    overlap: false,
	    editable: false,
	    selectable: false,
	    color: this.getCurrentSliceColor(),
	    textColor: this.textcolor_pending,
	    id: this.slotId(current_title, start, end),
	};
	this.fullCalendar('renderEvent', slot, true);
	this.fullCalendar('unselect');
	this.sendApi('add', slot);
    }


    // dropping a slice into the calendar
    interactiveDrop(dom, date) {

	this.adoptCurrentSlice($(dom))
	let current_title = this.getCurrentSliceName();

	let start = date;
	let end   = moment(date).add(this.initial_duration, 'minutes');
	if (this.isPastDate(end)) {
	    this.fullCalendar('unselect');
	    this.showMessage('This timeslot is in the past!');
	    return false;
	}
	
	[start, end] = this.adaptStartEnd(start, end);
	let slot = {
	    title: this.pendingName(current_title),
	    start: start,
	    end: end,
	    overlap: false,
	    editable: false,
	    selectable: false,
	    color: this.getCurrentSliceColor(),
	    textColor: this.textcolor_pending,
	    id: this.slotId(current_title, start, end),
	};
	this.fullCalendar('renderEvent', slot, true);
	this.fullCalendar('unselect');
	this.sendApi('add', slot);
    }


    // dragging a slot from one place to another
    interactiveEventDrop(slot, delta, revertFunc) {
	if (this.isReadOnlyView()) {
	    return;
	}
	if ( ! confirm("Confirm this change ?")) {
	    revertFunc();
	    return;
	}
	if (this.isPastDate(slot.end)) {
	    this.showMessage('This timeslot is in the past!');
	    revertFunc();
	    return;
	}
	slot.title = this.pendingName(slot.title);
	slot.textColor = this.textcolor_pending;
	this.fullCalendar('updateEvent', slot)
	this.sendApi('edit', slot);
    }

    // double click
    interactiveRemove(slot/*, element*/) {
	if (this.isReadOnlyView()) {
	    return;
	}
	// cannot only remove my slices
	if ( ! this.isMySlice(slot.title) )
	    return;
	// ignore leases in the past no matter what
	if (this.isPastDate(slot.end)) {
	    this.showMessage("This lease is in the past !");
	}
	
	// this is editable, let's confirm
	if ( ! confirm("Confirm removing?")) 
	    return;
	
	slot.title = this.removingName(slot.title);
	slot.textColor = this.textcolor_removing;
	slot.editable = false;
	slot.selectable = false;
	// how many minutes has it been running
	let started = moment().diff(moment(slot.start), 'minutes');
	if (started >= this.minimal_duration) {
	    // this is the case where we can just shrink it
	    liveleases_debug(`up ${started} mn : delete slot by shrinking it down`)
	    // set end to now and, let the API round it 
	    slot.end = moment();
	    this.fullCalendar( 'updateEvents', slot);
	    this.sendApi('edit', slot);
	} else {
	    // either it's in the future completely, or has run for too
	    // short a time that we can keep it, so delete altogether
	    liveleases_debug(`up ${started} mn : delete slot completely`)
	    this.fullCalendar( 'removeEvents', slot);
	    this.sendApi('del', slot);
	}
    }


    interactiveResize(slot) {
	if ( ! this.isMySlice(slot.title)) {
	    // should not happen..
	    this.showMessage("Not owner");
	    return;
	}
	if ( ! confirm("Confirm this change?")) {
	    // some bug in revertFunc
	    // must take the last date time and set manually
	    return;
	} 
	slot.title = this.pendingName(slot.title);
	slot.textColor = this.textcolor_pending;
	slot.editable = false;
	this.fullCalendar( 'updateEvent', slot);
	this.sendApi('edit', slot);
    }


    //////////
    sliceElementId(id){
	return id.replace(/\./g, '');
    }

    // make this the new current slice from a jquery element
    // associated to the clicked slice on the LHS
    adoptCurrentSlice(slice_element){
	let title  = $.trim(slice_element.text());
	this.persistent_slices.set_current(title);
	this.outlineCurrentSlice(title)
    }


    outlineCurrentSlice(name){
	let id = this.sliceElementId(name);
	$(".noactive").removeClass('slice-active');
	$(`#${id}`).addClass('slice-active');
    }


    getCurrentSliceName(){
	return this.persistent_slices.get_current_slice_name();
    }
    getCurrentSliceColor(){
	return this.persistent_slices.get_current_slice_color();
    }
    getMySlicesNames(){
	return this.persistent_slices.my_slices_names();
    }

    shortName(name){
	let new_name = name;
	new_name = name.replace('onelab.', '');
	return new_name
    }

    getMySlicesShortNames(){
	return this.getMySlicesNames().map(name => this.shortName(name));
    }

    ////////////////////
    isPastDate(end)    { return (moment().diff(end, 'minutes') > 0) }
    pendingName(name)  { return `${this.resetName(name)} (pending)`; }
    removingName(name) { return `${this.resetName(name)} (removing)`; }
    resetName(name) {
	return name
	    .replace(' (pending)', '')
	    .replace(' (removing)', '')
    }
    slotId(title, start, end){
	let m_start = moment(start)._d.toISOString();
	let m_end   = moment(end)._d.toISOString();
	return `${title}-from-${m_start}-until-${m_end}`;
    }

    ////////////////////

    adaptStartEnd(start, end) {
	let now = new Date();0
	let started = moment(now).diff(moment(start), 'minutes');
	if (started > 0){
	    let s   = moment(now).diff(moment(start), 'minutes')
	    let ns  = moment(start).add(s, 'minutes');
	    start = ns;
	    //end = moment(end).add(1, 'hour');
	}
	// round to not wait
	start = moment(start).floor(this.minimal_duration, 'minutes');
	return [start, end];
    }


    // go as deep as possible in an object
    dig_xpath(obj, xpath) {
	let result = obj;
	for (let attr of xpath) {
	    if ((typeof result == 'object') && (attr in result)) {
		result = result[attr];
	    } else {
		break;
	    }
	}
	return result;
    }

    showMessage(msg, type){
	let cls   = 'danger';
	let title = 'Ooops!'
	if (type == 'info'){
	    cls   = 'info';
	    title = 'Info:'
	}
	if (type == 'success'){
	    cls   = 'success';
	    title = 'Yep!'
	}
	$('html,body').animate({'scrollTop' : 0},400);
	$('#messages').removeClass().addClass('alert alert-'+cls);
	$('#messages').html(`<strong>${title}</strong> ${msg}`);
	$('#messages').fadeOut(200).fadeIn(200).fadeOut(200).fadeIn(200);
	$('#messages').delay(20000).fadeOut();
    }


    sendApi(action, slot){
	liveleases_debug("SENDING", action, slot);
	let liveleases = this;
	let verb = null;
	let request = null;

	if (action == 'add'){
	    verb = 'add';
	    request = {
		"slicename"  : this.resetName(slot.title),
		"valid_from" : slot.start._d.toISOString(),
		"valid_until": slot.end._d.toISOString()
	    };
	} else if (action == 'edit'){
	    verb = 'update';
	    request = {
		"uuid" : slot.uuid,
		"valid_from" : slot.start._d.toISOString(),
		"valid_until": slot.end._d.toISOString()
	    };
	} else if (action == 'del'){
	    verb = 'delete';
	    request = {
		"uuid" : slot.uuid,
	    };
	} else {
	    liveleases_debug(`sendApi : Unknown action ${action}`);
	    return false;
	}
	post_xhttp_django(`/leases/${verb}`, request, function(xhttp) {
	    if (xhttp.readyState == 4) {
		// this triggers a refresh of the leases once the sidecar server answers back
		liveleases.requestUpdateFromApi();
		////////// temporary
		// in all cases, show the results in console, in case we'd need to improve this
		// logic further on in the future
		liveleases_debug(`upon ajax POST: xhttp.status = ${xhttp.status}`);
		////////// what should remain
		if (xhttp.status != 200) {
		    // this typically is a 500 error inside django
		    // hard to know what to expect..
		    liveleases.showMessage(`Something went wrong when managing leases with code ${xhttp.status}`);
		} else {
		    // the http POST has been successful, but a lot can happen still
		    // for starters, are we getting a JSON string ?
		    try {
			let obj = JSON.parse(xhttp.responseText);
			if (obj.error) {
			    liveleases.showMessage(
				liveleases.dig_xpath(obj, ['error', 'exception', 'reason']));
			} else {
			    liveleases_debug("JSON.parse ->", obj);
			}
		    } catch(err) {
			liveleases.showMessage(`unexpected error while anayzing django answer ${err}`);
			console.log(err.stack);
		    }
		}
	    }
	});
    }


    getSliceColor(slicename){
	return this.persistent_slices.get_slice_color(slicename);
    }


    isMySlice(slicename){
	let pslice = this.persistent_slices.record_slice(slicename);
	return pslice.mine;
    }

    // incoming is an array of pslices as defined in
    // persistent_slices.js
    buildInitialSlicesBox(pslices) {
	let liveleases = this;
	liveleases_debug('buildInitialSlicesBox');
	let slices = $("#my-slices");
	let legend = "Double click in slice to select default";
	slices.html(`<h4 align="center" data-toggle="tooltip" title="${legend}">drag & drop to book</h4>`);

	pslices.forEach(
	    function(pslice) {
		// show only slices that are mine
		if ( ! pslice.mine )
		    return;
		// need to run shortName ?
		let name = pslice.name;
		let color = pslice.color;
		slices
		    .append(
			$("<div />")
			    .addClass('fc-event')
			    .attr("style", `background-color: ${color}`)
			    .text(name))
		    .append(
			$("<div />")
			    .attr("id", liveleases.sliceElementId(name))
			    .addClass('noactive'));
	    });
	this.makeSliceBoxDraggable();
    }

    makeSliceBoxDraggable() {
	$('#my-slices .fc-event').each(function() {
	    $(this).draggable({
		zIndex: 999,
		revert: true,
		revertDuration: 0
	    });
	});
    }


    refreshFromApiLeases(confirmed_slots) {
	liveleases_debug(`refreshFromApiLeases with ${confirmed_slots.length} API leases`)
	// not while dragging
	if (this.dragging)
	    return;

	////////// compute difference between displayed and confirmed slots
	// gather all slots currently displayed
	let displayed_slots = this.fullCalendar( 'clientEvents' );

	// initialize 
	for (let displayed_slot of displayed_slots)
	    displayed_slot.confirmed = false;
	for (let confirmed_slot of confirmed_slots)
	    confirmed_slot.displayed = false;
	
	// scan all confirmed
	for (let confirmed_slot of confirmed_slots) {
	    let confirmed_id = this.slotId(confirmed_slot.title,
					   confirmed_slot.start,
					   confirmed_slot.end);
	    // scan all displayed
	    for (let displayed_slot of displayed_slots) {
		// already paired visual slots can be ignored
		if (displayed_slot.confirmed)
		    continue;
		//liveleases_debug(`matching CONFIRMED ${confirmed_slot.title} ${confirmed_slot.uuid}`
		//		 + ` with displayed ${displayed_slot.title}`);
		let match = (displayed_slot.uuid)
		    ? (confirmed_slot.uuid == displayed_slot.uuid)
		    : (confirmed_id == displayed_slot.id);

		if (match) {
		    //liveleases_debug(`MATCH`);
		    // update displayed from confirmed
		    displayed_slot.uuid = confirmed_slot.uuid;
		    displayed_slot.title = confirmed_slot.title;
		    displayed_slot.start = moment(confirmed_slot.start);
		    displayed_slot.end = moment(confirmed_slot.end);
		    displayed_slot.textColor = this.textcolor_regular;
		    // mark both as matched
		    displayed_slot.confirmed = true;
		    confirmed_slot.displayed = true;
		    continue;
		}
	    }
	}
		    

	// update all slots, in case their title/start/end/colors have changed
	let slots = this.fullCalendar( 'clientEvents' );
	liveleases_debug(`refreshing ${slots.length} slots`);
	this.fullCalendar('updateEvents', slots);

	//	// remove displayed slots that are no longer relevant
	this.fullCalendar('removeEvents', slot => ! slot.confirmed);
//	let old_slots = displayed_slots.filter(slot => ! slot.confirmed);
//	liveleases_debug(`should remove ${old_slots.length} slots ...`);
//	old_slots.forEach((slot) => this.fullCalendar('removeEvents', slot.id));
//	try {
//	    this.fullCalendar('removeEvents', slot => ! slot.confirmed);
//	} catch (err) {
//	    console.log(`Could not remove zombies`, err.stack);
//	}
		
	// create slots in calendar for confirmed slots not yet displayed
	// typically useful at startup, and for stuff  created by someone else
	let new_slots = confirmed_slots.filter( slot => ! slot.displayed);
	liveleases_debug(`creating ${new_slots.length} slots`);
	this.fullCalendar('renderEvents', new_slots, true);
    }

    // use this to ask for an immediate refresh
    // of the set of leases
    // of course it must be called *after* the actual API call
    // via django
    requestUpdateFromApi(){
	let msg = "INIT";
	liveleases_debug("sending on request:leases -> ", msg);
	this.socket.emit('request:leases', msg);
    }

    listenToApiChannel(){
	let liveleases = this;
	this.socket.on('info:leases', function(json){
	    let api_slots = liveleases.parseLeases(json);
	    liveleases_debug(`incoming on info:leases ${api_slots.length} leases`, json);
	    liveleases.refreshFromApiLeases(api_slots);
	    liveleases.outlineCurrentSlice(liveleases.getCurrentSliceName());
	});
    }

    // 
    parseLeases(json) {
	let liveleases = this;
	let leases = JSON.parse(json);
	liveleases_debug("parseLeases", leases);

	return leases.map(function(lease){
	    let title = liveleases.shortName(lease.slicename);
	    let start = lease.valid_from;
	    let end = lease.valid_until;
	    // remember that slice
	    liveleases.persistent_slices.record_slice(title);
	    
	    return { title : title,
		     uuid : String(lease.uuid),
		     start : start,
		     end : end,
		     id : liveleases.slotId(title, start, end),
		     color : liveleases.getSliceColor(title),
		     editable : (liveleases.isMySlice(title)
				 && !liveleases.isPastDate(end)),
		     overlap : false
		   }
	})
    }

    ////////////////////////////////////////
    main(){
	
	this.buildInitialSlicesBox(this.persistent_slices.pslices);
	this.buildCalendar();
	this.outlineCurrentSlice(this.getCurrentSliceName());
	
	this.listenToApiChannel();

	this.requestUpdateFromApi();
	
	let run_mode = liveleases_options.mode == 'run';
	if (run_mode) {
	    // don't do this in book mode, it would change all days
	    $('.fc-day-header').html('today');
	}
	
	let liveleases = this;
	let slices = $('#my-slices .fc-event');
	slices.dblclick(function() {
	    liveleases.adoptCurrentSlice($(this));
	});
	
	$('body').on('click', 'button.fc-month-button', function() {
	    liveleases.showMessage('This view is read only!', 'info');
	});

    }
}


// global - only for debugging and convenience
let the_liveleases;

$(function() {
    the_liveleases = new LiveLeases('liveleases_container', r2lab_accounts);
    the_liveleases.main();
})
