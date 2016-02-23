$(document).ready(function() {

  var my_slices_name      = r2lab_slices;//['onelab.inria.r2lab.mario_test', 'onelab.inria.r2lab.admin', 'onelab.inria.mario.tutorial', 'onelab.inria.mario.script'];//r2lab_slices
  var my_slices_color     = [];
  var actionsQueue        = [];
  var actionsQueued       = [];
  var current_slice_name  = current_slice.name;//'onelab.inria.mario.tutorial';//current_slice.name
  var current_slice_color = '#ddd';
  var broadcastActions    = false;
  var current_leases      = null;
  var color_pending       = '#000000';
  var keepOldEvent        = null;


  function buildCalendar(theEvents) {
    var today = moment().format("YYYY-MM-DD");
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
        if (isPastDate(start)) {
          $('#calendar').fullCalendar('unselect');
          sendMessage('This is the past date/time!');
          return false;
        }
        var my_title = getCurrentSliceName();
        var eventData;
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
          updateLeases('addLease', eventData, broadcastActions);
        }
        $('#calendar').fullCalendar('unselect');
      },

      // this allows things to be dropped onto the calendar
      drop: function(date, event, view) {
        var start = date;
        var end   = moment(date).add(30, 'minutes');
        if (isPastDate(start)) {
          $('#calendar').fullCalendar('unselect');
          sendMessage('This is the past date/time!');
          return false;
        }
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

      // this happens when the event is dropped
      eventDrop: function(event, delta, revertFunc) {
        if (!confirm("Confirm this change?")) {
            revertFunc();
        }
        else {
          if (isPastDate(event.start)) {
            revertFunc();
            sendMessage('This is the past date/time!');
          } else {
            event.title = pendingName(event.title);
            event.textColor = color_pending;
            event.editable = false;
            updateLeases('editLease', event, broadcastActions);
          }
        }
      },

      // this fires when one event starts to be dragged
      eventDragStart: function(event, jsEvent, ui, view) {
        keepOldEvent = event;
      },

      // this fires when an event is rendered
      eventRender: function(event, element) {
        element.bind('dblclick', function() {
          if (isMySlice(event.title)) {
            updateLeases('delLease', event, broadcastActions);
          }
        });
      },

      // this is fired when an event is resized
      eventResize: function(event, jsEvent, ui, view) {
        if (!confirm("Confirm this change?")) {
          return;
        }
        else {
          if (isMySlice(event.title)) {
            event.title = pendingName(event.title);
            event.textColor = color_pending;
            event.editable = false;
            updateLeases('editLease', event, broadcastActions);
          }
        }
      },
      //Events from Json file
      events: theEvents,
    });
  }


  function sendMessage(msg, type){
    var cls   = 'danger';
    var title = 'Ooops!'
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
    $('#messages').html("<strong>"+title+"</strong> "+msg);
    $('#messages').fadeOut(200).fadeIn(200).fadeOut(200).fadeIn(200);
    $('#messages').delay(2000).fadeOut();
  }


  function isPastDate(start){
    var past = false;
    if(moment().diff(start, 'minutes') > 0){
      past = true;
    }
    return past;
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
          newLease.uuid = String(v.uuid);
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

    $.merge(leases, setNightlyAndPast());

    return leases;
  }


  function setNightlyAndPast(){
    var notAllowedEvents = []
    //Nightly routine fixed in each nigth from 3AM to 5PM
    newEvent = new Object();
    newEvent.title = "nightly routine";
    newEvent.id = "nightly";
    newEvent.start = " T03:00:00Z";
    newEvent.end   = " T05:00:00Z";
    newEvent.color = "#616161";
    newEvent.overlap = false;
    newEvent.editable = false;
    newEvent.dow = [0,1,2,3,4,5,6,7,8];
    notAllowedEvents.push(newEvent);

    //Past dates
    newEvent = new Object();
    newEvent.id = "pastDate";
    newEvent.start = moment().format("YYYY-01-01T00:00:00Z");
    newEvent.end   = moment().format("YYYY-MM-DD");
    newEvent.overlap = false;
    newEvent.editable = false;
    newEvent.rendering = "background",
    newEvent.color = "#FFE5E5";
    notAllowedEvents.push(newEvent);

    return notAllowedEvents;
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
      socket.emit('delLease', data.id);
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
    socket.on('editLease', function(msg){
      $('#calendar').fullCalendar('renderEvent', msg, true );
    });
  }


  function updateLeases(action, event, broadcast){
    if (broadcast){
      sendBroadcast(action, event);
    } else{
      if (action == 'addLease') {
        $('#calendar').fullCalendar('renderEvent', event, true );
        setActionsQueue('add', event);
      }
      if (action == 'delLease'){
        if( ($.inArray(event.id, getActionsQueue()) == -1) && (event.title.indexOf('* failed *') > -1) ){
          $('#calendar').fullCalendar('removeEvents',event.id);
        }
        else if(event.title.indexOf('(pending)') == -1) {
          $('#calendar').fullCalendar('removeEvents',event.id);
          setActionsQueue('del', event);
        }
      }
      if (action == 'editLease'){
        setActionsQueue('edit', event);
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
    var shiftAction = null;

    if(action == 'add'){
      shiftAction = 'add';
      var request = {
        "slicename"  : fullName(resetName(data.title)),
        "valid_from" : data.start.toISOString(),
        "valid_until": data.end._d.toISOString()
      };
      actionsQueue.push(data.id);
    }
    else if (action == 'edit'){
      shiftAction = 'update';
      var request = {
        "uuid     "  : fullName(resetName(data.uuid)),
        "valid_from" : data.start.toISOString(),
        "valid_until": data.end.toISOString()
      };
    }
    else if (action == 'del'){
      shiftAction = 'delete';
      var request = {
        "uuid     "  : fullName(resetName(data.uuid)),
      };
      delActionQueue(data.id);
    }
    else {
      console.log('Someting went wrong in map actions.');
      return false;
    }
    post_lease_request(shiftAction, request, function(xhttp) {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
        console.log(request);
      }
    });
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
  }


  function getRandomColor() {
    var reserved_colors = ["#D0D0D0", "#FF0000", "#000000", "#FFE5E5", "#616161"];
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
    return shortName(current_slice_name);
  }


  function getCurrentSliceColor(){
    return current_slice_color;
  }


  function setCurrentSliceColor(color){
    current_slice_color = color;
    return true;
  }


  function setCurrentSliceName(name){
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
    var knew = getMySlicesinShortName();
    var slices = $("#my-slices");

    $.each(leases, function(key,val){
      if ($.inArray(val.title, knew) === -1) { //already present?
        if (isMySlice(val.title)) {
          if(val.title === getCurrentSliceName()){
            setCurrentSliceColor(val.color);
          }
          slices.append($("<div />").addClass('fc-event').attr("style", "background-color: "+ val.color +"").text(val.title)).append($("<div />").attr("id", idFormat(val.title)).addClass('noactive'));
        } else{
          $("div.fc-event-not-mine").remove();
          slices.append($("<div />").addClass('fc-event-not-mine').attr("style", "background-color: "+ val.color +"").text(val.title));
        }
        knew.push(val.title);
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


  function buildInitialSlicesBox(leases){
    setColorLeases();
    var knew = [];
    var slices = $("#my-slices");

    slices.html('<h4 align="center">drag & drop slices</h4>');

    $.each(leases, function(key,val){
      val = shortName(val);
      var color = getColorLease(val);
      if ($.inArray(val, knew) === -1) { //already present?
        if (isMySlice(val)) {
          if(val === getCurrentSliceName()){
            setCurrentSliceColor(color);
          }
          slices.append($("<div />").addClass('fc-event').attr("style", "background-color: "+ color +"").text(val)).append($("<div />").attr("id", idFormat(val)).addClass('noactive'));
        } else{
          slices.append($("<div />").addClass('fc-event-not-mine').attr("style", "background-color: "+ color +"").text(val));
        }
        knew.push(val);
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


  function getMySlicesName(){
    return my_slices_name;
  }


  function getMySlicesinShortName(){
    var new_short_names = [];
    $.each(getMySlicesName(), function(key,val){
      new_short_names.push(shortName(val));
    });
    return new_short_names;
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


  function main (){
    // var socket = io.connect("http://r2lab.inria.fr:443");
    // socket.emit('chan-leases-request', current_slice_name);
    // socket.on('chan-leases-request', function(msg){
    //   console.log(msg);
    // });

    resetActionsQueued();
    buildInitialSlicesBox(getMySlicesName());
    buildCalendar(setNightlyAndPast());
    setCurrentSliceBox(getCurrentSliceName());

    var socket = io.connect("http://r2lab.inria.fr:443");
    socket.on('chan-leases', function(msg){
      console.log('chan answer...');
      setCurrentLeases(msg);
      resetActionsQueued();
      var leases = getCurrentLeases();
      var leasesbooked = parseLease(leases);

      refreshCalendar(leasesbooked);
      setCurrentSliceBox(getCurrentSliceName());
    });

  }

  //STOLEN FROM THIERRY
  //from https://docs.djangoproject.com/en/1.9/ref/csrf/
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }

  // callback will be called on the xhttp object upon ready state change
  // see http://www.w3schools.com/ajax/ajax_xmlhttprequest_onreadystatechange.asp
  function post_lease_request(verb, request, callback) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/leases/"+verb, true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    // this is where we retrieve the CSRF token from the context
    var csrftoken = getCookie('csrftoken');
    xhttp.setRequestHeader("X-CSRFToken", csrftoken);
    xhttp.send(JSON.stringify(request));
    xhttp.onreadystatechange = function(){callback(xhttp);};
  }

  main();
});
