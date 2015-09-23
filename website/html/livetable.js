////////// must be in sync with r2lab-sidecar.js 
// the 2 socket.io channels that are used
// (1) this is where actual JSON status is sent
var channel = 'r2lab-news';
// (2) this one is used for triggering a broadcast of the complete status
var signalling = 'r2lab-signalling';
// port number
var sidecar_port_number = 443;


var fedora_badge = '<img src="fedora-logo.png">';
var ubuntu_badge = '<img src="ubuntu-logo.png">';

var show_rxtx_rates = false;

//////////////////////////////
var nb_nodes = 37;

// nodes are dynamic
// their table row and cells get created through d3 enter mechanism
var TableNode = function (id) {
    this.id = id;
    this.cells_data = [
	[ id, 'id' ] ,  // id
	undefined, // avail
	undefined, // on/off
	undefined, // ping
	undefined // os_release
    ];
		 
    this.update_from_news = function(node_info) {
	// node_info is a dict coming through socket.io in JSON
	// simply copy the fieds present in this dict in the local object
	for (var prop in node_info)
	    if (node_info[prop] != undefined)
		this[prop] = node_info[prop];
	// then rewrite actual representation in cells_data
	// that will contain a list of ( html_text, class )
	// used by the d3 mechanism to update the <td> elements in the row
	var col = 1
	// available
	this.cells_data[col++] =
	    (this.available == 'ko') ?
	    [ 'Out of order', 'ko' ] : [ 'Good to go', 'ok' ];
	// 
	this.cells_data[col++] =
	    this.cmc_on_off == 'fail' ? [ 'N/A', 'ko' ]
	    : this.cmc_on_off == 'on' ? [ 'ON', 'ok' ]
	    : [ 'OFF', 'ko' ];
	this.cells_data[col++] = this.control_ping == 'on'
	    ? [ 'PING', 'ok' ]
	    : [ '--', 'ko' ];
	this.cells_data[col++] = this.release_cell(this.os_release);
	// optional
	if (show_rxtx_rates) {
	    this.cells_data[col++] = float_cell(this.wlan0_rx_rate);
	    this.cells_data[col++] = float_cell(this.wlan0_tx_rate);
	    this.cells_data[col++] = float_cell(this.wlan1_rx_rate);
	    this.cells_data[col++] = float_cell(this.wlan1_tx_rate);
	}
	//console.log("after update_from_news -> " + this.data);
    }

    this.release_cell = function(os_release) {
	// use a single css class for now
	var klass = 'os-release';
	if (os_release == undefined)
	    return [ "n/a", klass ];
	var gr_msg = (os_release.search('gnuradio') >= 0) ? ' + GNURADIO' : '';
	if (os_release.startsWith('fedora'))
	    return [ fedora_badge + gr_msg, klass ];
	else if (os_release.startsWith('ubuntu'))
	    return [ ubuntu_badge + gr_msg, klass ];
	else if (os_release == 'other')
	    return [ 'Other (ssh OK)', klass ];
	else
	    return [ 'N/A', klass ];
    }
}

var ident = function(d) { return d; };
var get_node_id = function(node){return node.id;}
var get_node_data = function(node){return node.cells_data;}
// rewriting info should happen in update_from_news
var get_html = function(tuple) {return tuple[0];}
var get_class = function(tuple) {return tuple[1];}
var float_cell = function(f) {return [ Number(f).toLocaleString(), undefined ];}

//////////////////////////////
function LiveTable() {

    // not even sure this makes sense
    this.tbody = $("tbody#livetable_container");
    this.nodes = [];
    
    this.init_nodes = function () {
	for (var i=0; i < nb_nodes; i++) { 
	    this.nodes[i] = new TableNode(i+1);
	}
    }

    this.locate_node_by_id = function(id) {
	return this.nodes[id-1];
    }
    
    this.animate_changes = function(nodes_info) {
	var tbody = d3.select("tbody#livetable_container");
	// row update selection
	var rows = tbody.selectAll('tr')
	    .data(this.nodes, get_node_id);
	////////// create rows as needed
	rows.enter()
	    .append('tr');
	// this is a nested selection like in http://bost.ocks.org/mike/nest/
	var cells = rows.selectAll('td')
	    .data(get_node_data);
	cells.enter()
	    .append('td');
	////////// update existing ones from cells_data
	cells.html(get_html)
	    .attr('class', get_class)
	return;
    }

    ////////// socket.io business
    this.handle_json_status = function(json) {
	try {
	    var nodes_info = JSON.parse(json);
	    // first we write this data into the TableNode structures
	    for (var i=0; i < nodes_info.length; i++) {
		var node_info = nodes_info[i];
		var id = node_info['id'];
		var node = this.locate_node_by_id(id);
		node.update_from_news(node_info);
	    }
	    this.animate_changes(nodes_info);
	} catch(err) {
	    if (json != "") {
//	    console.log("Could not apply news - ignored  - JSON=<<" + json + ">>");
	    console.log("Could not apply news - ignored  - JSON has " + json.length + " chars");
	    console.log(err.stack);
	    }
	}
    }

    this.init_sidecar_socket_io = function() {
	// try to figure hostname to get in touch with
	var sidecar_hostname = ""
	sidecar_hostname = new URL(window.location.href).hostname;
	if ( ! sidecar_hostname)
	    sidecar_hostname = 'localhost';
	var url = "http://" + sidecar_hostname + ":" + sidecar_port_number;
	console.log("livetable is connecting to sidecar server at " + url);
	this.sidecar_socket = io(url);
	// what to do when receiving news from sidecar
	var lab = this;
	this.sidecar_socket.on(channel, function(json){
            lab.handle_json_status(json);
	});
	this.request_complete_from_sidecar();
    }

    // request sidecar for initial status on the signalling channel
    // content is not actually used by sidecar server
    // could maybe send some client id instead
    this.request_complete_from_sidecar = function() {
	this.sidecar_socket.emit(signalling, 'INIT');
    }

}

// autoload
$(function() {
    the_livetable = new LiveTable();
    the_livetable.init_nodes();
    the_livetable.init_sidecar_socket_io();
})
