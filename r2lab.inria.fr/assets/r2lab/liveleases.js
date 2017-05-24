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
    }


    buildCalendar(initial_events_json) {
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
	    timezone: currentTimezone,
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
		if (isPastDate(end)) {
		    $(`#${xxxdomid}`).fullCalendar('unselect');
		    sendMessage('This timeslot is in the past!');
		    return false;
		}
		let my_title = getCurrentSliceName();
		let eventData;
		[start, end] = adaptStartEnd(start, end);
		
		if (my_title) {
		    eventData = {
			title: pendingName(my_title),
			start: start,
			end: end,
			overlap: false,
			editable: false,
			selectable: false,
			color: getCurrentSliceColor(),
			textColor: color_pending,
			id: getLocalId(my_title, start, end),
		    };
		    updateLeases('addLease', eventData);
		}
		$(`#${xxxdomid}`).fullCalendar('unselect');
	    },

	    // this allows things to be dropped onto the calendar
	    drop: function(date, event, view) {
		let start = date;
		let end   = moment(date).add(60, 'minutes');
		if (isPastDate(end)) {
		    $(`#${xxxdomid}`).fullCalendar('unselect');
		    sendMessage('This timeslot is in the past!');
		    return false;
		}

		setSlice($(this))
		[start, end] = adaptStartEnd(start, end);

		let my_title = getCurrentSliceName();
		let eventData;
		if (my_title) {
		    eventData = {
			title: pendingName(my_title),
			start: start,
			end: end,
			overlap: false,
			editable: false,
			selectable: false,
			color: getCurrentSliceColor(),
			textColor: color_pending,
			id: getLocalId(my_title, start, end),
		    };
		    updateLeases('addLease', eventData);
		}
	    },

	    // this happens when the event is dragged moved and dropped
	    eventDrop: function(event, delta, revertFunc) {
		let view = $(`#${xxxdomid}`).fullCalendar('getView').type;
		if(view != 'month'){
		    if (!confirm("Confirm this change ?")) {
			revertFunc();
		    } else if (isPastDate(event.end)) {
			revertFunc();
			sendMessage('This timeslot is in the past!');
		    } else {
			let newLease = createLease(event);
			newLease.title = pendingName(event.title);
			newLease.editable = false;
			newLease.textColor = color_pending;
			removeElementFromCalendar(newLease.id);
			updateLeases('editLease', newLease);
		    }
		} else {
		    revertFunc();
		}
	    },

	    // this fires when one event starts to be dragged
	    eventDragStart: function(event, jsEvent, ui, view) {
		keepOldEvent = event;
		refresh = false;
	    },

	    // this fires when one event starts to be dragged
	    eventDragStop: function(event, jsEvent, ui, view) {
		keepOldEvent = event;
		refresh = true;
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
		
		let view = $(`#${xxxdomid}`).fullCalendar('getView').type;
		if(view != 'month'){
		    element.bind('dblclick', function() {
			if (isMySlice(event.title) && event.editable == true ) {
			    if (!confirm("Confirm removing?")) {
				revertFunc();
			    }
			    let newLease = createLease(event);
			    let now = new Date();
			    let started = moment(now).diff(moment(event.start), 'minutes');
			    if(started >= 10){
				newLease.start = moment(event.start);
				newLease.end = moment(event.start).add(started, 'minutes');
				newLease.title = removingName(event.title);
				newLease.textColor = color_removing;
				newLease.editable = false;
				newLease.selectable = false;
				newLease.id = getLocalId(event.title+'new', newLease.start, newLease.end),
				removeElementFromCalendar(newLease.id);
				updateLeases('editLease', newLease);
			    } else {
				removeElementFromCalendar(event.id);
				addElementToCalendar(newLease);
				updateLeases('delLease', newLease);
			    }
			}
			if (isMySlice(event.title) && isPending(event.title)) {
			    if (confirm("This event is not confirmed yet. Are you sure to remove?")) {
				let newLease = createLease(event);
				newLease.title = removingName(event.title);
				newLease.textColor = color_removing;
				newLease.editable = false;
				removeElementFromCalendar(event.id);
				addElementToCalendar(newLease);
				updateLeases('delLease', newLease);
			    }
			}
			if (isMySlice(event.title) && isFailed(event.title)) {
			    removeElementFromCalendar(event.id);
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
		} else {
		    if (isMySlice(event.title)) {
			let newLease = createLease(event);
			newLease.title = pendingName(event.title);
			newLease.textColor = color_pending;
			newLease.editable = false;
			removeElementFromCalendar(newLease.id);
			updateLeases('editLease', newLease);
		    }
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
	if (local_colors.length >= my_slices_name.length) {
	    $.cookie("some-colors-data", local_colors)
	} else {
	    if (some_colors.length >= my_slices_name.length) {
		;
	    } else {
		let lack_colors = my_slices_name.length - local_colors.length;
		$.each(range(0,lack_colors), function(key,obj){
		    local_colors.push(getRandomColor());
		});
		$.cookie("some-colors-data", local_colors)
	    }
	}
    }


    getLastSlice(){
	$.cookie.json = true;
	let last_slice = $.cookie("last-slice-data")
	
	if ($.inArray(fullName(last_slice), getMySlicesName()) > -1){
	    setCurrentSliceName(last_slice);
	    $.cookie("last-slice-data", last_slice)
	} else {
	    $.cookie("last-slice-data", getCurrentSliceName())
	}
    }


    ////////////////////////////////////////
    main(){
	
	this.saveSomeColors();
	this.getLastSlice();
	
	resetActionsQueued();
	buildInitialSlicesBox(getMySlicesName());
	this.buildCalendar([]);
	setCurrentSliceBox(getCurrentSliceName());
	
	listenLeases();
	refreshLeases();
	
	let run_mode = liveleases_options.mode == 'run';
	if (run_mode) {
	    // don't do this in book mode, it would change all days
	    $('.fc-day-header').html('today');
	}
	
	let slice = $('#my-slices .fc-event');
	slice.dblclick(function() {
	    setSlice($(this));
	});
	
	$('body').on('click', 'button.fc-month-button', function() {
	    sendMessage('This view is read only!', 'info');
	});
    }
}

//global - mostly for debugging and convenience
let the_liveleases;

// xxx need options to select mode instead
$(function() {
    the_liveleases = new LiveLeases('book', 'liveleases_container');
    the_liveleases.main();
})

////////////////////////////////////////
// previously in liveleases-common.js
// needs to be redesigned into a proper class
// also needs some cleanup in the actionsQueue/actionsQueued area

let my_slices_name      = r2lab_accounts.map((account) => account.name); // a list of slice hrns

let my_slices_color     = [];
let actionsQueue        = [];
let actionsQueued       = [];
let current_slice_name  = current_slice.name;
let current_slice_color = '#DDD';
let current_leases      = null;
let color_pending       = '#FFFFFF';
let color_removing      = '#FFFFFF';
let keepOldEvent        = null;
let theZombieLeases     = [];

let socket              = io.connect(sidecar_url);
let refresh             = true;
let currentTimezone     = 'local';
let nigthly_slice_name  = 'inria_r2lab.nightly'
let nigthly_slice_color = '#000000';

let xxxdomid = 'liveleases_container';

function setSlice(element){
    let element_color = element.css("background-color");
    let element_name  = $.trim(element.text());
    setCurrentSliceBox(element_name)
    setCurrentSliceColor(element_color);
    setCurrentSliceName(element_name);
    setLastSlice();
}


function setCurrentSliceBox(element){
    let id = idFormat(element);
    $(".noactive").removeClass('slice-active');
    $("#"+id).addClass('slice-active');
}


function setCurrentSliceColor(color){
    current_slice_color = color;
    return true;
}


function setCurrentSliceName(name){
    current_slice_name = name;
    return true;
}


function setLastSlice(){
    $.cookie("last-slice-data", getCurrentSliceName())
}


function idFormat(id){
    let new_id = id.replace(/\./g, '');
    return new_id;
}


function getCurrentSliceName(){
    return shortName(current_slice_name);
}


function getCurrentSliceColor(){
    return current_slice_color;
}


function shortName(name){
    let new_name = name;
    new_name = name.replace('onelab.', '');
    return new_name
}


function getMySlicesName(){
    return my_slices_name;
}


function getMySlicesinShortName(){
    let new_short_names = [];
    $.each(getMySlicesName(), function(key,val){
	new_short_names.push(shortName(val));
    });
    return new_short_names;
}


function getMySlicesColor(){
    return my_slices_color;
}


function pendingName(name){
    let new_name = name;
    new_name = resetName(name) + ' (pending)';
    return new_name
}


function removingName(name){
    let new_name = name;
    new_name = resetName(name) + ' (removing)';
    return new_name
}


function resetName(name){
    let new_name = name;
    new_name = name.replace(' (pending)', '');
    new_name = new_name.replace(' (removing)', '');
    new_name = new_name.replace(' * failed *', '');
    return new_name
}


function failedName(name){
    let new_name = name;
    new_name = resetName(name) + ' * failed *';
    return new_name
}


function getRandomColor() {
    let reserved_colors = ["#A1A1A1", "#D0D0D0", "#FF0000", "#000000", "#FFE5E5", "#616161"];
    let letters = '0123456789ABCDEF'.split('');
    let color = '#';
    for (let i = 0; i < 6; i++ ) {
	color += letters[Math.round(Math.random() * 15)];
    }
    if ($.inArray(color.toUpperCase(), reserved_colors) > -1){
	getRandomColor();
    }
    return color;
}


// no extra 'onelab.' anymore
function fullName(name){
    return name;
}


function failedLease(lease){
    let newLease = new Object();
    newLease.title = failedName(lease.title);
    newLease.id = lease.id;
    newLease.start = lease.start;
    newLease.end   = lease.end;
    newLease.color = "#FF0000";
    newLease.overlap = false;
    newLease.editable = false;
    return newLease;
}


function zombieLease(lease){
    newLease = new Object();
    newLease.title = failedName(lease.title);
    newLease.id = lease.uuid;
    newLease.start = lease.start;
    newLease.end   = lease.end;
    newLease.color = "#FF0000";``
    newLease.overlap = false;
    newLease.editable = false;
    return newLease;
}


function removeElementFromCalendar(id){
    $(`#${xxxdomid}`).fullCalendar('removeEvents', id );
}


function diffArrays(first, second){
    let diff_array = null;
    diff_array = $(first).not(second).get()
    return diff_array;
}


function getLocalId(title, start, end){
    let id = null;
    let m_start = moment(start)._d.toISOString();
    let m_end   = moment(end)._d.toISOString();
    String.prototype.hash = function() {
	let self = this, range = Array(this.length);
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


function getActionsQueue(){
    return actionsQueue;
}


function isRemoving(title){
    let removing = true;
    if(title.indexOf('(removing)') == -1){
	removing = false;
    }
    return removing;
}


function isPending(title){
    let pending = true;
    if(title.indexOf('(pending)') == -1){
	pending = false;
    }
    return pending;
}


function isNightly(title){
    let nightly = false;
    if (title) {
	if(title.indexOf('nightly routine') > -1){
	    nightly = true;
	}
    }
    return nightly;
}


function getNightlyColor(){
    return nigthly_slice_color;
}


function isFailed(title){
    let failed = true;
    if(title.indexOf('* failed *') == -1){
	failed = false;
    }
    return failed;
}


function addElementToCalendar(element){
    $(`#${xxxdomid}`).fullCalendar('renderEvent', element, true );
}


function resetActionsQueued(){
    actionsQueued = [];
}


function getActionsQueued(){
    return actionsQueued;
}


function queueAction(title, start, end) {
    let local_id = null;
    local_id = getLocalId(title, start, end);
    actionsQueued.push(local_id);
}


function setCurrentLeases(leases){
    current_leases = leases;
}


function getCurrentLeases(){
    return current_leases;
}


function createLease(lease){
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


function isPastDate(end){
    let past = false;
    if(moment().diff(end, 'minutes') > 0){
	past = true;
    }
    return past;
}


function adaptStartEnd(start, end) {
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


function isR2lab(name){
    let r2lab = false;
    if (name.substring(0, 13) == 'inria_'){
	r2lab = true;
    }
    return r2lab;
}


function sendMessage(msg, type){
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


// xxx plcapi : do we still have zombies ?
function isZombie(obj){
    return false;

    let is_zombie = false;
    if(obj.resource_type == 'lease' && obj.status == 'pending' && isMySlice(shortName(obj.slicename))){
	is_zombie = true;
    }
    return is_zombie;
}


// use this to ask for an immediate refresh
// of the set of leases
// of course it must be called *after* the actual API call
// via django
function refreshLeases(){
    let msg = "INIT";
    liveleases_debug("sending on request:leases -> ", msg);
    socket.emit('request:leases', msg);
}

// show action immediately before it becomes confirmed
function showImmediate(action, event) {
    liveleases_debug("showImmediate", action);
    if (action == 'add'){
	let lease  = createLease(event);
	$(`#${xxxdomid}`).fullCalendar('renderEvent', lease, true );
    } else if (action == 'edit'){
	let lease  = createLease(event);
	removeElementFromCalendar(lease.id);
	$(`#${xxxdomid}`).fullCalendar('renderEvent', lease, true );
    } else if (action == 'del'){
	let lease  = createLease(event);
	removeElementFromCalendar(lease.id);
	$(`#${xxxdomid}`).fullCalendar('renderEvent', lease, true );
    }
}

function listenLeases(){
    socket.on('info:leases', function(msg){
	setCurrentLeases(msg);
	resetActionsQueued();
	let leases = getCurrentLeases();
	let leasesbooked = parseLeases(leases);
	liveleases_debug(`incoming on info:leases ${leasesbooked.length} leases`, msg);
	refreshCalendar(leasesbooked);
	setCurrentSliceBox(getCurrentSliceName());
    });
}


function updateLeases(action, event){
    if (action == 'addLease') {
	showImmediate('add', event);
	setActionsQueue('add', event);
    } else if (action == 'editLease'){
	showImmediate('edit', event);
	setActionsQueue('edit', event);
    } else if (action == 'delLease') {
	if( ($.inArray(event.id, getActionsQueue()) == -1) && (event.title.indexOf('* failed *') > -1) ){
	    removeElementFromCalendar(event.id);
	} else {
	    setActionsQueue('del', event);
	    showImmediate('del', event);
	}
    }
}


function setActionsQueue(action, data){
    let verb = null;
    let request = null;

    if (action == 'add'){
	verb = 'add';
	request = {
	    "slicename"  : fullName(resetName(data.title)),
	    "valid_from" : data.start._d.toISOString(),
	    "valid_until": data.end._d.toISOString()
	};
	actionsQueue.push(data.id);
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
	delActionQueue(data.id);
    } else {
	console.log('Something went wrong in map actions.');
	return false;
    }
    // xxx replace this with some more sensible code for showing errors
    let display_error_message = alert;
    post_xhttp_django(`/leases/${verb}`, request, function(xhttp) {
	if (xhttp.readyState == 4) {
	    // this triggers a refresh of the leases once the sidecar server answers back
	    refreshLeases();
	    ////////// temporary
	    // in all cases, show the results in console, in case we'd need to improve this
	    // logic further on in the future
	    liveleases_debug(`upon ajax POST: xhttp.status = ${xhttp.status}`);
	    ////////// what should remain
	    if (xhttp.status != 200) {
		// this typically is a 500 error inside django
		// hard to know what to expect..
		sendMessage(`Something went wrong when managing leases with code ${xhttp.status}`);
	    } else {
		// the http POST has been successful, but a lot can happen still
		// for starters, are we getting a JSON string ?
		try {
		    let obj = JSON.parse(xhttp.responseText);
		    if (obj['error']) {
			if (obj['error']['exception']) {
			    if (obj['error']['exception']['reason']) {
				sendMessage(obj['error']['exception']['reason']);
			    } else {
				sendMessage(obj['error']['exception']);
			    }
			} else {
			    sendMessage(obj['error']);
			}
		    } else {
			;//sendMessage(obj);
		    }
		} catch(err) {
		    sendMessage(`unexpected error while anayzing django answer ${err}`);
		}
	    }
	}
    });
}


function setColorLeases(){
    let some_colors = $.cookie("some-colors-data")
    $.each(my_slices_name, function(key,obj){
	my_slices_color[key] = some_colors[key];
    });
    return my_slices_color;
}


function range(start, end) {
    return Array(end-start).join(0).split(0).map(function(val, id) {return id+start});
}


function getColorLease(slice_title){
    let lease_color = '#A1A1A1';
    if ($.inArray(fullName(slice_title), getMySlicesName()) > -1){
	lease_color = my_slices_color[my_slices_name.indexOf(fullName(slice_title))];
    }
    return lease_color;
}


function delActionQueue(id){
    let idx = actionsQueue.indexOf(id);
    actionsQueue.splice(idx,1);
}


function resetZombieLeases(){
    theZombieLeases = [];
}


function resetActionQueue(){
    actionsQueue = [];
}


function resetCalendar(){
    $(`#${xxxdomid}`).fullCalendar('removeEvents');
}


function isMySlice(slice){
    let is_my = false;
    if ($.inArray(fullName(resetName(slice)), getMySlicesName()) > -1){
	is_my = true;
    }
    return is_my;
}


function isPresent(element, list){
    let present = false;

    if ($.inArray(element, list) > -1){
	present = true;
    }
    return present;
}


function buildSlicesBox(leases) {
    // let known_slices = getMySlicesinShortName();
    liveleases_debug('buildSlicesBox');
    let slices = $("#my-slices");

    $.each(leases, function(key, val){
	if ($.inArray(val.title, known_slices) === -1) { //already present?
	    if (isMySlice(val.title)) {
		if (val.title === nigthly_slice_name){
		    color = getNightlyColor();
		    setCurrentSliceColor(color);
		} else if(val.title === getCurrentSliceName()){
		    setCurrentSliceColor(val.color);
		}
		slices
		    .append(
			$("<div/>")
			    .addClass('fc-event')
			    .attr("style", `background-color: ${val.color}`)
			    .text(val.title))
		    .append(
			$("<div/>")
			    .attr("id", idFormat(val.title))
			    .addClass('noactive'));
	    }
	    known_slices.push(val.title);
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


let known_slices = [];
function buildInitialSlicesBox(leases){
    liveleases_debug('buildInitialSlicesBox');
    setColorLeases();
    let slices = $("#my-slices");
    let legend = "Double click in slice to select default";
    slices.html(`<h4 align="center" data-toggle="tooltip" title="${legend}">drag & drop to book</h4>`);

    $.each(leases, function(key, val){
	val = shortName(val);
	let color = getColorLease(val);
	if ($.inArray(val, known_slices) === -1) { //removing nightly routine and slices already present?
	    if (isMySlice(val)) {
		if (val === nigthly_slice_name){
		    color = getNightlyColor();
		    setCurrentSliceColor(color);
		}
		else if(val === getCurrentSliceName()){
		    setCurrentSliceColor(color);
		}
		slices
		    .append(
			$("<div />")
			    .addClass('fc-event')
			    .attr("style", `background-color: ${color}`)
			    .text(val))
		    .append(
			$("<div />")
			    .attr("id", idFormat(val))
			    .addClass('noactive'));
	    }
	    known_slices.push(val);
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


function refreshCalendar(events){
    // xxx ugly use of global
    if (refresh){
	$.each(events, function(key, event){
	    liveleases_debug(`refreshCalendar : lease = ${event.title}: ${event.start} .. ${event.end}`);
	    removeElementFromCalendar(event.id);
	    $(`#${xxxdomid}`).fullCalendar('renderEvent', event, true);
	});

	let each_removing = $(`#${xxxdomid}`).fullCalendar( 'clientEvents' );
	$.each(each_removing, function(k, obj){
	    // when click in month view all 'thousands' of nightly comes.
	    // Maybe reset when comeback from month view (not implemented)
	    if (!isNightly(obj.title) && obj.title) {
		if (isRemoving(obj.title)){
		    removeElementFromCalendar(obj.id);
		} else if (obj.uuid && isPending(obj.title)){
		    removeElementFromCalendar(obj.id);
		} else if (!isPresent(obj.id, actionsQueued) && !isPending(obj.title) && !isRemoving(obj.title) ){
		    removeElementFromCalendar(obj.id);
		} else if (/*isPresent(obj.id, actionsQueue) &&*/ isPending(obj.title) && !obj.uuid ){
		    removeElementFromCalendar(obj.id);
		}
	    }
	});

	let failedEvents = [];
	$.each(theZombieLeases, function(k, obj){
	    failedEvents.push(zombieLease(obj));
	});
	resetZombieLeases();
	$(`#${xxxdomid}`).fullCalendar('addEventSource', failedEvents);

	resetActionQueue();
    }
}


function parseLeases(data){
    let parsedData = JSON.parse(data);
    let leases = [];
    resetZombieLeases();

    liveleases_debug("parseLeases", data);
    
    parsedData.forEach(function(lease){
	let newLease = new Object();
	newLease.title = shortName(lease.slicename);
	newLease.uuid = String(lease.uuid);
	newLease.start = lease.valid_from;
	newLease.end = lease.valid_until;
	newLease.id = getLocalId(newLease.title, newLease.start, newLease.end);
	newLease.color = getColorLease(newLease.title);
	if (isMySlice(newLease.title) && !isPastDate(newLease.end)) {
	    newLease.editable = true;
	} else {
	    newLease.editable = false;
	}
	newLease.overlap = false;

	// //HARD CODE TO SET SPECIAL ATTR to nightly routine
	if (newLease.title == nigthly_slice_name){
	    newLease.color = getNightlyColor();
	}

	if (isZombie(lease)) {
	    theZombieLeases.push(newLease);
	    let request = {"uuid" : newLease.uuid};
	    post_xhttp_django('/leases/delete', request, function(xhttp) {
		if (xhttp.readyState == 4 && xhttp.status == 200) {
		    liveleases_debug("return from /leases/delete", request);
		}
	    });
	} else {
	    leases.push(newLease);
	    queueAction(newLease.title, newLease.start, newLease.end);
	}

    });

    buildSlicesBox(leases);
    return leases;
}
