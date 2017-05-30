// -*- js-indent-level:4 -*-
// this requires xhttp-django.js
"use strict";

/* for eslint */
/*global $ moment io*/
/*global PersistentSlices sidecar_url r2lab_accounts post_xhttp_django*/

let liveleases_options = {

    // set to 'book' for the BOOK page
    mode : 'run',

    // these properties in the fullCalendar object will
    // be traced when debug is set to true
    trace_events : [
	'select', 'drop', 'eventDrop', 'eventDragStart', 'eventResize',
	//'eventRender', 'eventMouseover', 'eventMouseout', 
    ],
    debug : true,
}


function liveleases_debug(...args) {
    if (liveleases_options.debug)
	console.log(...args);
}


////////////////////////////////////////
// events attached in the fullCalendar() plugin have
// (*) visible attributes like 'title', 'start' and 'end'
// (*) they also have a more subtle 'id' field, that can be used to
// refer to them from the outside
////
// now the other way around, leases are managed in the API
// also have of course a slicename, and start and end times
// and they have a uuid, that is the internal API lease_id
////
// so it is tempting to use this api lease_id as a event_id
// the only time when this is not convenient is when
// a lease is created for the first time, as we have no idea
// what the lease_id is going to be and so we need something else
// during that time
////

// xxx assuming the_persistent_slices has been loaded already
// see r2lab0user.js

class LiveLeases {

    constructor(domid, r2lab_accounts) {
	this.domid = domid;

	////////////////////////////////////////
	this.persistent_slices   = new PersistentSlices(r2lab_accounts, 'r2lab');

	// not clear what this contains, essentially it looks like a temporary
	this.tmpLeases           = [];
	// the ids of all the events known to the API
	this.confirmedLeases     = [];

	this.textcolor_pending   = 'black';
	this.textcolor_removing  = 'red';
	this.keepOldEvent        = null;
	
	this.socket              = io.connect(sidecar_url);
	this.dragging            = false;

	this.initial_duration    = 30;
	this.minimal_duration    = 10;
	
    }


    resetConfirmedLeases(){
	this.confirmedLeases = [];
    }
    /* used */
    addConfirmed(title, start, end) {
	let local_id = this.getLocalId(title, start, end);
	this.confirmedLeases.push(local_id);
    }

    tmpLeasesDel(id){
	let idx = this.tmpLeases.indexOf(id);
	this.tmpLeases.splice(idx, 1);
    }
    tmpLeasesReset(){
	this.tmpLeases = [];
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
	
	// Create the calendar
	let calendar_args = {
	    header:
	    run_mode
		? false
		: {
		    left: 'prev,next today',
		    center: 'title',
		    right: 'agendaDay,agendaThreeDay,agendaWeek,month',
		},
	    
	    views:
	    run_mode
		? {}
	    : {
		agendaThreeDay: {
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
		    selectable: false,
		    editable: false,
		    droppable: false,
		    dblclick: false,
		}
	    },
	    defaultView: run_mode ? 'agendaDay' : 'agendaThreeDay',
	    height: run_mode ? 455 : 770,
	    ////////////////////
	    defaultTimedEventDuration: '00:10:00',
	    slotDuration: "01:00:00",
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
	    select: function(start, end, event, view) {
		if (liveleases.isPastDate(end)) {
		    $(`#${liveleases.domid}`).fullCalendar('unselect');
		    liveleases.sendMessage('This timeslot is in the past!');
		    return false;
		}
		let my_title = liveleases.getCurrentSliceName();
		let eventData;
		[start, end] = liveleases.adaptStartEnd(start, end);
		
		if (my_title) {
		    eventData = {
			title: liveleases.pendingName(my_title),
			start: start,
			end: end,
			overlap: false,
			editable: false,
			selectable: false,
			color: liveleases.getCurrentSliceColor(),
			textColor: liveleases.textcolor_pending,
			id: liveleases.getLocalId(my_title, start, end),
		    };
		    liveleases.updateLeases('addLease', eventData);
		}
		$(`#${liveleases.domid}`).fullCalendar('unselect');
	    },

	    // this allows things to be dropped onto the calendar
	    drop: function(date, event, view) {
		let start = date;
		let end   = moment(date).add(liveleases.initial_duration, 'minutes');
		if (liveleases.isPastDate(end)) {
		    $(`#${liveleases.domid}`).fullCalendar('unselect');
		    liveleases.sendMessage('This timeslot is in the past!');
		    return false;
		}

		liveleases.setSlice($(this))
		[start, end] = liveleases.adaptStartEnd(start, end);

		let my_title = liveleases.getCurrentSliceName();
		let eventData;
		if (my_title) {
		    eventData = {
			title: liveleases.pendingName(my_title),
			start: start,
			end: end,
			overlap: false,
			editable: false,
			selectable: false,
			color: liveleases.getCurrentSliceColor(),
			textColor: liveleases.textcolor_pending,
			id: liveleases.getLocalId(my_title, start, end),
		    };
		    liveleases.updateLeases('addLease', eventData);
		}
	    },

	    // this happens when the event is dragged moved and dropped
	    eventDrop: function(event, delta, revertFunc) {
		let view = $(`#${liveleases.domid}`).fullCalendar('getView').type;
		if (view != 'month'){
		    if (!confirm("Confirm this change ?")) {
			revertFunc();
		    } else if (liveleases.isPastDate(event.end)) {
			revertFunc();
			liveleases.sendMessage('This timeslot is in the past!');
		    } else {
			let newLease = liveleases.createLease(event);
			newLease.title = liveleases.pendingName(event.title);
			newLease.editable = false;
			newLease.textColor = liveleases.textcolor_pending;
			liveleases.removeElementFromCalendar(newLease.id);
			liveleases.updateLeases('editLease', newLease);
		    }
		} else {
		    revertFunc();
		}
	    },

	    // this fires when one event starts to be dragged
	    eventDragStart: function(event, jsEvent, ui, view) {
		this.keepOldEvent = event;
		this.dragging = true;
	    },

	    // this fires when one event starts to be dragged
	    eventDragStop: function(event, jsEvent, ui, view) {
		this.keepOldEvent = event;
		this.dragging = false;
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
		
		let view = $(`#${liveleases.domid}`).fullCalendar('getView').type;
		if(view != 'month'){
		    element.bind('dblclick', function() {
			if (liveleases.isMySlice(event.title) && event.editable == true ) {
			    if (!confirm("Confirm removing?")) {
				// XXX undefined revertFunc XXX
				revertFunc();
			    }
			    let newLease = liveleases.createLease(event);
			    let now = new Date();
			    let started = moment(now).diff(moment(event.start), 'minutes');
			    if(started >= liveleases.minimal_duration){
				newLease.start = moment(event.start);
				newLease.end = moment(event.start).add(started, 'minutes');
				newLease.title = liveleases.removingName(event.title);
				newLease.textColor = liveleases.textcolor_removing;
				newLease.editable = false;
				newLease.selectable = false;
				newLease.id = liveleases.getLocalId(
				    event.title+'new', newLease.start, newLease.end),
				liveleases.removeElementFromCalendar(newLease.id);
				liveleases.updateLeases('editLease', newLease);
			    } else {
				liveleases.removeElementFromCalendar(event.id);
				liveleases.addElementToCalendar(newLease);
				liveleases.updateLeases('delLease', newLease);
			    }
			}
			if (liveleases.isMySlice(event.title) && liveleases.isPending(event.title)) {
			    if (confirm("This event is not confirmed yet. Are you sure to remove?")) {
				let newLease = liveleases.createLease(event);
				newLease.title = liveleases.removingName(event.title);
				newLease.textColor = liveleases.textcolor_removing;
				newLease.editable = false;
				liveleases.removeElementFromCalendar(event.id);
				liveleases.addElementToCalendar(newLease);
				liveleases.updateLeases('delLease', newLease);
			    }
			}
			if (liveleases.isMySlice(event.title) && liveleases.isFailed(event.title)) {
			    liveleases.removeElementFromCalendar(event.id);
			}
		    });
		}},

	    // eventClick: function(event, jsEvent, view) {
	    //   $(this).popover('show');
	    // },
	    
	    //eventMouseover: function(event, jsEvent, view) {
	    //$(this).popover('show');
	    //},
	    
	    eventMouseout: function(event, jsEvent, view) {
		$(this).popover('hide');
	    },

	    // this is fired when an event is resized
	    eventResize: function(event, jsEvent, ui, view, revertFunc) {
		if (!confirm("Confirm this change?")) {
		    //some bug in revertFunc
		    //must take the last date time and set manually
		    return;
		} else if (liveleases.isMySlice(event.title)) {
		    let newLease = liveleases.createLease(event);
		    newLease.title = liveleases.pendingName(event.title);
		    newLease.textColor = liveleases.textcolor_pending;
		    newLease.editable = false;
		    liveleases.removeElementFromCalendar(newLease.id);
		    liveleases.updateLeases('editLease', newLease);
		}
	    },
	    // events from Json file
	    events: [],
	};
	calendar_args = this.decorate_traced_event(calendar_args);
	$(`#${this.domid}`).fullCalendar(calendar_args);
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
		console.log(`liveleases: trace_events: ignoring undefined prop ${prop}`);
	    } else {
		calendar_args[prop] = trace_function(calendar_args[prop])
	    }
	}
	return calendar_args;
    }


    ////////////////////////////////////////
    main(){
	
	this.buildInitialSlicesBox(this.persistent_slices.pslices);
	this.buildCalendar();
	this.setCurrentSliceBox(this.getCurrentSliceName());
	
	this.listenLeases();

	this.refreshLeases();
	
	let run_mode = liveleases_options.mode == 'run';
	if (run_mode) {
	    // don't do this in book mode, it would change all days
	    $('.fc-day-header').html('today');
	}
	
	let slice = $('#my-slices .fc-event');
	let liveleases = this;
	slice.dblclick(function() {
	    liveleases.setSlice($(this));
	});
	
	$('body').on('click', 'button.fc-month-button', function() {
	    this.sendMessage('This view is read only!', 'info');
	});

	//////////
	
    }


    //////////
    sliceElementId(id){
	return id.replace(/\./g, '');
    }


    setSlice(slice_element){
	let color = slice_element.css("background-color");
	let name  = $.trim(slice_element.text());
	console.log("setSlice ->", name);
	this.persistent_slices.set_current(name);
	this.setCurrentSliceBox(name)
    }


    setCurrentSliceBox(element){
	let id = this.sliceElementId(element);
	$(".noactive").removeClass('slice-active');
	$("#"+id).addClass('slice-active');
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
    pendingName(name){
	return `${this.resetName(name)} (pending)`;
    }
    removingName(name){
	return `${this.resetName(name)} (removing)`;
    }
    failedName(name){
	return `${this.resetName(name)} * failed  *`;
    }
    resetName(name) {
	return name
	    .replace(' (pending)', '')
	    .replace(' (removing)', '')
	    .replace(' * failed *', '');
    }


    isRemoving(title){
	let removing = true;
	if(title.indexOf('(removing)') == -1){
	    removing = false;
	}
	return removing;
    }


    isPending(title){
	let pending = true;
	if(title.indexOf('(pending)') == -1){
	    pending = false;
	}
	return pending;
    }


    isNightly(title){
	let nightly = false;
	if (title) {
	    if(title.indexOf('nightly') > -1){
		nightly = true;
	    }
	}
	return nightly;
    }


    isFailed(title){
	let failed = true;
	if(title.indexOf('* failed *') == -1){
	    failed = false;
	}
	return failed;
    }


    removeElementFromCalendar(id){
	$(`#${this.domid}`).fullCalendar('removeEvents', id );
    }


    getLocalId(title, start, end){
	let m_start = moment(start)._d.toISOString();
	let m_end   = moment(end)._d.toISOString();
	return `${title}-from-${m_start}-until-${m_end}`;
    }


    addElementToCalendar(element){
	$(`#${this.domid}`).fullCalendar('renderEvent', element, true );
    }


    createLease(lease){
	let newLease         = new Object();
	newLease.id          = lease.id
	newLease.uuid        = lease.uuid
	newLease.title       = lease.title
	newLease.start       = lease.start
	newLease.end         = lease.end
	newLease.overlap     = lease.overlap
	newLease.editable    = lease.editable
	newLease.selectable  = lease.selectable
	newLease.color       = lease.color
	newLease.textColor   = lease.textColor

	return newLease;
    }


    isPastDate(end){
	let past = false;
	if(moment().diff(end, 'minutes') > 0){
	    past = true;
	}
	return past;
    }


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


    sendMessage(msg, type){
	let cls   = 'danger';
	let title = 'Ooops!'
	if(type == 'info'){
	    cls   = 'info';
	    title = 'Info:'
	}
	if(type == 'success'){
	    cls   = 'success';
	    title = 'Yep!'
	}
	$('html,body').animate({'scrollTop' : 0},400);
	$('#messages').removeClass().addClass('alert alert-'+cls);
	$('#messages').html(`<strong>${title}</strong> ${msg}`);
	$('#messages').fadeOut(200).fadeIn(200).fadeOut(200).fadeIn(200);
	$('#messages').delay(30000).fadeOut();
    }


    // use this to ask for an immediate refresh
    // of the set of leases
    // of course it must be called *after* the actual API call
    // via django
    refreshLeases(){
	let msg = "INIT";
	liveleases_debug("sending on request:leases -> ", msg);
	this.socket.emit('request:leases', msg);
    }

    // show action immediately before it becomes confirmed
    showImmediate(action, event) {
	liveleases_debug("showImmediate", action);
	if (action == 'add'){
	    let lease  = this.createLease(event);
	    $(`#${this.domid}`).fullCalendar('renderEvent', lease, true );
	} else if (action == 'edit'){
	    let lease  = this.createLease(event);
	    this.removeElementFromCalendar(lease.id);
	    $(`#${this.domid}`).fullCalendar('renderEvent', lease, true );
	} else if (action == 'del'){
	    let lease  = this.createLease(event);
	    this.removeElementFromCalendar(lease.id);
	    $(`#${this.domid}`).fullCalendar('renderEvent', lease, true );
	}
    }

    listenLeases(){
	let liveleases = this;
	this.socket.on('info:leases', function(json){
	    let leasesbooked = liveleases.parseLeases(json);
	    liveleases_debug(`incoming on info:leases ${leasesbooked.length} leases`, json);
	    liveleases.refreshCalendar(leasesbooked);
	    liveleases.setCurrentSliceBox(liveleases.getCurrentSliceName());
	});
    }


    updateLeases(action, event){
	if (action == 'addLease') {
	    this.showImmediate('add', event);
	    this.queueAction2('add', event);
	} else if (action == 'editLease'){
	    this.showImmediate('edit', event);
	    this.queueAction2('edit', event);
	} else if (action == 'delLease') {
	    if(    ($.inArray(event.id, this.tmpLeases) == -1)
		&& (event.title.indexOf('* failed *') > -1) ){
		this.removeElementFromCalendar(event.id);
	    } else {
		this.queueAction2('del', event);
		this.showImmediate('del', event);
	    }
	}
    }


    queueAction2(action, data){
	liveleases_debug("QUEUING", action, data);
	let liveleases = this;
	let verb = null;
	let request = null;

	if (action == 'add'){
	    verb = 'add';
	    request = {
		"slicename"  : this.resetName(data.title),
		"valid_from" : data.start._d.toISOString(),
		"valid_until": data.end._d.toISOString()
	    };
	    this.tmpLeases.push(data.id);
	} else if (action == 'edit'){
	    verb = 'update';
	    request = {
		"uuid" : data.uuid,
		"valid_from" : data.start._d.toISOString(),
		"valid_until": data.end._d.toISOString()
	    };
	} else if (action == 'del'){
	    verb = 'delete';
	    request = {
		"uuid" : data.uuid,
	    };
	    liveleases.tmpLeasesDel(data.id);
	} else {
	    console.log(`queueAction2 : Unknown action ${action}`);
	    return false;
	}
	post_xhttp_django(`/leases/${verb}`, request, function(xhttp) {
	    if (xhttp.readyState == 4) {
		// this triggers a refresh of the leases once the sidecar server answers back
		liveleases.refreshLeases();
		////////// temporary
		// in all cases, show the results in console, in case we'd need to improve this
		// logic further on in the future
		liveleases_debug(`upon ajax POST: xhttp.status = ${xhttp.status}`);
		////////// what should remain
		if (xhttp.status != 200) {
		    // this typically is a 500 error inside django
		    // hard to know what to expect..
		    liveleases.sendMessage(`Something went wrong when managing leases with code ${xhttp.status}`);
		} else {
		    // the http POST has been successful, but a lot can happen still
		    // for starters, are we getting a JSON string ?
		    try {
			let obj = JSON.parse(xhttp.responseText);
			if (obj.error) {
			    liveleases.sendMessage(
				obj.error.exception.reason
				    || obj.error.exception
				    || obj.error)
			} else {
			    liveleases_debug("JSON.parse ->", obj);
			}
		    } catch(err) {
			liveleases.sendMessage(`unexpected error while anayzing django answer ${err}`);
		    }
		}
	    }
	});
    }


    range(start, end) {
	return Array(end-start).join(0).split(0).map(function(val, id) {return id+start});
    }


    getColorLease(slicename){
	return this.persistent_slices.get_slice_color(slicename);
    }


    isMySlice(slicename){
	console.log("isMySlice", slicename);
	let pslice = this.persistent_slices.record_slice(slicename);
	return pslice.mine;
    }

    isPresent(element, list){
	let present = false;

	if ($.inArray(element, list) > -1){
	    present = true;
	}
	return present;
    }


    // incoming is a list of events suitable for fullCalendar
    // i.e. with fields like title, start, end and id 
    buildSlicesBox(leases) {
	let liveleases = this;
	let persistent_slices = this.persistent_slices;
	liveleases_debug('buildSlicesBox');
	let slices = $("#my-slices");

	leases.forEach(
	    function(lease) {
		let slicename = lease.title;
		let pslice = persistent_slices.get_pslice(slicename);
		// already present / skip it
		if (pslice)
		    return;
		pslice = persistent_slices.record_slice(slicename);
		slices
		    .append(
			$("<div/>")
			    .addClass('fc-event')
			    .attr("style", `background-color: ${pslice.color}`)
			    .text(pslice.name))
		    .append(
			$("<div/>")
			    .attr("id", liveleases.sliceElementId(pslice.name))
			    .addClass('noactive'));
	    });
	this.makeSliceBoxDraggable();
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


    refreshCalendar(events) {
	let liveleases = this;
	// xxx ugly use of global
	if ( ! this.dragging){
	    $.each(events, function(key, event){
		liveleases_debug(`refreshCalendar : lease = ${event.title}: ${event.start} .. ${event.end}`);
		liveleases.removeElementFromCalendar(event.id);
		$(`#${liveleases.domid}`).fullCalendar('renderEvent', event, true);
	    });

	    let each_removing = $(`#${liveleases.domid}`).fullCalendar( 'clientEvents' );
	    $.each(each_removing, function(k, obj){
		// when click in month view all 'thousands' of nightly comes.
		// Maybe reset when comeback from month view (not implemented)
		if (!liveleases.isNightly(obj.title) && obj.title) {
		    if (liveleases.isRemoving(obj.title)){
			liveleases.removeElementFromCalendar(obj.id);
		    } else if (obj.uuid && liveleases.isPending(obj.title)){
			liveleases.removeElementFromCalendar(obj.id);
		    } else if (!liveleases.isPresent(obj.id, liveleases.confirmedLeases) &&
			       !liveleases.isPending(obj.title) && !liveleases.isRemoving(obj.title) ){
			liveleases.removeElementFromCalendar(obj.id);
		    } else if (
			/*isPresent(obj.id, liveleases.tmpLeases) &&*/
			liveleases.isPending(obj.title) && !obj.uuid ){
			liveleases.removeElementFromCalendar(obj.id);
		    }
		}
	    });

	    liveleases.tmpLeasesReset();
	}
    }


    parseLeases(json) {
	let liveleases = this;
	let data = JSON.parse(json);
	liveleases_debug("parseLeases", data);

	let leases = [];
	liveleases.resetConfirmedLeases();
	
	data.forEach(function(lease){
	    let newLease = new Object();
	    newLease.title = liveleases.shortName(lease.slicename);
	    newLease.uuid = String(lease.uuid);
	    newLease.start = lease.valid_from;
	    newLease.end = lease.valid_until;
	    newLease.id = liveleases.getLocalId(newLease.title, newLease.start, newLease.end);
	    newLease.color = liveleases.getColorLease(newLease.title);
	    newLease.editable = (liveleases.isMySlice(newLease.title)
				 && !liveleases.isPastDate(newLease.end));
	    newLease.overlap = false;

	    leases.push(newLease);
	    liveleases.addConfirmed(newLease.title, newLease.start, newLease.end);

	});

	this.buildSlicesBox(leases);
	return leases;
    }
}


// global - only for debugging and convenience
let the_liveleases;

$(function() {
    the_liveleases = new LiveLeases('liveleases_container', r2lab_accounts);
    the_liveleases.main();
})
