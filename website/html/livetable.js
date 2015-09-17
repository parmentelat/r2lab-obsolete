////////// must be in sync with r2lab-sidecar.js 
// the 2 socket.io channels that are used
// (1) this is where actual JSON status is sent
var channel = 'r2lab-news';
// (2) this one is used for triggering a broadcast of the complete status
var signalling = 'r2lab-signalling';
// port number
var sidecar_port_number = 8000;


//////////////////////////////
var nb_nodes = 37;

// nodes are dynamic
// their table row and cells get created through d3 enter mechanism
var Node = function (id) {
    this.id = id;
    this.cell_texts = [id,  // id
		 undefined, // avail
		 undefined, // on/off
		 undefined, // ping
		 undefined // os_release
		];
		 
    // node_info is a dict coming through socket.io in JSON
    // simply copy the fieds present in this dict in the local object
    this.update_from_news = function(node_info) {
	// update fields like node.cmc_on_off
	for (var prop in node_info)
	    if (node_info[prop] != undefined)
		this[prop] = node_info[prop];
	// rewrite actual representation in cell_texts 
	// pedestrian for now
	// fill in this.cell_texts that is passed to d3.data for each node
	var col = 2
	this.cell_texts[col++] =
	    this.cmc_on_off == 'fail' ? 'N/A'
	    : this.cmc_on_off == 'on' ? 'ON' : 'OFF';
	this.cell_texts[col++] = this.control_ping == 'on' ? 'PING' : '--';
	this.cell_texts[col++] = this.rewrite_release(this.os_release);
	this.cell_texts[col++] = nice_float(this.wlan0_rx_rate);
	this.cell_texts[col++] = nice_float(this.wlan0_tx_rate);
	this.cell_texts[col++] = nice_float(this.wlan1_rx_rate);
	this.cell_texts[col++] = nice_float(this.wlan1_tx_rate);
	//console.log("after update_from_news -> " + this.data);
    }

    // quick and dirty
    this.rewrite_release = function(os_release) {
	var gr_msg = (os_release.search('gnuradio') >= 0) ? ' + GNURADIO' : '';
	if (os_release.startsWith('fedora'))
	    return 'Fedora' + gr_msg;
	else if (os_release.startsWith('ubuntu'))
	    return 'Ubuntu' + gr_msg;
	else if (os_release == 'other')
	    return 'Other (ssh OK)';
	else
	    return 'N/A';
    }
}

var ident = function(d) { return d; };
var get_node_id = function(node){return node.id;}
var get_node_data = function(node){return node.cell_texts;}
// rewriting info should happen in update_from_news
var get_html = ident;
var nice_float = function(f) {return Number(f).toLocaleString();}

//////////////////////////////
function LiveTable() {

    // not even sure this makes sense
    this.tbody = $("tbody#livetable_container");
    this.nodes = [];
    
    this.init_nodes = function () {
	for (var i=0; i < nb_nodes; i++) { 
	    this.nodes[i] = new Node(i+1);
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
	////////// update existing ones
	cells.html(get_html);
	return;
    }

    ////////// socket.io business
    this.handle_json_status = function(json) {
	try {
	    var nodes_info = JSON.parse(json);
	    // first we write this data into the Node structures
	    for (var i=0; i < nodes_info.length; i++) {
		var node_info = nodes_info[i];
		var id = node_info['id'];
		var node = this.locate_node_by_id(id);
		node.update_from_news(node_info);
	    }
	    this.animate_changes(nodes_info);
	} catch(err) {
	    if (json != "") {
		console.log("Could not parse JSON - ignored :<<" + json + ">>");
		console.log(err);
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
	console.log("Connecting to r2lab status sidecar server at " + url);
	this.sidecar_socket = io(url);
	// what to do when receiving news from sidecar
	var lab=this;
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
