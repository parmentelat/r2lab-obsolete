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
var default_port_number = 999;
var global_port_number = undefined;

// use -v to turn on
var verbose_flag = false;
// use -l to turn on
var local_flag = false;
// default is to be incremental - i.e. emit only differences
// use -c (--complete) to go back to the mode where the complete
// news string gets emitted
var incremental_flag = true;

// always display
function display(args) {
    for (var i in arguments) {
       console.log(new Date() + " sidecar " + arguments[i]);
    }
}
// display only if in verbose mode
function vdisplay(args) {
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

// this code is common to the 2 channels associated
// to persistent data (nodes and phones)
// when receiving something on a status channel (that is, either nodes or phones), we
// * update nodes.json (i.e, read the file, apply changes, store again)
// * and then, according to incremental_mode, we:
//   * either forward the news as-is if incremental_mode is off
//   * or forward the smallest delta that describes the changes if it is on
function prepare_persistent_channel(socket, name) {
    var info_channel = info_channel_name(name);
    var filename = db_filename(name);
    vdisplay("arming callback for channel " + info_channel);
    socket.on(info_channel, function(news_string) {
	vdisplay("received on channel " + info_channel + " chunk " + news_string)
	infos_to_emit = update_dbfile_from_news(filename, news_string, incremental_flag);
	// avoid the noise of sending empty news
	if (infos_to_emit.length >= 1) {
	    string_to_emit = JSON.stringify(infos_to_emit);
	    vdisplay("emitting on "+ info_channel + " chunk " + string_to_emit);
	    io.emit(info_channel, string_to_emit);
	} else {
	    vdisplay("no news found in news_string (was "
		     + news_string.length + " chars long)");
	}
    });
    // this now is how complete status gets transmitted initially
    var request_channel = request_channel_name(name);
    vdisplay("arming callback for channel " + request_channel);
    socket.on(request_channel, function(msg) {
	display("Received " + msg + " on channel " + request_channel);
	// feature : if we can find 'CLEAR' in the text, we clear our own db
	if (msg.indexOf('CLEAR') != -1) {
	    clean_dbfile(filename);
	} 
	emit_file(filename, info_channel);
    });
}

function clean_dbfile(filename) {
    sync_save_dbfile(filename, []);
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
	vdisplay("sync read " + filename + " -> " + contents.length + " chars");
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

// utility to open a file and broadcast its contents on channel
function emit_file(filename, channel){
    var complete_string = sync_read_file_as_string(filename);
    if (complete_string) {
	//vdisplay("emit_file: sending on channel " + channel + ":" + complete_string);
	vdisplay("emit_file: sending on channel " + channel + ":" + complete_string.length + " chars");
	io.emit(channel, complete_string);
    } else {
	display("OOPS - not emitting - empty contents found in " + filename)
    }
}

// convenience function to save a list of JS infos (records) into a file
// we do everything synchroneously to avoid trouble
function sync_save_dbfile(filename, infos){
    try {
	var contents = JSON.stringify(infos);
	fs.writeFileSync(filename, contents, 'utf8');
	vdisplay("sync (over)wrote " + contents.length + " on " + filename)
    } catch(err) {
	display(filename + ": could not sync write " + filename + " - " + err);
    }
}

// convenience function to
// (*) open and read the complete status file - e.g. nodes.json
// (*) merge new info into that dictionary
// (*) save result in same file
// (*) return object is the infos to be broadcasted
//   (*) if incremental_mode == false (traditional mode)
//       this is essentially (the infos for) news_string as-is
//   (*) if incremental_mode == true,
//       only the changes to the db are reported
function update_dbfile_from_news(filename, news_string, incremental_mode) {
    if (news_string == "") {
	display("OOPS - empty news feed - ignoring");
	return [];
    }
    try {
	// start from the complete infos
	var complete_infos = sync_read_file_as_infos(filename);
	// convert string into infos
	var news_infos = JSON.parse(news_string);
	vdisplay("updating dbfile with " + news_infos.length + " news infos");
	// merge both and save in file
	delta_infos = merge_news_into_complete(complete_infos, news_infos, filename);
	// xxx
	return incremental_mode ? delta_infos : news_infos;
    } catch(err) {
	display(" OOPS - unexpected exception in update_dbfile_from_news",
		"news_string was " + news_string,
		"strack trace is " + err.stack);
	return [];
    }
}

// merge news info into complete infos
// save complete infos if filename is provided
// return delta_infos, the smallest set of infos
// that describe the changes from previous db state
function merge_news_into_complete(complete_infos, news_infos, filename) {
    var delta_infos = [];
    news_infos.forEach(function(news_info) {
	var id = news_info.id;
	var item_already_present_in_db = false;
	complete_infos.forEach(function(complete_info) {
	    // search for corresponding item in complete db
	    if (complete_info['id'] == id) {
		item_already_present_in_db = true;
		items_has_changes = false;
		var delta_info;
		// copy all contents from news_info into complete_infos
		for (var prop in news_info) {
		    // do we have change for that node x prop
		    if ( (news_info[prop] != undefined) &&
			 (complete_info[prop] != news_info[prop]) ) {
			// is this the first change detected for that node
			if ( ! items_has_changes) {
			    items_has_changes = true;
			    delta_info = { 'id' : id };
			    delta_infos.push(delta_info);
			}
			// check if we need to create a delta_info 
			complete_info[prop] = news_info[prop];
			delta_info[prop] = news_info[prop];
		    }
		}
		// we're done searching for this item
		// skip rest of search in complete_infos
		return;
	    }
	})
	// complete gets created empty at the very beginning
	// so, if id is not yet known, add it as-is
	if (! item_already_present_in_db) {
	    complete_infos.push(news_info);
	    delta_infos.push(news_info);
	}
    })
    if (filename) {
	sync_save_dbfile(filename, complete_infos);
    }

    return delta_infos;
}

////////////////////////////////////////
var usage = "Usage: sidecar.js [-v] [-l] [-c] [-p port-number] \n\
  -v: verbose mode \n\
  -l: local mode for devel (create local logfile) \n\
  -c: incremental mode (only publish differences instead of flooding with the whole data) \n\
  -p: set port number - default is " + default_port_number + "\n";  

function parse_args() {
    // very rough parsing of command line args - to set verbosity
    var argv = process.argv.slice(2);
    for (var index=0; index < argv.length; index++) {
	var arg = argv[index];
	if (arg == "-h") {
	    console.log(usage);
	    process.exit(1);
	// verbose
	} else if (arg == "-v") {
	    verbose_flag = true;
	// local dev (use json files in .)
	} else if (arg == "-l") {
	    local_flag = true;
	} else if (arg == "-c") {
	    incremental_flag = false;
	} else if (arg == "-p") {
	    global_port_number = parseInt(argv[index+1]);
	    index ++;
	}
    };
    vdisplay("complete file for nodes = " + db_filename('node'));
}

// run http server
function run_server() {
    process.on('SIGINT', function(){
	display("Received SIGINT - exiting"); process.exit(1);});
    process.on('SIGTERM', function(){
	display("Received SIGTERM - exiting"); process.exit(1);});

    if (global_port_number == undefined)
	global_port_number = default_port_number;

    try {
	http.listen(global_port_number, function(){
	    display('listening on *:' + global_port_number);
	    display('verbose flag is ' + verbose_flag);
	    display('local flag is ' + local_flag);
	    display('incremental mode is ' + incremental_flag);
	});
    } catch (err) {
	console.log("Could not run http server on port " + global_port_number);
	console.run("Need to sudo ?");
    }
}

function main() {
    parse_args();
    run_server();
}

main()
