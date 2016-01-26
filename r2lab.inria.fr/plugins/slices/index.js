var app   = require('express')();
var http  = require('http').Server(app);
var io    = require('socket.io')(http);
var path  = require('path');
var serveStatic = require('serve-static')

app.use(serveStatic(__dirname + '/js'))
app.use(serveStatic(__dirname + '/css'))

var slices_complete = 'slices_complete.json';

app.get('/events', function(req, res){
  res.sendFile('events.html', { root: __dirname });
});

app.get('/slices_complete', function(req, res){
  res.sendFile('slices_complete.json', { root: __dirname });
});

io.on('connection', function(socket){
  // ADD SLICE MESSAGE
  socket.on('add_slice', function(msg){
    // console.log(msg);
    io.emit('add_slice', msg);
  });
  // REMOVE SLICE MESSAGE BY ID
  socket.on('remove_slice_by_id', function(msg){
    // console.log(msg);
    io.emit('remove_slice_by_id', msg);
  });
});

http.listen(3000, function(){
  console.log('listening on *:3000');
});
