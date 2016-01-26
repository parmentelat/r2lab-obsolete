$(document).ready(function() {

  var socket  = io();
  var today   = moment().format("YYYY-MM-DD");
  var path_to_slices_complete = "/slices_complete";

  //CREATIING THE CALENDAR
  $('#calendar').fullCalendar({
    header: {
      left: 'prev,next today',
      center: 'title',
      right: 'agendaWeek,agendaDay',
    },

    defaultView: 'agendaWeek',
    timezone: 'Europe/Paris',
    defaultDate: today,
    selectable: true,
    selectHelper: false,
    overlap: false,
    editable: false,
    allDaySlot: false,

    //EVENTS
    select: function(start, end, jsEvent, view) {

      //AVOID PAST DATES WHEN TRY A SLICE
      if (moment().diff(start, 'days') > 0) {
        $('#calendar').fullCalendar('unselect');
        $('#messages').fadeOut(200).fadeIn(200).fadeOut(200).fadeIn(200);
        $('#messages').delay(2000).fadeOut();
        return false;
      }
      var my_title = 'my slice';
      var eventData;
      if (my_title) {
        eventData = {
          title: my_title,
          start: start,
          end: end,
          //end: start+ ((3600*1000)*0.5),
          overlap: false,
          editable: true,
          allDaySlot: false,
        };

        //receive the event information when click
        socket.emit('add_slice', eventData);
      }
      $('#calendar').fullCalendar('unselect');
    },

    //REMOVE SLICE WITH SINGLE CLICK
    //eventClick: function(event){
      //$('#calendar').fullCalendar('removeEvents',event._id);
    //},

    //REMOVE SLICE WITH DOUBLE CLICK
    eventRender: function(event, element) {
      element.bind('dblclick', function() {

        if (event.title == 'my slice') {
          socket.emit('remove_slice_by_id', event._id);
        }
      });
    },

    //DEFINING THE EVENTS LOADIN FROM THE JSON FILE
    events: {
      url: path_to_slices_complete,
      error: function() {
        alert('Ops! Someting went wrong when load json file');
      }
    },
    loading: function(bool) {
      $('#loading').toggle(bool);
    }

  });
});
