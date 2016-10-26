#!/usr/bin/env node

//// oct. 2016
// major changes in channels naming scheme
// with the addition of the 'phones' channels
// see AA-overview.md for detail
//
// another major change is about sidecar only sending along CHANGES
// as compared to its current known state

// dependencies
var express_app = require('express')();
var http = require('http').Server(express_app);
var io = require('socket.io')(http);
var fs = require('fs');
var path = require('path');

//////// names for the channels used are
// info:nodes
// request:nodes
// info:phones
// request:phones
// info:leases
// request:leases

// filenames used for persistent channels : essentially for smooth restart
// /var/lib/sidecar/nodes.json
// /var/lib/sidecar/phones.json
// it is fine to delete, it will just take some while to rebuild itself
// from the outcome of monitor
// in local mode (for devel) these files are in current directory


// in the following, name = 'nodes' or 'phones' or 'leases' 
function info_channel_name(name) {
    return "info:" + name;
}
function request_channel_name(name) {
    return "request:" + name;
}
function db_filename(name) {
    if (! local_flag) {
	return "/var/lib/sidecar/" + name + ".json";
    } else {
	return "./" + name + ".json";
    }
}
	
//////////
var port_number = 443;

// use -v to turn on
var verbose_flag = false;
// use -l to turn on
var local_flag = false;

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

// when receiving something on a status channel (that is, either nodes or phones), we
// * update nodes.json (i.e, read the file, apply changes, store again)
// * and forward the news as-is
// NOTE that this can also be used for debugging / tuning
// by sending JSON messages manually (e.g. using a chat app)
//
// this code is common to the 2 channels associated
// to persistent data (nodes and phones)
function prepare_persistent_channel(socket, name) {
    var info_channel = info_channel_name(name);
    var filename = db_filename(name);
    vdisplay("arming callback for channel " + info_channel);
    socket.on(info_channel, function(news_string){
	vdisplay("received on channel " + info_channel + " chunk " + news_string)
	update_complete_file_from_news(filename, news_string);
	vdisplay("emitting on "+ info_channel + " chunk " + news_string);
	io.emit(info_channel, news_string);
    });
    // this now is how complete status gets transmitted initially
    var request_channel = request_channel_name(name);
    vdisplay("arming callback for channel " + request_channel);
    socket.on(request_channel, function(msg){
	display("Received " + msg + " on channel " + request_channel);
	emit_file(filename, info_channel);
    });
}

// non-persistent channels are simpler,
// e.g. we always propagate a complete list of leases
function prepare_non_persistent_channel(socket, name) {
    var info_channel = info_channel_name(name);
    vdisplay("arming callback for channel " + info_channel);
    socket.on(info_channel, function(infos){
	vdisplay("Forwarding on non-persistent channel " + info_channel);
	io.emit(info_channel, infos);
    });

    var request_channel = request_channel_name(name);
    vdisplay("arming callback for channel " + request_channel);
    socket.on(request_channel, function(anything) {
	display("Forwarding trigger message " + anything + " on channel "+ request_channel);
	io.emit(request_channel, anything);
    });
    
}

// arm callbacks for the channels we use
io.on('connection', function(socket){
    //////////////////// (nodes) status
    prepare_persistent_channel(socket, 'nodes');

    //////////////////// phones
    prepare_persistent_channel(socket, 'phones');

    //////////////////// leases
    prepare_non_persistent_channel(socket, 'leases');

});

// convenience function to synchroneously read a file as a string
function sync_read_file_as_string(filename){
    try {
	var contents = fs.readFileSync(filename, 'utf8');
	vdisplay("sync read (1) " + filename + " -> " + contents);
	if (! contents) {
	    display(filename + ": WARNING, could not read");
	    // artificially return an empty list
	    return "[]";
	} else {
	    return contents;
	}
    } catch(err){
	display(filename + ": could not read - " + err);
	return "[]";
    }
}

// same but do JSON.parse on result
function sync_read_file_as_infos(filename) {
    try {
	return JSON.parse(sync_read_file_as_string(filename));
    } catch(err) {
	display(filename + ": could not parse JSON - " + err);
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
	display(filename + ": could not sync write - " + err);
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
    if (complete_string) {
	vdisplay("emit_file: sending on channel " + channel + ":" + complete_string);
	io.emit(channel, complete_string);
    } else {
	display("OOPS - empty contents in " + filename)
    }
}

// convenience function to
// (*) open and read the complete status file - e.g. nodes.json
// (*) merge new info into that dictionary
// (*) save result in same file
// (*) return the dictionaries to be sent as news
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
	    verbose_flag = true;
	// local dev (use json files in .)
	if (arg == "-l") {
	    local_flag = true;
	}
    });
    vdisplay("complete file for nodes = " + db_filename('node'));
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
