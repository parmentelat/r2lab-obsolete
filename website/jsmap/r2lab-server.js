var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);

var fs = require('fs');

var channel = 'r2lab-news';
var signalling = 'r2lab-signalling';
var news_filename = 'r2lab-news.json';
var complete_filename = 'r2lab-complete.json';

var port_number = 8000;

app.get('/', function(req, res){
    /* answer something */
    res.sendFile(__dirname + '/r2lab-complete.json');
    /* and emit the complete status */
    console.log("Received request on / : sending " + complete_filename);
    emit_file(complete_filename);
});

io.on('connection', function(socket){
    console.log('user connect');
    socket.on('disconnect', function(){
	console.log('user disconnect');
    });
});

io.on('connection', function(socket){
    /* 
       forward messages that come on our channel
       useful for debugging / tuning, so we can send JSON
       messages manually (e.g. using a chat app)
    */
    socket.on(channel, function(msg){
	console.log("Forwarding on channel " + channel + ":" + msg);
	io.emit(channel, msg);
    });
    /*
      this is more crucial, this is how complete status gets transmitted initially 
    */
    socket.on(signalling, function(msg){
	console.log("Received " + msg + " on channel " + signalling);
	emit_file(complete_filename);
    });
});


function emit_file(filename){
    try {
	fs.readFile(filename,
		    function(err, data){
			if (err) throw err;
			/* convert ArrayBuffer to string */
			var buffer = new Uint8Array(data)
			var string = String.fromCharCode.apply(null, data)
			console.log("emitting on channel " + channel + ":" + string);
			io.emit(channel, string);
		    });
    }
    catch(err){
	console.log("Error when emitting file " + filename);
    }
}

fs.watch(news_filename, 
	 function(event, filename){
	     console.log("watch -> event=" + event);
	     emit_file(news_filename);
	 });

http.listen(port_number, function(){
    console.log('listening on *:' + port_number);
});
