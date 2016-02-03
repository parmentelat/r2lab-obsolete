var app   = require('express')();
var http  = require('http').Server(app);
var io    = require('socket.io')(http);
var path  = require('path');
var serveStatic = require('serve-static');
var bodyParser = require('body-parser');

app.use(serveStatic(__dirname + '/js'))
app.use(serveStatic(__dirname + '/css'))

app.use(bodyParser());

app.get('/', function(req, res){
  res.sendFile('liveleases.html', { root: __dirname });
});

app.get('/leasesbooked', function(req, res){
  res.sendFile('leasesbooked.json', { root: __dirname });
});

app.post('/leasesbooked', function(req, res){
  console.log(req.body.length);
  console.log(req.body);
  res.send(req.body);
});

io.on('connection', function(socket){
  // ADD SLICE MESSAGE
  socket.on('addLease', function(msg){
    // console.log(msg);
    io.emit('addLease', msg);
  });
  // REMOVE SLICE MESSAGE BY ID
  socket.on('delLease', function(msg){
    // console.log(msg);
    io.emit('delLease', msg);
  });
});

http.listen(3000, function(){
  console.log('listening on *:3000');
});
