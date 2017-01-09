// -*- js-indent-level:2 -*-
// this requires xhttp-django.js and liveleases-common.js

$(document).ready(function() {
  var version = '1.33';

  function buildCalendar(theEvents) {
    var today  = moment().format("YYYY-MM-DD");
    var showAt = moment().subtract(1, 'hour').format("HH:mm");

    //Create the calendar
    $('#calendar').fullCalendar({
      header: {
        left: 'prev,next today',
        center: 'title',
        right: 'agendaDay,agendaThreeDay,agendaWeek,month',
      },

      views: {
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
      defaultTimedEventDuration: '01:00:00',
      slotDuration: "01:00:00",
      forceEventDuration: true,
      defaultView: 'agendaThreeDay',
      timezone: currentTimezone,
      defaultDate: today,
      selectHelper: false,
      overlap: false,
      selectable: true,
      editable: true,
      allDaySlot: false,
      droppable: true,
      height: 515,
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
        var my_title = getCurrentSliceName();
        var eventData;

        if (my_title) {
          eventData = {
            title: pendingName(my_title),
            start: adaptStart(start),
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
        var start = date;
        var end   = moment(date).add(60, 'minutes');
        if (isPastDate(end)) {
          $('#calendar').fullCalendar('unselect');
          sendMessage('This timeslot is in the past!');
          return false;
        }

        setSlice($(this))

        var my_title = getCurrentSliceName();
        var eventData;
        if (my_title) {
          eventData = {
            title: pendingName(my_title),
            start: adaptStart(start),
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
        var view = $('#calendar').fullCalendar('getView').type;
        if(view != 'month'){
          if (!confirm("Confirm this change?")) {
              revertFunc();
          }
          else {
            if (isPastDate(event.end)) {
              revertFunc();
              sendMessage('This timeslot is in the past!');
            } else {
              newLease = createLease(event);
              newLease.title = pendingName(event.title);
              newLease.editable = false;
              newLease.textColor = color_pending;
              removeElementFromCalendar(newLease.id);
              updateLeases('editLease', newLease);
            }
          }
        }else {
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
        $(element).popover({content: event.title, placement: 'top', trigger: 'hover', delay: {"show": 1000 }});

        var view = $('#calendar').fullCalendar('getView').type;
        if(view != 'month'){
          element.bind('dblclick', function() {
            if (isMySlice(event.title) && event.editable == true ) {
              if (!confirm("Confirm removing?")) {
                  revertFunc();
              }
              newLease = createLease(event);
              newLease.title = removingName(event.title);
              newLease.textColor = color_removing;
              newLease.editable = false;
              removeElementFromCalendar(event.id);
              addElementToCalendar(newLease);
              updateLeases('delLease', newLease);
            }
            if (isMySlice(event.title) && isPending(event.title)) {
              if (confirm("This event is not confirmed yet. Are you sure to remove?")) {
                newLease = createLease(event);
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
        }
        else {
          if (isMySlice(event.title)) {
            newLease = createLease(event);
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
    });
  }


  function main (){
    console.log("liveleases book version " + version);
    saveSomeColors();
    getLastSlice();

    resetActionsQueue();
    buildInitialSlicesBox(getMySlicesName());
    buildCalendar(setNightlyAndPast());
    setCurrentSliceBox(getCurrentSliceName());

    listenLeases();
    refreshLeases();

    // $('.fc-day-header').html('today');

    var slice = $('#my-slices .fc-event');
    slice.dblclick(function() {
      setSlice($(this));
    });

    $('body').on('click', 'button.fc-month-button', function() {
      sendMessage('This view is read only!', 'info');
    });
  }


  main();
});
