#!/usr/bin/env node
// deps
var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var fs = require('fs');

//// names for the channels used
// sending deltas; json is flying on this channel
var channel_news = 'r2lab-news';
// requesting a whole status; anything arriving
// on this channel causes a full status to be exposed
// on r2lab-news
var channel_signalling = 'r2lab-signalling';
//// filenames
// the file that is watched for changes
// when another program writes this file, we send its contents
// to all clients
var filename_news = 'r2lab-news.json';
// this is where we read and write current complete status
// it typically is expected to be written by an outside program
// but any changes seen in r2lab-news.json are merged and stored
// in this file, so that it should always contain a consistent
// global view
var filename_complete = 'r2lab-complete.json';

////
var port_number = 8000;

var verbose=false;
//verbose=true;

// program this webserver so that a GET to /
// exposes the complete json status
// + triggers a broadcast on all clients
// only for debugging
app.get('/', function(req, res){
    /* answer something */
    res.sendFile(__dirname + '/r2lab-complete.json');
    /* and emit the complete status */
    console.log("Received request on / : sending " + filename_complete);
    emit_file(filename_complete);
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
    socket.on(channel_news, function(msg){
	console.log("Forwarding on channel " + channel_news + ":" + msg);
	io.emit(channel_news, msg);
    });
    /*
      this is more crucial, this is how complete status gets transmitted initially 
    */
    socket.on(channel_signalling, function(msg){
	console.log("Received " + msg + " on channel " + channel_signalling);
	emit_file(filename_complete);
    });
});

// convenience function to read a file as a string and do something with result
function sync_read_file_as_string(filename){
    try{
	if (verbose) console.log("sync Reading file " + filename);
	return fs.readFileSync(filename, 'utf8');
    } catch(err){
	console.log("Could not sync read " + filename + err);
    }
}

// allow for 2 attempts
function sync_read_file_as_infos(filename) {
    try {
	// xxx hack - sometimes (quite often indeed) we see
	// this read returning an empty string
	return JSON.parse(sync_read_file_as_string(filename));
    } catch(err) {
	try {
	    console.log("2nd attempt to read " + filename);
	    return JSON.parse(sync_read_file_as_string(filename));
	} catch(err) {
	    console.log("Could not parse JSON in " + filename + " after 2 attempts");
	}
    }
}

// convenience function to save a list of JS infos (records) into a file
// we do everything synchroneously to avoid trouble
function sync_save_infos_in_file(filename, infos){
    try{
	fs.writeFileSync(filename, JSON.stringify(infos), 'utf8');
	if (verbose) console.log("sync (Over)wrote " + filename)
    } catch(err) {
	console.log("Could not sync write " + filename + err);
    }
    
}    
    
// merge news info into complete infos; return new complete
function merge_news_into_complete(complete_infos, news_infos){
    for (var nav=0; nav < news_infos.length; nav++) {
	var node_info = news_infos[nav];
	var id = node_info.id;
	for (var nav2=0; nav2 < complete_infos.length; nav2++) {
	    var complete_info = complete_infos[nav2];
	    if (complete_info['id'] == id) {
		// copy all contents from node_info into complete_infos
		for (var prop in node_info)
		    if (node_info[prop] != undefined)
			complete_info[prop] = node_info[prop];
		// we're done, skip rest of search in complete_infos
		break;
	    }
	}
    }
    return complete_infos;
}
		

// utility to open a file and broadcast its contents on channel_news
function emit_file(filename){
    var complete_string = sync_read_file_as_string(filename);
    if (verbose) console.log("emitting on channel " + channel_news + ":" + complete_string);
    if (complete_string == "")
	console.log("OOPS - empty contents in " + filename)
    else
	io.emit(channel_news, complete_string);
}


// convenience function to
// (*) open and read r2lab-complete
// (*) merge news dictionary
// (*) save result in r2lab-complete
function update_complete_file_from_news(){
    try{
	
	var complete_infos = sync_read_file_as_infos(filename_complete);
	var news_infos = sync_read_file_as_infos(filename_news);
	complete_infos = merge_news_into_complete(complete_infos, news_infos);
	sync_save_infos_in_file(filename_complete, complete_infos);
	if (verbose) console.log(new Date() + " merged -> " + JSON.stringify(complete_infos));
	return complete_infos;
    } catch(err) {
	if (news_string == "")
	    console.log(new Date() + " OOPS - empty news feed - ignored");
	else {
	    console.log("OOPS - unexpected exception in update_complete_file_from_news " + err);
	    console.log("news_string is " + news_string);
	    console.log("strack trace is " + err.stack);
	}
    }
}

// watch complete status file: set callback
fs.watch(filename_news, 
	 function(event, filename){
	     if (verbose) console.log("watch -> event=" + event);
	     // update complete from news
	     var complete_infos = update_complete_file_from_news();
	     // should do emit_file but we already have the data at hand
	     io.emit(channel_news, JSON.stringify(complete_infos));
	 });

// very rough parsing of command line args - to set verbosity
var argv = process.argv.slice(2);
argv.forEach(function (val, index, array) {
    if (val == "-v") verbose=true;
});

// run http server
http.listen(port_number, function(){
    console.log('listening on *:' + port_number);
});
