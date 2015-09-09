// deps
var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var fs = require('fs');

//// names for the channels used
// sending deltas; json is flying on this channel
var channel = 'r2lab-news';
// requesting a whole status; anything arriving
// on this channel causes a full status to be exposed
// on r2lab-news
var signalling = 'r2lab-signalling';
//// filenames
// the file that is watched for changes
// when another program writes this file, we send its contents
// to all clients
var news_filename = 'r2lab-news.json';
// this is where we read and write current complete status
// it typically is expected to be written by an outside program
// but any changes seen in r2lab-news.json are merged and stored
// in this file, so that it should always contain a consistent
// global view
var complete_filename = 'r2lab-complete.json';

////
var port_number = 8000;

var debug=false;

// program this webserver so that a GET to /
// exposes the complete json status
// + triggers a broadcast on all clients
// only for debugging
app.get('/', function(req, res){
    /* answer something */
    res.sendFile(__dirname + '/r2lab-complete.json');
    /* and emit the complete status */
    console.log("Received request on / : sending " + complete_filename);
    emit_file(complete_filename);
});

// remainings of a socket.io example, we don't react
// to these events as of now
io.on('connection', function(socket){
    console.log('user connect');
    socket.on('disconnect', function(){
	console.log('user disconnect');
    });
});

// arm callbacks for the 2 channels we use
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

// utility to open a file and broadcast its contents
function emit_file(filename){
    try {
	fs.readFile(filename,
		    function(err, data){
			if (err) throw err;
			/* convert ArrayBuffer to string */
			var buffer = new Uint8Array(data)
			var string = String.fromCharCode.apply(null, data)
			if (debug) console.log("emitting on channel " + channel + ":" + string);
			io.emit(channel, string);
		    });
    }
    catch(err){
	console.log("Error when emitting file " + filename);
    }
}

// watch complete status file: set callback
fs.watch(news_filename, 
	 function(event, filename){
	     if (debug) console.log("watch -> event=" + event);
	     emit_file(news_filename);
	 });

// run http server
http.listen(port_number, function(){
    console.log('listening on *:' + port_number);
});
