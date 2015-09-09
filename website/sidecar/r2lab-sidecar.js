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

var debug=false;

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
// throw exception in case of problem
function read_file_as_string(filename, callback){
    if (debug) console.log("Reading file " + filename);
    fs.readFile(filename,
		'utf8',
		function(err, string){
		    if (err) throw err;
		    callback(string);
		});
}

// same but synchroneous
function sync_read_file_as_string(filename){
    try{
	if (debug) console.log("sync Reading file " + filename);
	return fs.readFileSync(filename, 'utf8');
    } catch(err){
	console.log("Could not sync read " + filename + err);
    }
}

// convenience function to save a JS record into a file
function save_records_in_file(filename, records){
    fs.writeFile(filename, record,
		 'utf8',
		 function(err){
		     if (debug) console.log("(Over)wrote file " + filename);
		 });
}

function sync_save_records_in_file(filename, records){
    try{
	fs.writeFileSync(filename, JSON.stringify(records), 'utf8');
	if (debug) console.log("sync (Over)wrote " + filename)
    } catch(err) {
	console.log("Could not sync write " + filename + err);
    }
    
}    
    
// merge news record into complete record; return new complete
function merge_news_into_complete(complete, news_infos){
    for (var nav=0; nav < news_infos.length; nav++) {
	var node_info = news_infos[nav];
	var id = node_info.id;
	for (var nav2=0; nav2 < complete.length; nav2++) {
	    var complete_info = complete[nav2];
	    if (complete_info['id'] == id) {
		// found the place where to update complete
		// xxx this is a cut-n-paste from livemap.js, should be refactored
		if (node_info.cmc_on_off != undefined)
		    complete_info.cmc_on_off = node_info.cmc_on_off;
		if (node_info.control_ping != undefined)
		    complete_info.control_ping = node_info.control_ping;
		if (node_info.os_release != undefined)
		    complete_info.os_release = node_info.os_release;
		// these 2 are not sniffed yet
		if (node_info.data_ping != undefined)
		    complete_info.data_ping = node_info.data_ping;
		if (node_info.control_ssh != undefined)
		    complete_info.control_ssh = node_info.control_ssh;
		// we're done, skip rest of search in complete
		break;
	    }
	}
    }
    return complete;
}
		

// utility to open a file and broadcast its contents on channel_news
function emit_file(filename){
    var emit_callback = function(string){
	if (debug) console.log("emitting on channel " + channel_news + ":" + string);
	io.emit(channel_news, string);
    };
    try {
	read_file_as_string(filename, emit_callback);
    } 
    catch(err){
	console.log("Error when emitting file " + filename);
    }
}


// convenience function to
// (*) open and read r2lab-complete
// (*) merge news dictionary
// (*) save result in r2lab-complete
function update_complete_file(news_infos){
    var callback = function(complete_string){
	var complete_records = JSON.parse(complete_string);
	var news_string = sync_read_file_as_string(filename_news);
	var news_records = JSON.parse(news_string);
	complete_records = merge_news_into_complete(complete_records, news_records);
	sync_save_records_in_file(filename_complete, complete_records);
	if (debug) console.log(new Date() + " merged -> " + JSON.stringify(complete_records));
    }
    read_file_as_string(filename_complete, callback);
}

// watch complete status file: set callback
fs.watch(filename_news, 
	 function(event, filename){
	     if (debug) console.log("watch -> event=" + event);
	     // update complete from news
	     read_file_as_string(filename_news,
				 update_complete_file);
	     // xxx mmh, this should probably be specified as a callback
	     // and not called synchroneously like this
	     emit_file(filename_news);
	 });

// run http server
http.listen(port_number, function(){
    console.log('listening on *:' + port_number);
});
