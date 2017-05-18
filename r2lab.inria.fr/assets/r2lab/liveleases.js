// -*- js-indent-level:4 -*-
// this requires xhttp-django.js and liveleases-common.js
"use strict";

// create this object with mode='run' or mode='book'
// e.g. $(function() {let the_leases = new LiveLeases('run', 'container-leases'); the_leases.main(); })

let liveleases_options = {

    mode : 'run',

    // these properties in the fullCalendar object will
    // be traced when debug is set to true
    trace_events : [
	'select'
    ],
    debug : true,
}

function liveleases_debug(...args) {
    if (liveleases_options.debug)
	console.log(...args);
}


let LiveLeases = function(mode, domid) {
    this.mode = mode;
    this.domid = domid;
}

LiveLeases.prototype.buildCalendar = function(theEvents) {
    let today  = moment().format("YYYY-MM-DD");
    let showAt = moment().subtract(1, 'hour').format("HH:mm");
    let run_mode = liveleases_options.mode == 'run';
    
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
	defaultTimedEventDuration: '00:01:00',
	slotDuration: "01:00:00",
	forceEventDuration: true,
	defaultView: run_mode ? 'agendaDay' : 'agendaThreeDay',
	timezone: currentTimezone,
	defaultDate: today,
	selectHelper: false,
	overlap: false,
	selectable: true,
	editable: true,
	allDaySlot: false,
	droppable: true,
	height: run_mode ? 455 : 515 ,
	nowIndicator: true,
	scrollTime: showAt,
	//Events
	// this is fired when a selection is made
	select: function(start, end, event, view) {
	    if (isPastDate(end)) {
		$('#calendar').fullCalendar('unselect');
		sendMessage('This timeslot is in the past!');
		return false;
	    }
	    let my_title = getCurrentSliceName();
	    let eventData;
	    let adapt = adaptStartEnd(start, end);
	    start = adapt[0];
	    end   = adapt[1];

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
	    $('#calendar').fullCalendar('unselect');
	},

	// this allows things to be dropped onto the calendar
	drop: function(date, event, view) {
	    let start = date;
	    let end   = moment(date).add(60, 'minutes');
	    if (isPastDate(end)) {
		$('#calendar').fullCalendar('unselect');
		sendMessage('This timeslot is in the past!');
		return false;
	    }

	    setSlice($(this))
	    let adapt = adaptStartEnd(start, end);
	    start = adapt[0];
	    end   = adapt[1];

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
	    let view = $('#calendar').fullCalendar('getView').type;
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
	    $(element).popover({content: event.title, placement: 'top',
				trigger: 'hover', delay: {"show": 1000 }});
	    
	    let view = $('#calendar').fullCalendar('getView').type;
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

	// eventMouseover: function(event, jsEvent, view) {
	//   $(this).popover('show');
	// },
	//
	eventMouseout: function(event, jsEvent, view) {
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
	events: theEvents,
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
	calendar_args[prop] = trace_function(calendar_args[prop])
    }
    $(`#${this.domid}`).fullCalendar(calendar_args);
}


LiveLeases.prototype.main = function (){
    console.log('main');

    saveSomeColors();
    getLastSlice();

    resetActionsQueue();
    buildInitialSlicesBox(getMySlicesName());
    this.buildCalendar(setNightlyAndPast());
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

//global - mostly for debugging and convenience
let the_liveleases;

// xxx need options to select mode instead
$(function() {
    the_liveleases = new LiveLeases('book', 'liveleases_container');
    the_liveleases.main();
})
