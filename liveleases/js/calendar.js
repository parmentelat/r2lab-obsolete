$(document).ready(function() {



  function buildCalendar(events) {

    var socket  = io();
    var today   = moment().format("YYYY-MM-DD");
    var path_to_leases_complete = events;
    var date = new Date();

    $('#external-events .fc-event').each(function() {
      // store data so the calendar knows to render an event upon drop
      var color = $(this).css("background-color");

      $(this).data('event', {
        title: $.trim($(this).text()), // use the element's text as the event title
        stick: true, // maintain when user navigates (see docs on the renderEvent method)
        color: color,
        overlap: false,
        selectable: true,
        editable: true,
      });

      // make the event draggable using jQuery UI
      $(this).draggable({
        zIndex: 999,
        revert: true,      // will cause the event to go back to its
        revertDuration: 0  //  original position after the drag
      });
    });

    //Create the calendar
    $('#calendar').fullCalendar({
      header: {
        left: 'prev,next today',
        center: 'title',
        right: 'agendaDay,agendaThreeDay,agendaWeek',
      },

      views: {
        agendaThreeDay: {
          type: 'agenda',
          duration: { days: 3 },
          buttonText: '3 days'
        }
      },
      defaultTimedEventDuration: '00:30:00',
      defaultView: 'agendaThreeDay',
      timezone: 'Europe/Paris',
      defaultDate: today,
      selectable: true,
      selectHelper: false,
      overlap: false,
      editable: true,
      allDaySlot: false,
      droppable: true,

      //Events
      select: function(start, end, jsEvent, view) {
        //Avoid past dates when try to book a lease
        if (moment().diff(start, 'days') > 0) {
          $('#calendar').fullCalendar('unselect');
          $('#messages').fadeOut(200).fadeIn(200).fadeOut(200).fadeIn(200);
          $('#messages').delay(2000).fadeOut();
          return false;
        }
        var my_title = getLeaseName();
        var eventData;
        if (my_title) {
          eventData = {
            title: my_title,
            start: start,
            end: end,
            // end: start+ ((3600*1000)*0.5),
            overlap: false,
            editable: true,
            allDaySlot: false,
            color: 'green',
          };

          //receive the event information when click
          socket.emit('addlease', eventData);
        }
        $('#calendar').fullCalendar('unselect');
      },
      // this allows things to be dropped onto the calendar
      drop: function(date) {

			},
      //Remove leases with double click
      eventRender: function(event, element) {
        element.bind('dblclick', function() {

          if (event.title == getLeaseName()) {
            socket.emit('dellease', event._id);
          }
        });
      },
      //Events from Json file
      events: path_to_leases_complete,
    });
  }


  function getLeaseName(){
    return 'my lease name';
  }


  function parseLease(url){
    var all_leases_for_calendar;
    $.ajax({
      url: url,
      async: false,
      success: function(data) {
        var leases = [];
        var title, start, end, color;
        loadSlices(data, '');
        $.each(data, function(key,val){
          $.each(val.resource_response.resources, function(k,v){
            title = v.account.name;
            start = v.valid_from;
            end   = v.valid_until;
            if (v.resource_type === 'lease') {
              color = '#257e4a';
            }

            newLease = new Object();
            newLease.title = title;
            newLease.start = start;
            newLease.end   = end;
            newLease.color = color;
            newLease.editable = false;
            newLease.overlap = false;
            leases.push(newLease);

          });

          //Nightly routine fixed in each nigth from 3AM to 5PM
          newLease = new Object();
          newLease.title = "nightly routine";
          newLease.start = " T03:00:00Z";
          newLease.end   = " T05:00:00Z";
          newLease.color = "#616161";
          newLease.overlap = false;
          newLease.editable = false;
          newLease.dow = [0,1,2,3,4,5,6,7,8];
          leases.push(newLease);

          //Past dates
          newLease = new Object();
          newLease.id = "pastDate";
          newLease.start = "2016-01-01T00:00:00Z";
          newLease.end   = "2016-01-28T00:00:00Z";
          newLease.overlap = false;
          newLease.editable = false;
          newLease.rendering = "background",
          newLease.color = "#ffe5e5";
          leases.push(newLease);

        });

        all_leases_for_calendar = leases;
      }
    });
    return all_leases_for_calendar;
  }


  function updateLeases(){
    var socket = io();

    socket.on('addlease', function(msg){
      $('#calendar').fullCalendar('renderEvent', msg, true );
    });

    socket.on('dellease', function(msg){
      $('#calendar').fullCalendar('removeEvents',msg);
    });
  }


  function loadSlices(data, user) {
    var options = $("#slices");
    $.each(data, function(key,val){
      $.each(val.resource_response.resources, function(k,v){
        options.append($("<option />").val(v.account.name).text(v.account.name));
      });
    });
  }


  function main () {
    var events = parseLease('/leasesbooked')

    buildCalendar(events);
    updateLeases();
  }



  main();

});
