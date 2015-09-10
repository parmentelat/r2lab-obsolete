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

var verbose_flag=false;
//verbose_flag=true;

// always display
function display(args){
    for (var i in arguments) {
       console.log(new Date() + " " + arguments[i]);
    }
}
// display in verbose mode
function verbose(args){
    if (verbose_flag)
	display.apply(this, arguments);
}


// program this webserver so that a GET to /
// exposes the complete json status
// + triggers a broadcast on all clients
// only for debugging
app.get('/', function(req, res){
    /* answer something */
    res.sendFile(__dirname + '/r2lab-complete.json');
    /* and emit the complete status */
    display("Received request on / : sending " + filename_complete);
    emit_file(filename_complete);
});

// remainings of a socket.io example, we don't react
// to these events as of now
io.on('connection', function(socket){
    display('user connect');
    socket.on('disconnect', function(){
	display('user disconnect');
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
	verbose("Forwarding on channel " + channel_news + ":" + msg);
	io.emit(channel_news, msg);
    });
    /*
      this is more crucial, this is how complete status gets transmitted initially 
    */
    socket.on(channel_signalling, function(msg){
	display("Received " + msg + " on channel " + channel_signalling);
	emit_file(filename_complete);
    });
});

// convenience function to read a file as a string and do something with result
function sync_read_file_as_string(filename){
    try{
	verbose("sync Reading file " + filename);
	return fs.readFileSync(filename, 'utf8');
    } catch(err){
	display("Could not sync read " + filename + err);
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
	    display("2nd attempt to read " + filename);
	    return JSON.parse(sync_read_file_as_string(filename));
	} catch(err) {
	    display("Could not parse JSON in " + filename + " after 2 attempts");
	}
    }
}

// convenience function to save a list of JS infos (records) into a file
// we do everything synchroneously to avoid trouble
function sync_save_infos_in_file(filename, infos){
    try{
	fs.writeFileSync(filename, JSON.stringify(infos), 'utf8');
	verbose("sync (Over)wrote " + filename)
    } catch(err) {
	display("Could not sync write " + filename + err);
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
    if (complete_string != "") {
	verbose("emit_file: sending on channel " + channel_news + ":" + complete_string);
	io.emit(channel_news, complete_string);
    } else {
	display("OOPS - empty contents in " + filename)
    }
}


// convenience function to
// (*) open and read r2lab-complete
// (*) merge news dictionary
// (*) save result in r2lab-complete
function update_complete_file_from_news(news_string){
    try{
	// start from the complete infos
	var complete_infos = sync_read_file_as_infos(filename_complete);
	// convert string into infos
	var news_infos = JSON.parse(news_string);
	// merge both
	complete_infos = merge_news_into_complete(complete_infos, news_infos);
	verbose("merged news : " + JSON.stringify(news_infos));
	// save result
	sync_save_infos_in_file(filename_complete, complete_infos);
	return complete_infos;
    } catch(err) {
	if (news_string == "")
	    display("OOPS - empty news feed - ignored");
	else {
	    display(" OOPS - unexpected exception in update_complete_file_from_news " + err,
		    "news_string is " + news_string,
		    "strack trace is " + err.stack);
	}
    }
}

// watch complete status file: set callback
var watcher = fs.watch(
    filename_news, 
    function(event, filename){
	verbose("watch -> event=" + event);
	// read news file as a string
	var news_string = sync_read_file_as_string(filename_news);
	// update complete from news_string
	var complete_infos = update_complete_file_from_news(news_string);
	// should do emit_file but we already have the data at hand
	verbose("NEWS: sending on channel " + channel_news + ":" + news_string);
	io.emit(channel_news, news_string);
    });

// very rough parsing of command line args - to set verbosity
var argv = process.argv.slice(2);
argv.forEach(function (val, index, array) {
    if (val == "-v") verbose_flag=true;
});

// run http server
http.listen(port_number, function(){
    display('listening on *:' + port_number);
});
