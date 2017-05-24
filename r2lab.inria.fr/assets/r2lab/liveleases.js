// -*- js-indent-level:4 -*-
// this requires xhttp-django.js
"use strict";

// create this object with mode='run' or mode='book'
// e.g. $(function() {let the_leases = new LiveLeases('run', 'container-leases'); the_leases.main(); })

let liveleases_options = {

    // set to 'book' for the BOOK page
    mode : 'run',

    // these properties in the fullCalendar object will
    // be traced when debug is set to true
    trace_events : [
	'select', 'drop', 'eventDrop', 'eventDragStart', 'eventResize',
	//'eventRender', 'eventMouseover',
	'eventMouseout', 
    ],
    debug : true,
}


function liveleases_debug(...args) {
    if (liveleases_options.debug)
	console.log(...args);
}


////////////////////////////////////////
class LiveLeases {

    constructor(mode, domid) {
	this.mode = mode;
	this.domid = domid;

	////////////////////////////////////////
	// also needs some cleanup in the actionsQueue/actionsQueued area
	
	this.my_slices_name      = r2lab_accounts.map((account) => account.name);
	
	this.my_slices_color     = [];
	this.known_slices        = [];

	this.actionsQueue        = [];
	this.actionsQueued       = [];
	this.current_slice_name  = current_slice.name;
	this.current_slice_color = '#DDD';
	this.current_leases      = null;
	this.color_pending       = '#FFFFFF';
	this.color_removing      = '#FFFFFF';
	this.keepOldEvent        = null;
	
	this.socket              = io.connect(sidecar_url);
	this.refresh             = true;
	this.currentTimezone     = 'local';
	this.nightly_slice_name  = 'inria_r2lab.nightly'
	this.nightly_slice_color = '#000000';
	
    }


    buildCalendar(initial_events_json) {
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
		? {
		    agendaTwoDay: {
			type: 'agenda',
			duration: { days: 2},
			buttonText: '2 days',
		    }
		}
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
	    defaultTimedEventDuration: '00:01:00',
	    slotDuration: "01:00:00",
	    forceEventDuration: true,
	    timezone: liveleases.currentTimezone,
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
			textColor: liveleases.color_pending,
			id: liveleases.getLocalId(my_title, start, end),
		    };
		    liveleases.updateLeases('addLease', eventData);
		}
		$(`#${liveleases.domid}`).fullCalendar('unselect');
	    },

	    // this allows things to be dropped onto the calendar
	    drop: function(date, event, view) {
		let start = date;
		let end   = moment(date).add(60, 'minutes');
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
			textColor: liveleases.color_pending,
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
			newLease.textColor = liveleases.color_pending;
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
		this.refresh = false;
	    },

	    // this fires when one event starts to be dragged
	    eventDragStop: function(event, jsEvent, ui, view) {
		this.keepOldEvent = event;
		this.refresh = true;
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
				revertFunc();
			    }
			    let newLease = liveleases.createLease(event);
			    let now = new Date();
			    let started = moment(now).diff(moment(event.start), 'minutes');
			    if(started >= 10){
				newLease.start = moment(event.start);
				newLease.end = moment(event.start).add(started, 'minutes');
				newLease.title = liveleases.removingName(event.title);
				newLease.textColor = liveleases.color_removing;
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
				newLease.textColor = liveleases.color_removing;
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
		console.log('inside eventMouseout, this & $(this)= ', this, $(this));
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
		    newLease.textColor = liveleases.color_pending;
		    newLease.editable = false;
		    liveleases.removeElementFromCalendar(newLease.id);
		    liveleases.updateLeases('editLease', newLease);
		}
	    },
	    //Events from Json file
	    events: initial_events_json,
	};
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
	    if ( ! prop in calendar_args) {
		console.log(`liveleases: trace_events: ignoring undefined prop ${prop}`);
	    } else {
		calendar_args[prop] = trace_function(calendar_args[prop])
	    }
	}
	$(`#${this.domid}`).fullCalendar(calendar_args);
    }


    ////////////////////////////////////////
    saveSomeColors () {
	$.cookie.json = true;
	let local_colors = ["#F3537D", "#5EAE10", "#481A88", "#2B15CC", "#8E34FA",
			    "#A41987", "#1B5DF8", "#7AAD82", "#8D72E4", "#323C89"];
	let some_colors = $.cookie("some-colors-data");
	
	if (! some_colors){
	    some_colors = 0
	}
	if (local_colors.length >= this.my_slices_name.length) {
	    $.cookie("some-colors-data", local_colors)
	} else if (some_colors.length >= this.my_slices_name.length) {
	    ;
	} else {
	    let lack_colors = this.my_slices_name.length - local_colors.length;
	    $.each(this.range(0, lack_colors), function(key, obj){
		local_colors.push(this.getRandomColor());
	    });
	    $.cookie("some-colors-data", local_colors)
	}
    }


    getLastSlice(){
	$.cookie.json = true;
	let last_slice = $.cookie("last-slice-data")
	
	if ($.inArray(last_slice, this.getMySlicesName()) > -1){
	    this.setCurrentSliceName(last_slice);
	    $.cookie("last-slice-data", last_slice)
	} else {
	    $.cookie("last-slice-data", liveleases.getCurrentSliceName())
	}
    }


    ////////////////////////////////////////
    main(){
	
	this.saveSomeColors();
	this.getLastSlice();
	
	this.resetActionsQueued();
	this.buildInitialSlicesBox(this.getMySlicesName());
	this.buildCalendar([]);
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
    }



    setSlice(element){
	let element_color = element.css("background-color");
	let element_name  = $.trim(element.text());
	this.setCurrentSliceBox(element_name)
	this.setCurrentSliceColor(element_color);
	this.setCurrentSliceName(element_name);
	this.setLastSlice();
    }


    setCurrentSliceBox(element){
	let id = this.idFormat(element);
	$(".noactive").removeClass('slice-active');
	$("#"+id).addClass('slice-active');
    }


    setCurrentSliceColor(color){
	this.current_slice_color = color;
	return true;
    }


    setCurrentSliceName(name){
	this.current_slice_name = name;
	return true;
    }


    setLastSlice(){
	$.cookie("last-slice-data", this.getCurrentSliceName())
    }


    idFormat(id){
	return id.replace(/\./g, '');
    }


    getCurrentSliceName(){
	return this.shortName(this.current_slice_name);
    }


    getCurrentSliceColor(){
	return this.current_slice_color;
    }


    shortName(name){
	let new_name = name;
	new_name = name.replace('onelab.', '');
	return new_name
    }


    getMySlicesName(){
	return this.my_slices_name;
    }


    getMySlicesinShortName(){
	let liveleases = this;
	let new_short_names = [];
	$.each(this.getMySlicesName(), function(key, val){
	    new_short_names.push(liveleases.shortName(val));
	});
	return new_short_names;
    }


    getMySlicesColor(){
	return my_slices_color;
    }


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


    getRandomColor() {
	let reserved_colors = ["#A1A1A1", "#D0D0D0", "#FF0000",
			       "#000000", "#FFE5E5", "#616161"];
	let letters = '0123456789ABCDEF'.split('');
	let color = '#';
	for (let i = 0; i < 6; i++ ) {
	    color += letters[Math.round(Math.random() * 15)];
	}
	if ($.inArray(color.toUpperCase(), reserved_colors) > -1){
	    return this.getRandomColor();
	}
	return color;
    }


    removeElementFromCalendar(id){
	$(`#${this.domid}`).fullCalendar('removeEvents', id );
    }


    getLocalId(title, start, end){
	let id = null;
	let m_start = moment(start)._d.toISOString();
	let m_end   = moment(end)._d.toISOString();
	String.prototype.hash = function() {
	    let self = this;
	    let range = Array(this.length);
	    for(let i = 0; i < this.length; i++) {
		range[i] = i;
	    }
	    return Array.prototype.map.call(range, function(i) {
		return self.charCodeAt(i).toString(16);
	    }).join('');
	}
	id = (title+m_start+m_end).hash();
	liveleases_debug(`title = ${title} -> ${id}`);
	return id;
    }


    getActionsQueue(){
	return this.actionsQueue;
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
	    if(title.indexOf('nightly routine') > -1){
		nightly = true;
	    }
	}
	return nightly;
    }


    getNightlyColor(){
	return this.nightly_slice_color;
    }


    isFailed(title){
	let failed = true;
	if(title.indexOf('* failed *') == -1){
	    failed = false;
	}
	return failed;
    }


    addElementToCalendar(element){
	$(`#${this.domid}`).fullCalendar('renderEvent', element, true );
    }


    resetActionsQueued(){
	this.actionsQueued = [];
    }


    queueAction(title, start, end) {
	let local_id = null;
	local_id = this.getLocalId(title, start, end);
	this.actionsQueued.push(local_id);
    }


    setCurrentLeases(leases){
	this.current_leases = leases;
    }


    getCurrentLeases(){
	return this.current_leases;
    }


    createLease(lease){
	let newLease             = new Object();
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
	//round to not wait
	start = moment(start).floor(10, 'minutes');
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
	this.socket.on('info:leases', function(msg){
	    liveleases.setCurrentLeases(msg);
	    liveleases.resetActionsQueued();
	    let leases = liveleases.getCurrentLeases();
	    let leasesbooked = liveleases.parseLeases(leases);
	    liveleases_debug(`incoming on info:leases ${leasesbooked.length} leases`, msg);
	    liveleases.refreshCalendar(leasesbooked);
	    liveleases.setCurrentSliceBox(liveleases.getCurrentSliceName());
	});
    }


    updateLeases(action, event){
	if (action == 'addLease') {
	    this.showImmediate('add', event);
	    this.setActionsQueue('add', event);
	} else if (action == 'editLease'){
	    this.showImmediate('edit', event);
	    this.setActionsQueue('edit', event);
	} else if (action == 'delLease') {
	    if(    ($.inArray(event.id, this.getActionsQueue()) == -1)
		&& (event.title.indexOf('* failed *') > -1) ){
		this.removeElementFromCalendar(event.id);
	    } else {
		this.setActionsQueue('del', event);
		this.showImmediate('del', event);
	    }
	}
    }


    setActionsQueue(action, data){
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
	    this.actionsQueue.push(data.id);
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
	    liveleases.delActionQueue(data.id);
	} else {
	    console.log('Something went wrong in map actions.');
	    return false;
	}
	// xxx replace this with some more sensible code for showing errors
	let display_error_message = alert;
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
			if (obj['error']) {
			    if (obj['error']['exception']) {
				if (obj['error']['exception']['reason']) {
				    liveleases.sendMessage(obj['error']['exception']['reason']);
				} else {
				    liveleases.sendMessage(obj['error']['exception']);
				}
			    } else {
				liveleases.sendMessage(obj['error']);
			    }
			} else {
			    ;//sendMessage(obj);
			}
		    } catch(err) {
			liveleases.sendMessage(`unexpected error while anayzing django answer ${err}`);
		    }
		}
	    }
	});
    }


    setColorLeases() {
	let liveleases = this;
	let some_colors = $.cookie("some-colors-data")
	$.each(liveleases.my_slices_name, function(key, obj){
	    liveleases.my_slices_color[key] = some_colors[key];
	});
	return this.my_slices_color;
    }


    range(start, end) {
	return Array(end-start).join(0).split(0).map(function(val, id) {return id+start});
    }


    getColorLease(slice_title){
	let lease_color = '#A1A1A1';
	if ($.inArray(slice_title, this.getMySlicesName()) > -1){
	    lease_color = this.my_slices_color[this.my_slices_name.indexOf(slice_title)];
	}
	return lease_color;
    }


    delActionQueue(id){
	let idx = this.actionsQueue.indexOf(id);
	this.actionsQueue.splice(idx, 1);
    }


    resetActionQueue(){
	this.actionsQueue = [];
    }


    isMySlice(slice){
	let is_my = false;
	if ($.inArray(this.resetName(slice), this.getMySlicesName()) > -1) {
	    is_my = true;
	}
	return is_my;
    }


    isPresent(element, list){
	let present = false;

	if ($.inArray(element, list) > -1){
	    present = true;
	}
	return present;
    }


    buildSlicesBox(leases) {
	let liveleases = this;
	// let known_slices = getMySlicesinShortName();
	liveleases_debug('buildSlicesBox');
	let slices = $("#my-slices");

	$.each(leases, function(key, val){
	    if ($.inArray(val.title, liveleases.known_slices) === -1) { //already present?
		if (liveleases.isMySlice(val.title)) {
		    if (val.title === liveleases.nightly_slice_name){
			color = liveleases.getNightlyColor();
			liveleases.setCurrentSliceColor(color);
		    } else if(val.title === liveleases.getCurrentSliceName()){
			liveleases.setCurrentSliceColor(val.color);
		    }
		    slices
			.append(
			    $("<div/>")
				.addClass('fc-event')
				.attr("style", `background-color: ${val.color}`)
				.text(val.title))
			.append(
			    $("<div/>")
				.attr("id", liveleases.idFormat(val.title))
				.addClass('noactive'));
		}
		liveleases.known_slices.push(val.title);
	    }
	});

	$('#my-slices .fc-event').each(function() {
	    $(this).draggable({
		zIndex: 999,
		revert: true,
		revertDuration: 0
	    });
	});
    }


    buildInitialSlicesBox(leases){
	let liveleases = this;
	liveleases_debug('buildInitialSlicesBox');
	liveleases.setColorLeases();
	let slices = $("#my-slices");
	let legend = "Double click in slice to select default";
	slices.html(`<h4 align="center" data-toggle="tooltip" title="${legend}">drag & drop to book</h4>`);

	$.each(leases, function(key, val){
	    val = liveleases.shortName(val);
	    let color = liveleases.getColorLease(val);
	    if ($.inArray(val, liveleases.known_slices) === -1) {
		//removing nightly routine and slices already present?
		if (liveleases.isMySlice(val)) {
		    if (val === liveleases.nightly_slice_name){
			color = liveleases.getNightlyColor();
			liveleases.setCurrentSliceColor(color);
		    }
		    else if(val === liveleases.getCurrentSliceName()){
			liveleases.setCurrentSliceColor(color);
		    }
		    slices
			.append(
			    $("<div />")
				.addClass('fc-event')
				.attr("style", `background-color: ${color}`)
				.text(val))
			.append(
			    $("<div />")
				.attr("id", liveleases.idFormat(val))
				.addClass('noactive'));
		}
		liveleases.known_slices.push(val);
	    }
	});

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
	if (this.refresh){
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
		    } else if (!liveleases.isPresent(obj.id, liveleases.actionsQueued) &&
			       !liveleases.isPending(obj.title) && !liveleases.isRemoving(obj.title) ){
			liveleases.removeElementFromCalendar(obj.id);
		    } else if (
			/*isPresent(obj.id, liveleases.actionsQueue) &&*/
			liveleases.isPending(obj.title) && !obj.uuid ){
			liveleases.removeElementFromCalendar(obj.id);
		    }
		}
	    });

	    liveleases.resetActionQueue();
	}
    }


    parseLeases(data){
	let liveleases = this;
	let parsedData = JSON.parse(data);
	let leases = [];

	liveleases_debug("parseLeases", data);
	
	parsedData.forEach(function(lease){
	    let newLease = new Object();
	    newLease.title = liveleases.shortName(lease.slicename);
	    newLease.uuid = String(lease.uuid);
	    newLease.start = lease.valid_from;
	    newLease.end = lease.valid_until;
	    newLease.id = liveleases.getLocalId(newLease.title, newLease.start, newLease.end);
	    newLease.color = liveleases.getColorLease(newLease.title);
	    if (liveleases.isMySlice(newLease.title) && !liveleases.isPastDate(newLease.end)) {
		newLease.editable = true;
	    } else {
		newLease.editable = false;
	    }
	    newLease.overlap = false;

	    // //HARD CODE TO SET SPECIAL ATTR to nightly routine
	    if (newLease.title == liveleases.nightly_slice_name){
		newLease.color = liveleases.getNightlyColor();
	    }

	    leases.push(newLease);
	    liveleases.queueAction(newLease.title, newLease.start, newLease.end);

	});

	this.buildSlicesBox(leases);
	return leases;
    }
}


//global - mostly for debugging and convenience
let the_liveleases;

// xxx need options to select mode instead
$(function() {
    the_liveleases = new LiveLeases('book', 'liveleases_container');
    the_liveleases.main();
})

