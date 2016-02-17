$(document).ready(function() {

  var my_slices_name      = ['onelab.inria.r2lab.mario_test', 'onelab.inria.r2lab.admin', 'onelab.inria.mario.tutorial', 'onelab.inria.mario.script'];
  var my_slices_color     = [];
  var actionsQueue        = [];
  var actionsQueued       = [];
  var current_slice_name  = 'onelab.inria.mario.script';
  var current_slice_color = '#ddd';
  var broadcastActions    = false;
  var current_leases      = null;
  var color_pending       = '#000000';
  var keepOldEvent        = null;
  var refreshCicle        = 0;


  function buildCalendar(theEvents) {

    var today = moment().format("YYYY-MM-DD");
    var date = new Date();

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
      defaultView: 'agendaDay',
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
            id: getLocalId(my_title, start, end),
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
            // end: end,
            end: start+ ((3600*1000)*0.5),
            overlap: false,
            editable: false,
            selectable: false,
            color: getCurrentSliceColor(),
            textColor: color_pending,
            id: getLocalId(my_title, start, end),
          };
          updateLeases('addLease', eventData, broadcastActions);
        }
			},

      eventDrop: function(event, delta, revertFunc) {
        if (!confirm("Are you sure about this change?")) {
            revertFunc();
        }
        else {
          event.title = pendingName(event.title);
          event.textColor = color_pending;
          event.editable = false;
          updateLeases('moveLease', event, broadcastActions);
        }
      },

      eventDragStart: function( event, jsEvent, ui, view ) {
        keepOldEvent = event;
      },

      eventRender: function(event, element) {
        element.bind('dblclick', function() {
          if (isMySlice(event.title)) {
            updateLeases('delLease', event, broadcastActions);
          }
        });
      },

      eventResize: function( event, delta, revertFunc, jsEvent, ui, view ) {
        alert('not yet');
      },
      //Events from Json file
      events: theEvents,
    });
  }


  function isR2lab(name){
    var r2lab = false;
    if (name.substring(0, 13) == 'onelab.inria.'){
      r2lab = true;
    }
    return r2lab;
  }


  function parseLease(data){
    var parsedData = $.parseJSON(data);
    var leases = [];

    $.each(parsedData, function(key,val){
      $.each(val, function(k,v){
        // if (isR2lab(v.account.name)){
          newLease = new Object();
          newLease.title = shortName(v.account.name);
          newLease.id = getLocalId(newLease.title, newLease.start, newLease.end);//String(v.uuid);
          newLease.start = v.valid_from;
          newLease.end = v.valid_until;
          newLease.color = getColorLease(newLease.title);
          newLease.editable = isMySlice(newLease.title);
          newLease.overlap = false;
          leases.push(newLease);

          setActionsQueued(newLease.title, newLease.start, newLease.end);
        // }
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

    return leases;
  }


  function resetActionsQueued(){
    actionsQueued = [];
  }


  function getActionsQueued(){
    return actionsQueued;
  }


  function setActionsQueued(title, start, end){
    var local_id = null;
    local_id = getLocalId(title+start+end);
    actionsQueued.push(local_id);
  }


  function sendBroadcast(action, data){
    var socket = io();
    if (action == 'addLease'){
      socket.emit('addLease', data);
    }
    else if (action == 'delLease'){
      socket.emit('delLease', data._id);
    }
  }


  function setCurrentLeases(leases){
    current_leases = leases;
  }


  function getCurrentLeases(){
    return current_leases;
  }


  function listenBroadcast(){
    var socket = io();
    socket.on('addLease', function(msg){
      $('#calendar').fullCalendar('renderEvent', msg, true );
    });
    socket.on('delLease', function(msg){
      $('#calendar').fullCalendar('removeEvents',msg);
    });
    socket.on('moveLease', function(msg){
      alert('not yet');
    });
  }


  function updateLeases(action, data, broadcast){
    if (broadcast){
      sendBroadcast(action, data);
    } else{
      if (action == 'addLease') {
        $('#calendar').fullCalendar('renderEvent', data, true );
        actionsLeases('add', data);
        setActionsQueue('add', data);
      }
      if (action == 'delLease'){
        if( ($.inArray(data._id, getActionsQueue()) == -1) && (data.title.indexOf('* failed *') > -1) ){
          $('#calendar').fullCalendar('removeEvents',data._id);
        }
        else if(data.title.indexOf('(pending)') == -1) {
          $('#calendar').fullCalendar('removeEvents',data._id);
          actionsLeases('del', data);
          setActionsQueue('del', data);
        }
      }
      if (action == 'moveLease'){
        actionsLeases('move', data);
        setActionsQueue('move', data);
      }
    }
  }


  function getLocalId(title, start, end){
    var id = null;

    String.prototype.hash = function() {
      var self = this, range = Array(this.length);
      for(var i = 0; i < this.length; i++) {
        range[i] = i;
      }
      return Array.prototype.map.call(range, function(i) {
        return self.charCodeAt(i).toString(16);
      }).join('');
    }
    id = (title+start+end).hash();
    return id;
  }


  function getActionsQueue(){
    return actionsQueue;
  }


  function setActionsQueue(action, data){
    if(action == 'add'){
      actionsQueue.push(data.id);
    }
    else if (action == 'move'){
      actionsQueue.push(data.id);
      actionsQueue.push(data.id);
    }
    else if (action == 'del'){ //include to not consider when this have failed in text
      actionsQueue.push(data.id);
    }
    else {
      alert ('Someting went wrong in map actions.');
      return false;
    }
  }


  function delActionQueue(id){
    var idx = actionsQueue.indexOf(id);
    actionsQueue.splice(idx,1);
  }


  function resetActionQueue(){
    actionsQueue = [];
  }


  function resetCalendar(){
    $('#calendar').fullCalendar('removeEvents');
  }


  function diffArrays(first, second){
    var diff_array = null;
    diff_array = $(first).not(second).get()
    return diff_array;
  }


  function refreshCalendar(events){
    refreshCicle = refreshCicle + 1;

    if(refreshCicle == 2){
      var diffLeases = diffArrays(getActionsQueue(), getActionsQueued());
      var failedEvents = [];
      $.each(diffLeases, function(key,obj){
        var each = $("#calendar").fullCalendar( 'clientEvents', obj );
        $.each(each, function(k,o){
          newLease = new Object();
          newLease.title = failedName(o.title);
          newLease.id = o.id;
          newLease.start = o.start;
          newLease.end   = o.end;
          newLease.color = "#FF0000";
          newLease.overlap = false;
          newLease.editable = false;
          failedEvents.push(newLease);
        });
      });

      resetActionQueue();
      resetCalendar();
      $('#calendar').fullCalendar('addEventSource', events);
      $('#calendar').fullCalendar('addEventSource', failedEvents);

      refreshCicle = 0;

    } else {
      console.log('waiting...'+refreshCicle);
    }
  }


  function actionsLeases(action, data){
    if(action == 'add'){
      $('#actions').append('ADD: '+fullName(resetName(data.title)) +' ['+ data.start +'-'+ data.end+']').append('<br>');
    }
    else if (action == 'move'){
      $('#actions').append('DEL: '+fullName(resetName(keepOldEvent.title)) +' ['+ keepOldEvent.start +'-'+ keepOldEvent.end+']').append('<br>');
      $('#actions').append('ADD: '+fullName(resetName(data.title)) +' ['+ data.start +'-'+ data.end+']').append('<br>');
    }
    else if (action == 'del'){
      $('#actions').append('DEL: '+fullName(resetName(data.title)) +' ['+ data.start +'-'+ data.end+']').append('<br>');
    }
  }


  function getRandomColor() {
    var reserved_colors = ["#D0D0D0", "#FF0000", "#000000"];
    var letters = '0123456789ABCDEF'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++ ) {
        color += letters[Math.round(Math.random() * 15)];
    }

    if ($.inArray(color.toUpperCase(), reserved_colors) > -1){
      getRandomColor();
    }

    return color;
  }


  function fullName(name){
    var new_name = name;
    new_name = 'onelab.inria.'+name;
    return new_name
  }


  function shortName(name){
    var new_name = name;
    new_name = name.replace('onelab.inria.', '');
    new_name = new_name.replace('onelab.upmc.', '');
    return new_name
  }


  function pendingName(name){
    var new_name = name;
    new_name = resetName(name) + ' (pending)';
    return new_name
  }


  function resetName(name){
    var new_name = name;
    new_name = name.replace(' (pending)', '');
    new_name = new_name.replace(' * failed *', '');
    return new_name
  }


  function failedName(name){
    var new_name = name;
    new_name = resetName(name) + ' * failed *';
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


  function setColorLeases(){
    $.each(my_slices_name, function(key,obj){
      my_slices_color[key] = getRandomColor();
    });
    return my_slices_color;
  }


  function getColorLease(slice_title){
    var lease_color = '#d0d0d0';

    if ($.inArray(fullName(slice_title), getMySlicesName()) > -1){
      lease_color = my_slices_color[my_slices_name.indexOf(fullName(slice_title))];
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
    if ($.inArray(fullName(resetName(slice)), getMySlicesName()) > -1){
      is_my = true;
    }
    return is_my;
  }


  function buildSlicesBox(leases){
    var knew = [];
    var slices = $("#my-slices");

    slices.html('<h4 align="center">drag & drop slices</h4>');

    $.each(leases, function(key,val){
      if ($.inArray(val.title, knew) === -1) { //already present?
        if (isMySlice(val.title)) {
          if(val.title === getCurrentSliceName()){
            setCurrentSliceColor(val.color);
          }
          slices.append($("<div />").addClass('fc-event').attr("style", "background-color: "+ val.color +"").text(val.title)).append($("<div />").attr("id", idFormat(val.title)).addClass('noactive'));
        } else{
          slices.append($("<div />").addClass('fc-event-not-mine').attr("style", "background-color: "+ val.color +"").text(val.title));
        }
        knew.push(val.title);
      }
    });

    $('#my-slices .fc-event').each(function() {
      $(this).draggable({
        zIndex: 999,
        revert: true,      // will cause the event to go back to its
        revertDuration: 0  //  original position after the drag
      });
    });
  }


  function getMySlicesName(){
    return my_slices_name;
  }


  function getMySlicesColor(){
    return my_slices_color;
  }


  function eventPresentbyDate(start, end, title) {
    var title = pendingName(shortName(title)); //'onelab.inria.mario.tutorial';
    var start = new Date(start); //new Date("2016-02-11T13:00:00Z");
    var end   = new Date(end); //new Date("2016-02-11T14:30:00Z");

    calendar = $('#calendar').fullCalendar('clientEvents');

    $.each(calendar, function(key,obj){
      if ((new Date(obj.start._d) - start == 0) && (new Date(obj.end._d) - end == 0) && (obj.title == title)){
        obj.title = resetName(title);
        obj.textColor = "#ffffff";
        obj.editable = true;
        $('#calendar').fullCalendar( 'rerenderEvents', obj.id);
      }
    });
  }


  function loadEfects(opt){
    if(opt == 'in'){
      $('#loading').fadeIn(100);
    }
    else {
      $('#loading').delay(100).fadeOut();
      $('#all').fadeIn(100);
    }
  }


  function waitForLeases(){
    if(getCurrentLeases() !== null){
      resetActionsQueued();
      var leases = getCurrentLeases();
      var leasesbooked  = parseLease(leases);
      loadEfects();
      buildCalendar(leasesbooked);
      setCurrentSliceBox(getCurrentSliceName());
      // in case of receiving live booking
      if (broadcastActions){
        listenBroadcast();
      }
    }
    else{
      loadEfects('in');
      setTimeout(function(){
        waitForLeases();
      },250);
    }
  }


  function main (){
    waitForLeases();
    setColorLeases();

    var socket = io.connect("http://r2lab.inria.fr:443");
    socket.on('chan-leases', function(msg){
      setCurrentLeases(msg)
      resetActionsQueued();;
      var leases = getCurrentLeases();
      var leasesbooked = parseLease(leases);

      refreshCalendar(leasesbooked);
      setCurrentSliceBox(getCurrentSliceName());
    });

  }


  // function sendConfirm(leases){
  //   $.ajax({
  //     url: '/leasesbooked',
  //     type: 'POST',
  //     data: JSON.stringify(leases),
  //     contentType: 'application/json; charset=utf-8',
  //     dataType: 'json',
  //     async: false,
  //     success: function(msg) {
  //         alert('Done, booked successfully!');
  //     }
  //   });
  // }
  //
  //
  // $('#confirm').click(function() {
  //   calendar = $('#calendar').fullCalendar('clientEvents')
  //   leases = [];
  //   leases_avoid = ['nightly', 'pastDate'];
  //   $.each(calendar, function(key,obj){
  //     var lease = new Object();
  //
  //     lease.name  = fullName(obj.title);
  //     lease.start = obj.start._d;
  //     lease.end   = obj.end._d;
  //     if ($.inArray(obj.id, leases_avoid) === -1) {
  //       leases.push(lease);
  //     }
  //   });
  //
  //   sendConfirm(leases);
  // });

  main();
});
