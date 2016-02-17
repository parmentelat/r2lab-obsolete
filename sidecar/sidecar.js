#!/usr/bin/env node
// deps
var express_app = require('express')();
var http = require('http').Server(express_app);
var io = require('socket.io')(http);
var fs = require('fs');
var path = require('path');

//// names for the channels used
// sending deltas; json is flying on this channel
var chan_status = 'chan-status';
// requesting a whole status; anything arriving
// on this channel causes a full status to be exposed
// on chan-status
var chan_status_request = 'chan-status-request';

// the channel where the current state of leases is published
var chan_leases = 'chan-leases';

// likewise: anything arriving on this channel requires
// the leases status to be refreshed
// in practical terms this will trigger an event sent back to
// the monitor, asking it to short-circuit its loop
// and to immediately refresh leases
var chan_leases_request = 'chan-leases-request';

//// filenames
// this is where we write current complete status
// essentially for smooth restart
// it is fine to delete, it will just take some while to rebuild itself
// from the outcome of monitor
var filename_complete = '/var/lib/sidecar/complete.json';

////
var port_number = 443;

// use -v to turn on
var verbose_flag = false;

// always display
function display(args){
    for (var i in arguments) {
       console.log(new Date() + " sidecar " + arguments[i]);
    }
}
// display only if in verbose mode
function vdisplay(args){
    if (verbose_flag)
	display.apply(this, arguments);
}

//// historical
// at some point in time, this server would answer
// GET requests on /
// this feature was unused so it's now turned off

// remainings of a socket.io example; this is only
// marginally helpful to check for the server sanity
io.on('connection', function(socket){
    display('user connect');
    socket.on('disconnect', function(){
	display('user disconnect');
    });
});

// arm callbacks for the channels we use
io.on('connection', function(socket){
    //////////////////// status
    // preferred method is to send a news chunk through socket.io
    // on chan-status
    // in this case we:
    // * update complete.json (i.e, read the file, apply changes, store again)
    // * and forward the news as-is
    // NOTE that this can also be used for debugging / tuning
    // by sending JSON messages manually (e.g. using a chat app)
    vdisplay("arming callback for channel " + chan_status);
    socket.on(chan_status, function(news_string){
	vdisplay("received on channel " + chan_status + ": " + news_string)
	update_complete_file_from_news(news_string);
	vdisplay("emitting on "+ chan_status + " chunk " + news_string);
	io.emit(chan_status, news_string);
    });
    // this is more crucial, this is how complete status gets transmitted initially
    vdisplay("arming callback for channel " + chan_status_request);
    socket.on(chan_status_request, function(msg){
	display("Received " + msg + " on channel " + chan_status_request);
	emit_file(filename_complete);
    });

    //////////////////// leases
    // it's simpler, we always propagate a complete list of leases
    vdisplay("arming callback for channel " + chan_leases);
    socket.on(chan_leases, function(leases){
	vdisplay("Forwarding leases message " + leases);
	io.emit(chan_leases, leases);
    });

    vdisplay("arming callback for channel " + chan_leases_request);
    socket.on(chan_leases_request, function(anything){
	vdisplay("Forwarding trigger message " + anything);
	io.emit(chan_leases_request, anything);
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
    vdisplay("ENTERING merge with complete = " + complete_infos);
    vdisplay("ENTERING merge with news = " + news_infos);
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
    vdisplay("EXITING merge with complete = " + complete_infos);
    return complete_infos;
}


// utility to open a file and broadcast its contents on chan_status
function emit_file(filename){
    var complete_string = sync_read_file_as_string(filename);
    if (complete_string != "") {
//	vdisplay("emit_file: sending on channel " + chan_status + ":" + complete_string);
	io.emit(chan_status, complete_string);
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
	vdisplay("updating complete file with " + news_infos.length + " news infos");
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
    argv.forEach(function (arg, index, array) {
	console.log("scanning arg " + arg);
	// verbose
	if (arg == "-v")
	    verbose_flag=true;
	// local dev (use json files in .)
	if (arg == "-l") {
	    filename_complete = path.basename(filename_complete);
	    console.log("local mode : using " + filename_complete);
	}
    });
    vdisplay("complete file = " + filename_complete);
}

// run http server
function run_server() {
    process.on('SIGINT', function(){
	display("Received SIGINT - exiting"); process.exit(1);});
    process.on('SIGTERM', function(){
	display("Received SIGTERM - exiting"); process.exit(1);});

    try {
	http.listen(port_number, function(){
	    display('listening on *:' + port_number);
	    display('verbose mode is ' + verbose_flag);
	});
    } catch (err) {
	console.log("Could not run http server on port " + port_number);
	console.run("Need to sudo ?");
    }
}

function main() {
    parse_args();
    run_server();
}

main()
