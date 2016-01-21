var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);

var fs = require('fs');

app.get('/', function(req, res){
    res.sendFile(__dirname + '/index.html');
});

io.on('connection', function(socket){
  console.log('a user connected');
  socket.on('disconnect', function(){
    console.log('user disconnected');
  });
});

io.on('connection', function(socket){
    console.log("Routing type " + "chat message");
    socket.on("chat message", function(msg){
	console.log("Forwarding type " + "chat message");
	io.emit("chat message", msg);
    });
    console.log("Routing type " + "r2lab status");
    socket.on("r2lab status", function(msg){
	console.log("Forwarding type " + "r2lab status" + msg);
	io.emit("r2lab status", msg);
    });

});

http.listen(10000, function(){
  console.log('listening on *:10000');
});
