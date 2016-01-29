var socket = io();

socket.on('add_lease', function(msg){
  $('#calendar').fullCalendar('renderEvent', msg, true );
});

socket.on('remove_lease_by_id', function(msg){
  $('#calendar').fullCalendar('removeEvents',msg);
});
