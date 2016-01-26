var socket = io();

socket.on('add_slice', function(msg){
  $('#calendar').fullCalendar('renderEvent', msg, true );
});

socket.on('remove_slice_by_id', function(msg){
  $('#calendar').fullCalendar('removeEvents',msg);
});
