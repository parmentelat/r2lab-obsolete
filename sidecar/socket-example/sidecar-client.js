// the socketio instance
var socket = undefined;

var names = [ 'leases', 'status'];
// max number of entries in each section
var depths = []
depths['leases'] = 2;
depths['status'] = 40;

// a function to prettify the leases message
var pretty_lease = function(json) {
    var js = $.parseJSON(json);
    var leases = js[0]; // not quite sure what this is about
    var html = "<ul>";
    leases.forEach(function(lease) {
	var l_html = "<li>";
	l_html += "(" + lease['status'] + ") ";
	l_html += lease['account']['name'] + " from " + lease['valid_from']
	    + " until " + lease['valid_until'];
//	console.log(lease);
	l_html += "</li>";
	html += l_html;
    })
    html += "</ul>";
    return html;
}

var prettifiers = []
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
	var request_sender_html = '<div class="allpage" id="request-' + name + '"><span class="header">send Request ' + name + '</span>' +
	    '<input id="' + name + '"/><button>Request update</button></div>';
	$("#requests").append(request_sender_html);
	var sender_html = '<div class="allpage" id="send-' + name + '"><span class="header">send raw (json) line as ' + name + '</span>' +
	    '<input id="' + name + '"/><button>Send raw line</button></div>';
	$("#requests").append(sender_html);
	// create div for the received contents
	var contents_html = '<div class="contents" id=contents-"' + name + '">' +
	    '<h3>Contents of ' + name + '</h3>' +
	    '<ul class="contents" id="ul-' + name + '"></ul>' + '</div>';
	$("#contents").append(contents_html);
    })
    $("div#send-status>input").val('{["id":1, "available":"ko"]}');
    $("div#send-leases>input").val('-- not recommended --');
    $("div#request-status>input").val('REQUEST');
    $("div#request-leases>input").val('REQUEST');
};

function send(name, prefix, suffix) {
    var channel = 'chan-' + name + suffix ;
    var value = $('#' + prefix + name + ">input").val();
    console.log("emitting on channel " + channel + " : <" + value + ">");
    socket.emit(channel, value);
    return false;
}
    

function connect_sidecar(hostname) {
    var url = 'http://'+ hostname + ':443';
    console.log('connecting to sidecar at ' + url);
    socket = io.connect(url);

    names.forEach(function(name) {
	// behaviour for the apply buttons
	$('div#request-' + name + '>button').click(function(e){
	    send(name, 'request-', '-request');
	});
	$('div#send-' + name + '>button').click(function(e){
	    send(name, 'send-', '');
	});
	// what to do upon reception on that channel
	socket.on('chan-' + name, function(msg){
//	    console.log("received on channel chan-" + name + " : " + msg);
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

var init = function() {
    populate();
    console.log('initing');
    set_hostname();
}
$(init);
			   
//  $('#form-status').submit(function(){
//    socket.emit('chan-status', $('#status').val());
///*    $('#status').val(''); */
//    return false;
//  });
//  $('#form-leases').submit(function(){
//    socket.emit('chan-leases', $('#leases').val());
///*    $('#leases').val('');*/
//    return false;
//  });
//  $('#form-leases-request').submit(function(){
//    socket.emit('chan-leases-request', $('#leases-request').val());
///*    $('#leases-request').val('');*/
//    return false;
//  });
//  socket.on('chan-leases', function(msg){
//    $('#messages').append($('<li>').text('leases: ' + msg));});
//  socket.on('chan-leases-request', function(msg){
//    $('#messages').append($('<li>').text('leases-request: ' + msg));});
//</script>
//  </body>
//</html>
//-->

