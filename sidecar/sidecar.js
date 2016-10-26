#!/usr/bin/env node

//// oct. 2016
// major changes in channels naming scheme
// with the addition of the 'phones' channels
// see AA-overview.md for detail

// dependencies
var express_app = require('express')();
var http = require('http').Server(express_app);
var io = require('socket.io')(http);
var fs = require('fs');
var path = require('path');

//////// names for the channels used

//// (nodes) status
// (*) sending deltas; actual json is flying on this channel
var chan_nodes = 'info:nodes';
// (*) requesting a whole (nodes) status; anything arriving
// on this channel causes a full status to be sent on info:nodes
var chan_nodes_request = 'request:nodes';
// (*) the place where the current status is stored 
// essentially for smooth restart
// it is fine to delete, it will just take some while to rebuild itself
// from the outcome of monitor
var filename_status = '/var/lib/sidecar/nodes.json';


//// phones status
// 2 channels and one filename, like for nodes
var chan_phones = 'info:phones';
var chan_phones_request = 'request:phones';
var filename_phones = '/var/lib/sidecar/phones.json';


//// leases
// 2 channels like for nodes and phones
// in practical terms, a new request to publish leases
// will trigger an event sent back to the monitor,
// asking it to short-circuit its loop and to immediately refresh leases
// so leases are different in the sense that we don't keep anything locally
var chan_leases = 'info:leases';
var chan_leases_request = 'request:leases';

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

// we don't honour anymore GET requests on /

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
    //////////////////// (nodes) status
    // when receiving something on a status channel (that is, either nodes or phones), we
    // * update nodes.json (i.e, read the file, apply changes, store again)
    // * and forward the news as-is
    // NOTE that this can also be used for debugging / tuning
    // by sending JSON messages manually (e.g. using a chat app)
    vdisplay("arming callback for channel " + chan_nodes);
    socket.on(chan_nodes, function(news_string){
	vdisplay("received on channel " + chan_nodes + ": " + news_string)
	update_complete_file_from_news(filename_status, news_string);
	vdisplay("emitting on "+ chan_nodes + " chunk " + news_string);
	io.emit(chan_nodes, news_string);
    });
    // this now is how complete status gets transmitted initially
    vdisplay("arming callback for channel " + chan_nodes_request);
    socket.on(chan_nodes_request, function(msg){
	display("Received " + msg + " on channel " + chan_nodes_request);
	emit_file(filename_status, chan_nodes);
    });

    //////////////////// phones
    vdisplay("arming callback for channel " + chan_phones);
    socket.on(chan_phones, function(news_string){
	vdisplay("received on channel " + chan_phones + ": " + news_string)
	update_complete_file_from_news(filename_phones, news_string);
	vdisplay("emitting on "+ chan_phones + " chunk " + news_string);
	io.emit(chan_phones, news_string);
    });
    // this now is how complete phones gets transmitted initially
    vdisplay("arming callback for channel " + chan_phones_request);
    socket.on(chan_phones_request, function(msg){
	display("Received " + msg + " on channel " + chan_phones_request);
	emit_file(filename_phones, chan_phones);
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
	display("Forwarding trigger message " + anything + " on channel "+ chan_leases_request);
	io.emit(chan_leases_request, anything);
    });

});

// convenience function to synchroneously read a file as a string
// xxx hack - sometimes (quite often indeed) we see
// this read returning an empty string...
// apparently when watching a file we get to it too fast, so
// allow for 2 attempts
function sync_read_file_as_string(filename, verbose){
    try {
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
	// return an empty list in this case
	// useful for when the file does not exist yet
	// a little hacky as this assumes all our files contain JSON lists
	return [];
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


// utility to open a file and broadcast its contents on channel
function emit_file(filename, channel){
    var complete_string = sync_read_file_as_string(filename);
    if (complete_string != "") {
	vdisplay("emit_file: sending on channel " + channel + ":" + complete_string);
	io.emit(channel, complete_string);
    } else {
	display("OOPS - empty contents in " + filename)
    }
}


// convenience function to
// (*) open and read r2lab-complete
// (*) merge news dictionary
// (*) save result in r2lab-complete
function update_complete_file_from_news(filename, news_string){
    if (news_string == "") {
	display("OOPS - empty news feed - ignored");
	return;
    }
    try {
	// start from the complete infos
	var complete_infos = sync_read_file_as_infos(filename);
	// convert string into infos
	var news_infos = JSON.parse(news_string);
	vdisplay("updating complete file with " + news_infos.length + " news infos");
	// merge both
	complete_infos = merge_news_into_complete(complete_infos, news_infos);
//	vdisplay("merged news : " + JSON.stringify(news_infos));
	// save result
	sync_save_infos_in_file(filename, complete_infos);
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
	    filename_status = path.basename(filename_status);
	    console.log("local mode : using " + filename_status);
	    filename_phones = path.basename(filename_phones);
	    console.log("local mode : using " + filename_phones);
	}
    });
    vdisplay("complete file = " + filename_status);
    vdisplay("complete file = " + filename_phones);
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
