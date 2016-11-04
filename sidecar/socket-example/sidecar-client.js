// the socketio instance
var socket = undefined;

var names = [ 'phones', 'nodes', 'leases'];

//////////////////// global functions
function connect_sidecar(hostname) {
    var url = 'http://'+ hostname + ':443';
    console.log("Connecting to sidecar at " + url);
    socket = io.connect(url);

    names.forEach(function(name) {
	// behaviour for the apply buttons
	$('div#request-' + name + '>button').click(function(e){
	    send(name, 'request:', 'request-');
	});
	$('div#send-' + name + '>button').click(function(e){
	    send(name, 'info:', 'send-');
	});
	// what to do upon reception on that channel
	channel = 'info:' + name;
	console.log("subscribing to channel " + channel)
	socket.on(channel, function(msg){
	    console.log("received on channel " + channel + " : " + msg);
	    update_contents(name, msg)});
    })
}

var set_hostname = function(e) {
    var hostname = $('input#hostname').val();
    if (hostname == "") {
	hostname = "r2lab.inria.fr";
	$('input#hostname').val(hostname);
    }
    connect_sidecar(hostname);
}

var pause = function() {
    console.log("Pausing");
    if (socket == undefined) {
	console.log("already paused");
	return;
    }
    socket.disconnect();
    socket = undefined;
}

//////////////////// the 3 channels
// max number of entries in each section
var depths = []
depths['leases'] = 2;
depths['nodes'] = 10;
depths['phones'] = 2;

// a function to prettify the leases message
var pretty_lease = function(json) {
    console.log("json = " + json);
    var leases = $.parseJSON(json);
    var html = "<ul>";
    leases.forEach(function(lease) {
	var l_html = "<li>";
	l_html += lease['account']['name'] + " from " + lease['valid_from']
	    + " until " + lease['valid_until'];
//	console.log(lease);
	l_html += "</li>";
	html += l_html;
    })
    html += "</ul>";
    return html;
}

var the_record;
// applicable to nodes and phones
var pretty_records = function(json) {
    var records = $.parseJSON(json);
    console.log("records = " + records);
    var html = "<ul>";
    records.forEach(function(record) {
	var li = "<li>" + JSON.stringify(record) + "</li>";
	html += li;
	the_record = record;
    });
    html += "</ul>";
    return html;
}

var prettifiers = []
prettifiers['phones'] = pretty_records;
prettifiers['nodes'] = pretty_records;
prettifiers['leases'] = pretty_lease;

// update the 'contents' <ul> and keep at most <depth> entries in there
function update_contents(name, value) {
    var ul_name = '#ul-' + name;
    var details = value;
    var prettifier = prettifiers[name];
    if (prettifier) details = prettifier(details);
    var html = '<li><span class="date">' + new Date() + '</span>' + details + '</li>';
    var depth = depths[name];
    var current = $(ul_name + '>li').length;
    if (current >= depth) {
	$('#ul-' + name + '>li').first().remove()
    } 
    $('#ul-' + name).append(html);
}

    
var populate = function() {
    names.forEach(function(name) {
	// create form for the request input
	var html;
	html = '<div class="allpage" id="request-' + name + '"><span class="header">send Request ' + name + '</span>' +
	    '<input id="' + name + '"/><button>Request update</button></div>';
	$("#requests").append(html);
	html = '<div class="allpage" id="send-' + name + '"><span class="header">send raw (json) line as ' + name + '</span>' +
	    '<input id="' + name + '"/><button>Send raw line</button></div>';
	$("#requests").append(html);
	// create div for the received contents
	html = '<div class="contents" id=contents-"' + name + '">' +
	    '<h3>Contents of ' + name + '</h3>' +
	    '<ul class="contents" id="ul-' + name + '"></ul>' + '</div>';
	$("#contents").append(html);
    })
    $("div#send-phones>input").val('[{"id":1, "airplane_mode":"on"}]');
    $("div#send-nodes>input").val('[{"id":1, "available":"ko"}]');
    $("div#send-leases>input").val('-- not recommended --');
    $("div#request-phones>input").val('REQUEST');
    $("div#request-nodes>input").val('REQUEST');
    $("div#request-leases>input").val('REQUEST');
};

var clear_contents = function() {
    console.log("Clearing");
    $("div#contents>div.contents>ul").html("")
}	

// channel_prefix is typically 'info:' or 'request:'
// widget_prefix is either 'send-' or 'request-'
function send(name, channel_prefix, widget_prefix) {
    var channel = channel_prefix + name ;
    var value = $('#' + widget_prefix + name + ">input").val();
    console.log("emitting on channel " + channel + " : <" + value + ">");
    socket.emit(channel, value);
    return false;
}
    
////////////////////
var init = function() {
    populate();
    console.log('initing');
    set_hostname();
}
$(init);
