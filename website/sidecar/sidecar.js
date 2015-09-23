#!/usr/bin/env node
// deps
var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var fs = require('fs');
var path = require('path');

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
// use -l command line option to use files in local dir
var filename_news = '/var/lib/sidecar/news.json';
// this is where we read and write current complete status
// it typically is expected to be written by an outside program
// but any changes seen in r2lab-news.json are merged and stored
// in this file, so that it should always contain a consistent
// global view
var filename_complete = '/var/lib/sidecar/complete.json';

////
var port_number = 443;

// use -v to turn on
var verbose_flag=false;

// always display
function display(args){
    for (var i in arguments) {
       console.log(new Date() + " " + arguments[i]);
    }
}
// display only if in verbose mode
function vdisplay(args){
    if (verbose_flag)
	display.apply(this, arguments);
}


// program this webserver so that a GET to /
// exposes the complete json status
// + triggers a broadcast on all clients
// only for debugging
app.get('/', function(req, res){
    // answer something
    res.sendFile(__dirname + '/r2lab-complete.json');
    // and emit the complete status 
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
    // preferred method is to send a news chunk through socket.io
    // in this case we
    // update complete.json (i.e, read the file, apply changes, store again)
    // and forward the news as-is
    // this can also be useful for debugging / tuning
    // so we can send JSON messages manually (e.g. using a chat app)
    socket.on(channel_news, function(news_string){
	update_complete_file_from_news(news_string);
	vdisplay("Forwarding on channel " + channel_news + ":" + news_string);
	io.emit(channel_news, news_string);
    });
    // this is more crucial, this is how complete status gets transmitted initially 
    socket.on(channel_signalling, function(msg){
	display("Received " + msg + " on channel " + channel_signalling);
	emit_file(filename_complete);
    });
});

// convenience function to synchroneously read a file as a string
// xxx hack - sometimes (quite often indeed) we see
// this read returning an empty string...
// apparently when watching a file we get to it too fast, so 
// allow for 2 attempts
function sync_read_file_as_string(filename, verbose){
    try{ 
	var contents = fs.readFileSync(filename, 'utf8');
	if (verbose) vdisplay("sync read (1) " + filename + " -> " + contents);
	if (contents == "") {
	    display("sync read (2nd attempt) on " + filename);
	    contents = fs.readFileSync(filename, 'utf8');
	    if (verbose) vdisplay("sync read (2) -> " + contents);
	}
	if (contents == "")
	    display("warning, file " + filename + " still read as empty after 2 attempts");
	return contents;
    } catch(err){
	display("Could not sync read " + filename + err.stack);
    }
}

// same but do JSON.parse on result
function sync_read_file_as_infos(filename) {
    try {
	return JSON.parse(sync_read_file_as_string(filename));
    } catch(err) {
	display("Could not parse JSON in " + filename,
		err.stack);
    }
}

// convenience function to save a list of JS infos (records) into a file
// we do everything synchroneously to avoid trouble
function sync_save_infos_in_file(filename, infos){
    try{
	fs.writeFileSync(filename, JSON.stringify(infos), 'utf8');
	vdisplay("sync (Over)wrote " + filename)
    } catch(err) {
	display("Could not sync write " + filename + err);
    }
}    
    
// merge news info into complete infos; return new complete
function merge_news_into_complete(complete_infos, news_infos){
    for (var nav=0; nav < news_infos.length; nav++) {
	var node_info = news_infos[nav];
	var id = node_info.id;
	var found = false;
	for (var nav2=0; nav2 < complete_infos.length; nav2++) {
	    var complete_info = complete_infos[nav2];
	    if (complete_info['id'] == id) {
		found = true;
		// copy all contents from node_info into complete_infos
		for (var prop in node_info)
		    if (node_info[prop] != undefined)
			complete_info[prop] = node_info[prop];
		// we're done, skip rest of search in complete_infos
		break;
	    }
	}
	// complete gets created empty at the very beginning
	// so, if id is not yet known, add it as-is
	if (! found)
	    complete_infos.push(node_info);
    }
    return complete_infos;
}
		

// utility to open a file and broadcast its contents on channel_news
function emit_file(filename){
    var complete_string = sync_read_file_as_string(filename);
    if (complete_string != "") {
//	vdisplay("emit_file: sending on channel " + channel_news + ":" + complete_string);
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
    if (news_string == "") {
	display("OOPS - empty news feed - ignored");
	return;
    }
    try{
	// start from the complete infos
	var complete_infos = sync_read_file_as_infos(filename_complete);
	// convert string into infos
	var news_infos = JSON.parse(news_string);
	// merge both
	complete_infos = merge_news_into_complete(complete_infos, news_infos);
//	vdisplay("merged news : " + JSON.stringify(news_infos));
	// save result
	sync_save_infos_in_file(filename_complete, complete_infos);
	return complete_infos;
    } catch(err) {
	display(" OOPS - unexpected exception in update_complete_file_from_news",
		"news_string is " + news_string,
		"strack trace is " + err.stack);
    }
}
function parse_args() {
    // very rough parsing of command line args - to set verbosity
    var argv = process.argv.slice(2);
    argv.forEach(function (val, index, array) {
	// verbose
	if (val == "-v")
	    verbose_flag=true;
	// local dev (use json files in .)
	if (val == "-l") {
	    filename_news = path.basename(filename_news);
	    filename_complete = path.basename(filename_complete);
	    console.log("local mode : watching " + filename_news);
	}
    });
    vdisplay("news file = " + filename_news,
	    "complete file = " + filename_complete);
}

function init_watcher() {
    var touch_if_missing = function(filename) {
	try {
	    fs.statSync(filename);
	} catch (err) {
	    sync_save_infos_in_file(filename, []);
	}
    }
    touch_if_missing(filename_news);
    touch_if_missing(filename_complete);

    // watch news file and attach callback
    var watcher = fs.watch(
	filename_news, 
	function(event, filename){
	    vdisplay("watch -> event=" + event);
	    // read news file as a string
	    var news_string = sync_read_file_as_string(filename_news, true);
	    // update complete from news_string
	    var complete_infos = update_complete_file_from_news(news_string);
	    // should do emit_file but we already have the data at hand
	    vdisplay("NEWS: sending on channel " + channel_news + ":" + news_string);
	    io.emit(channel_news, news_string);
	});
}

// run http server
function run_server() {
    try {
	http.listen(port_number, function(){
	    display('listening on *:' + port_number);
	});
    } catch (err) {
	console.log("Could not run http server on port " + port_number);
	console.run("Need to sudo ?");
    }
}

function main() {
    parse_args();
    init_watcher();
    run_server();
}

main()
