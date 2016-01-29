$(document).ready(function() {

  function BuildCalendar() {

    var socket  = io();
    var today   = moment().format("YYYY-MM-DD");
    // var path_to_leases_complete = "/leases_complete";
    var path_to_leases_complete = parseLease('/leases_original');

    //Create the calendar
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
            //end: start+ ((3600*1000)*0.5),
            overlap: false,
            editable: true,
            allDaySlot: false,
          };

          //receive the event information when click
          socket.emit('add_lease', eventData);
        }
        $('#calendar').fullCalendar('unselect');
      },

      //Remove leases with single click
      //eventClick: function(event){
        //$('#calendar').fullCalendar('removeEvents',event._id);
      //},

      //Remove leases with double click
      eventRender: function(event, element) {
        element.bind('dblclick', function() {

          if (event.title == getLeaseName()) {
            socket.emit('remove_lease_by_id', event._id);
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
            leases.push(newLease);

          });

          //Nightly routine fixed in each nigth from 3AM to 5PM
          newLease = new Object();
          newLease.title = "nightly routine";
          newLease.start = " T03:00:00Z";
          newLease.end   = " T05:00:00Z";
          newLease.color = "#616161";
          newLease.overlap = false;
          newLease.dow = [0,1,2,3,4,5,6,7,8];
          leases.push(newLease);

          //Past dates
          newLease = new Object();
          newLease.id = "pastDate";
          newLease.start = "2016-01-01T00:00:00Z";
          newLease.end   = "2016-01-28T00:00:00Z";
          newLease.overlap = false;
          newLease.rendering = "background",
          newLease.color = "#ffe5e5";
          leases.push(newLease);

        });

        all_leases_for_calendar = leases;
      }
    });
    return all_leases_for_calendar;
  }

  function main () {
    BuildCalendar();
  }

  main();

});
