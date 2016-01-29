var app   = require('express')();
var http  = require('http').Server(app);
var io    = require('socket.io')(http);
var path  = require('path');
var serveStatic = require('serve-static')

app.use(serveStatic(__dirname + '/js'))
app.use(serveStatic(__dirname + '/css'))

var leases_complete = 'leases_complete.json';

app.get('/', function(req, res){
  res.sendFile('leases.html', { root: __dirname });
});

app.get('/leases_complete', function(req, res){
  res.sendFile('leases_complete.json', { root: __dirname });
});

app.get('/leases_original', function(req, res){
  res.sendFile('leases_original.json', { root: __dirname });
});

io.on('connection', function(socket){
  // ADD SLICE MESSAGE
  socket.on('add_lease', function(msg){
    // console.log(msg);
    io.emit('add_lease', msg);
  });
  // REMOVE SLICE MESSAGE BY ID
  socket.on('remove_lease_by_id', function(msg){
    // console.log(msg);
    io.emit('remove_lease_by_id', msg);
  });
});

http.listen(3000, function(){
  console.log('listening on *:3000');
});
