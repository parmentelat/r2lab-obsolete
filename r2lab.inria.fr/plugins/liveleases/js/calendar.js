$(document).ready(function() {

  var list_of_my_slices   = ['onelab.inria.r2lab.admin', 'onelab.inria.mario.tutorial', 'onelab.inria.mario.script'];
  var current_slice_name  = 'onelab.inria.mario.script';
  var current_slice_color = '#ddd';
  var broadcastActions    = false;
  var current_leases      = null;
  var color_pending       = '#000';

  function newId(){
    var date  = new Date();
    var newId = date.getSeconds()+''+date.getMilliseconds()+''+Math.round((Math.random() * 10000));
    return newId;
  }


  function buildCalendar(events) {

    var today = moment().format("YYYY-MM-DD");
    var path_to_leases_complete = events;
    var date = new Date();

    $('#my-slices .fc-event').each(function() {
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
        right: 'agendaDay,agendaTwoDay',
      },

      views: {
        agendaTwoDay: {
          type: 'agenda',
          duration: { days: 2 },
          buttonText: '2 days'
        }
      },
      defaultTimedEventDuration: '00:30:00',
      forceEventDuration: true,
      defaultView: 'agendaTwoDay',
      timezone: 'Europe/Paris',
      defaultDate: today,
      selectHelper: false,
      overlap: false,
      selectable: true,
      editable: true,
      allDaySlot: false,
      droppable: true,
      height: 970,

      //Events
      // this is fired when a selection is made
      select: function(start, end, event, view) {
        //Avoid past dates when try to book a lease
        if (moment().diff(start, 'days') > 0) {
          $('#calendar').fullCalendar('unselect');
          $('#messages').fadeOut(200).fadeIn(200).fadeOut(200).fadeIn(200);
          $('#messages').delay(2000).fadeOut();
          return false;
        }
        var my_title = getCurrentSliceName();
        var eventData;
        if (my_title) {
          eventData = {
            title: pendingName(my_title),
            start: start,
            end: end,
            //end: start+ ((3600*1000)*1),
            overlap: false,
            editable: false,
            selectable: false,
            color: getCurrentSliceColor(),
            textColor: color_pending,
            id: newId(),
          };
          updateLeases('addLease', eventData, broadcastActions);
        }
        $('#calendar').fullCalendar('unselect');
      },

      // this allows things to be dropped onto the calendar
      drop: function(start, end, event, view) {
        var element = $(this);
        var last_drag_color = element.css("background-color");
        var last_drag_name  = $.trim(element.text());

        setCurrentSliceColor(last_drag_color);
        setCurrentSliceName(last_drag_name);
        setCurrentSliceBox(element.text());

        var my_title = getCurrentSliceName();
        var eventData;
        if (my_title) {
          eventData = {
            title: pendingName(my_title),
            start: start,
            end: end,
            //end: start+ ((3600*1000)*1),
            overlap: false,
            editable: false,
            selectable: false,
            color: getCurrentSliceColor(),
            textColor: color_pending,
            id: newId(),
          };
          updateLeases('addLease', eventData, broadcastActions);
        }
			},

      //Remove leases with double click
      eventRender: function(event, element) {
        element.bind('dblclick', function() {
          if (isMySlice(event.title)) {
            updateLeases('delLease', event._id, broadcastActions);
          }
        });
      },
      //Events from Json file
      events: path_to_leases_complete,
    });
  }


  function parseLease(data){
    var parsedData = $.parseJSON(data);
    var all_leases_for_calendar;
    var leases = [];

    $.each(parsedData, function(key,val){
      $.each(val, function(k,v){
        newLease = new Object();
        newLease.title = shortName(v.account.name);
        newLease.id    = String(v.uuid);
        newLease.start = v.valid_from;
        newLease.end   = v.valid_until;
        newLease.color = setColorLease(newLease.title);
        newLease.editable = isMySlice(newLease.title);
        newLease.overlap = false;
        leases.push(newLease);
      });
    });

    buildSlicesBox(leases);

    //Nightly routine fixed in each nigth from 3AM to 5PM
    newLease = new Object();
    newLease.title = "nightly routine";
    newLease.id = "nightly";
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
    newLease.end   = "2016-02-02T00:00:00Z";
    newLease.overlap = false;
    newLease.editable = false;
    newLease.rendering = "background",
    newLease.color = "#ffe5e5";
    leases.push(newLease);

    all_leases_for_calendar = leases;

    return all_leases_for_calendar;
  }


  function sendBroadcast(action, data){
    var socket = io();
    if (action == 'addLease'){
      socket.emit('addLease', data);
    }
    else if (action == 'delLease'){
      socket.emit('delLease', data);
    }
  }


  function listenBroadcastFromServer(){
    var socket = io.connect("http://r2lab.inria.fr:443");

    socket.on('chan-leases', function(msg){
      current_leases = msg;
      // console.log(current_leases);
    });
  }


  function listenBroadcast(){
    var socket = io();
    socket.on('addLease', function(msg){
      $('#calendar').fullCalendar('renderEvent', msg, true );
    });
    socket.on('delLease', function(msg){
      $('#calendar').fullCalendar('removeEvents',msg);
    });
  }


  function updateLeases(action, data, broadcast){
    if (broadcast){
      sendBroadcast(action, data);
    } else{
      if (action == 'addLease') {
        $('#calendar').fullCalendar('renderEvent', data, true );
        alert('add lease');
      }
      if (action == 'delLease'){
        $('#calendar').fullCalendar('removeEvents',data);
      }
    }
  }


  function eventPresentbyDate(start, end, title) {
    var title = noPendingName(shortName(title)); //'onelab.inria.mario.tutorial';
    var start = new Date(start); //new Date("2016-02-11T13:00:00Z");
    var end   = new Date(end); //new Date("2016-02-11T14:30:00Z");

    calendar = $('#calendar').fullCalendar('clientEvents');

    $.each(calendar, function(key,obj){
      if ((new Date(obj.start._d) - start == 0) && (new Date(obj.end._d) - end == 0) && (obj.title == title)){
        obj.title = noPendingName(title);
        obj.textColor = "#000"
        // console.log(obj.id);
        $('#calendar').fullCalendar( 'rerenderEvents', obj.id);
      }
    });
  }


  function getRandomColor() {
    var letters = '0123456789ABCDEF'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++ ) {
        color += letters[Math.round(Math.random() * 15)];
    }
    return color;
  }


  function fullName(name){
    var new_name;
    new_name = 'onelab.inria.'+name;
    return new_name
  }


  function shortName(name){
    var new_name;
    new_name = name.replace('onelab.inria.', '');
    return new_name
  }


  function pendingName(name){
    var new_name;
    new_name = name + ' (pending)';
    return new_name
  }


  function noPendingName(name){
    var new_name;
    new_name = name.replace(' (pending)', '');
    return new_name
  }


  function getCurrentSliceName(){
    // var current_slice_name = $('#current-slice').attr('data-current-slice-name');
    return shortName(current_slice_name);
  }


  function getCurrentSliceColor(){
    // var current_slice_color = $('#current-slice').attr('data-current-slice-color');
    return current_slice_color;
  }


  function setCurrentSliceColor(color){
    // $('#current-slice').attr('data-current-slice-color', color);
    current_slice_color = color;
    return true;
  }


  function setCurrentSliceName(name){
    // $('#current-slice').attr('data-current-slice-name', name);
    current_slice_name = name;
    return true;
  }


  function setColorLease(slice){
    var lease_color = '#d0d0d0';

    if ($.inArray(fullName(slice), getMySlices()) > -1){
      lease_color = getRandomColor();
    }
    return lease_color;
  }


  function idFormat(id){
    new_id = id.replace('.', '');
    return new_id;
  }


  function setCurrentSliceBox(element){
    id = idFormat(element);
    $(".noactive").removeClass('sactive');
    $("#"+id).addClass('sactive');
  }


  function isMySlice(slice){
    var is_my = false;
    if ($.inArray(fullName(slice), getMySlices()) > -1){
      is_my = true;
    }
    return is_my;
  }


  function buildSlicesBox(leases){
    var knew = [];
    var slices = $("#my-slices");

    $.each(leases, function(key,val){
      if ($.inArray(val.title, knew) === -1) { //already present?
        if (isMySlice(val.title)) {
          if(val.title === getCurrentSliceName()){
            setCurrentSliceColor(val.color);
          }
          knew.push(val.title);
          slices.append($("<div />").addClass('fc-event').attr("style", "background-color: "+ val.color +"").text(val.title)).append($("<div />").attr("id", idFormat(val.title)).addClass('noactive'));
        } else{
          slices.append($("<div />").addClass('fc-event-not-mine').attr("style", "background-color: "+ val.color +"").text(val.title));
        }
      }
    });
  }


  function getMySlices(){
    // list_of_my_slices = ['onelab.inria.r2lab.mario_test', 'onelab.inria.r2lab.admin', 'onelab.inria.mario.tutorial', 'onelab.inria.mario.script']
    return list_of_my_slices;
  }

  function ok(){
    eventPresentbyDate("2016-02-11T13:00:00Z","2016-02-11T14:30:00Z",'onelab.inria.mario.tutorial');
    //remover o noPendingName para pendingName
  }
  function waitForLeases(){
    if(current_leases !== null){
      var leasesbooked  = parseLease(current_leases);
      // var leasesbooked  = parseLease('/plugins/liveleases/leasesbooked.json');
      $('#loading').delay(100).fadeOut();
      $('#all').fadeIn(100);
      buildCalendar(leasesbooked);
      setCurrentSliceBox(getCurrentSliceName());
      if (broadcastActions){
        listenBroadcast();
      }

      window.setTimeout( ok, 5000 ); // 5 seconds

    }
    else{
      $('#loading').fadeIn(100);
      setTimeout(function(){
        waitForLeases();
      },250);
    }
  }


  function main (){
    listenBroadcastFromServer();
    waitForLeases();
  }


  function sendConfirm(leases){
    $.ajax({
      url: '/leasesbooked',
      type: 'POST',
      data: JSON.stringify(leases),
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
      async: false,
      success: function(msg) {
          alert('Done, booked successfully!');
      }
    });
  }


  $('#confirm').click(function() {
    calendar = $('#calendar').fullCalendar('clientEvents')
    leases = [];
    leases_avoid = ['nightly', 'pastDate'];
    $.each(calendar, function(key,obj){
      var lease = new Object();

      lease.name  = fullName(obj.title);
      lease.start = obj.start._d;
      lease.end   = obj.end._d;
      if ($.inArray(obj.id, leases_avoid) === -1) {
        leases.push(lease);
      }
    });

    sendConfirm(leases);
  });

  main();
});
