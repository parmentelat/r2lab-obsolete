var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);

var fs = require('fs');

var channel = 'r2lab-status';
var status_filename = 'r2lab-status.json';

var port_number = 3000;

io.on('connection', function(socket){
    console.log('user connect');
    socket.on('disconnect', function(){
	console.log('user disconnect');
    });
});

/* 
  forward messages that come on our channel
  useful for debugging / tuning, so we can send JSON
  messages manually
 */
io.on('connection', function(socket){
    console.log("Routing channel " + channel);
    socket.on(channel, function(msg){
	console.log("Forwarding on channel " + channel + ":" + msg);
	io.emit(channel, msg);
    });

});


/* TODO : create file if not present */

fs.watch(status_filename, 
  function(event, filename){
    fs.readFile(status_filename,
      function(err, data){
          if (err) throw err;
	  /* convert ArrayBuffer to string */
	  var buffer = new Uint8Array(data)
	  var string = String.fromCharCode.apply(null, data)
	  console.log("event=" + event + ", emitting on channel " + channel + ":" + string);
	  io.emit(channel, string);
      });
  });

http.listen(port_number, function(){
  console.log('listening on *:' + port_number);
});
