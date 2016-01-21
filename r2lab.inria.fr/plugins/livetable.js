////////// must be in sync with r2lab-sidecar.js 
// the 2 socket.io channels that are used
// (1) this is where actual JSON status is sent
var channel = 'r2lab-news';
// (2) this one is used for triggering a broadcast of the complete status
var signalling = 'r2lab-signalling';
// port number
var sidecar_port_number = 443;


var fedora_badge = '<img src="assets/img/fedora-logo.png">';
var ubuntu_badge = '<img src="assets/img/ubuntu-logo.png">';
var gnuradio_badge = '<img src="assets/img/gnuradio-logo.png">';
var other_badge = '<img src="assets/img/other-logo.png">';

// ready to fly as soon as the data comes in from monitor
var livetable_show_rxtx_rates = false;


// quick'n dirty helper to create <span> tags inside the <td>
// d3 should allow us to do that more nicely but I could not figure it out yet
function span_html(text, klass) {
    var res = "<span";
    if (klass) res += " class='" + klass + "'";
    res += '>';
    res += text;
    res += "</span>";
    return res;
}
//////////////////////////////
var nb_nodes = 37;

// nodes are dynamic
// their table row and cells get created through d3 enter mechanism
var TableNode = function (id) {
    this.id = id;
    this.cells_data = [
	[ span_html(id, 'badge'), '' ],  // id 
	undefined,			// avail
	undefined,			// on/off
	undefined,			// ping
	undefined,			// ssh
	undefined			// os_release
    ];
		 
    this.is_alive = function() {
	return this.cmc_on_off == 'on'
	    && this.control_ping == 'on'
	    && this.control_ssh == 'on'
	    && this.available != 'ko';
    }

    // node_info is a dict coming through socket.io in JSON
    // simply copy the fieds present in this dict in the local object
    // for further usage in animate_changes
    // don't bother if no change is detected
    this.update_from_news = function(node_info) {
	var modified = false;
	for (var prop in node_info)
	    if (node_info[prop] != this[prop]) {
		this[prop] = node_info[prop];
		modified = true;
	    }
	if (! modified) return;
	// then rewrite actual representation in cells_data
	// that will contain a list of ( html_text, class )
	// used by the d3 mechanism to update the <td> elements in the row
	var col = 1
	// available
	this.cells_data[col++] =
	    (this.available == 'ko') ?
	    [ 'Out of order', 'error' ] : [ 'Good to go', 'ok' ];
	// 
	this.cells_data[col++] =
	    this.cmc_on_off == 'fail' ? [ 'N/A', 'error' ]
	    : this.cmc_on_off == 'on' ? [ span_html('', 'fa fa-toggle-on'), 'ok' ]
	    : [ span_html('', 'fa fa-toggle-off'), 'ko' ];
	this.cells_data[col++] =
	    this.control_ping == 'on' ? [ span_html('', 'fa fa-link'), 'ok' ]
	    : [ span_html('', 'fa fa-unlink'), 'ko' ];
	this.cells_data[col++] =
	    this.control_ssh == 'on' ? [ span_html('', 'fa fa-circle'), 'ok' ]
	    : [ span_html('', 'fa fa-circle-o'), 'ko' ];
	this.cells_data[col++] = this.release_cell(this.os_release);
	// optional
	if (livetable_show_rxtx_rates) {
	    var alive = this.is_alive();
	    this.cells_data[col++] = this.rxtx_cell(this.wlan0_rx_rate);
	    this.cells_data[col++] = this.rxtx_cell(this.wlan0_tx_rate);
	    this.cells_data[col++] = this.rxtx_cell(this.wlan1_rx_rate);
	    this.cells_data[col++] = this.rxtx_cell(this.wlan1_tx_rate);
	}
	//console.log("after update_from_news -> " + this.data);
    }

    this.release_cell = function(os_release) {
	// use a single css class for now
	var klass = 'os';
	if (os_release == undefined)
	    return [ "n/a", klass ];
	var gr_badge = (os_release.search('gnuradio') >= 0) ? gnuradio_badge : '';
	if (os_release.startsWith('fedora'))
	    return [ fedora_badge + ' ' + os_release + ' ' + gr_badge, klass ];
	else if (os_release.startsWith('ubuntu'))
	    return [ ubuntu_badge + ' ' + os_release + ' ' + gr_badge, klass ];
	else if (os_release == 'other')
	    return [ other_badge + ' (ssh OK)', klass ];
	else
	    return [ 'N/A', klass ];
    }

    // raw data is bits/s
    this.rxtx_cell = function(value) {
	var klass = 'rxtx';
	if ((value == undefined) || (! this.is_alive()))
	    return ["-", klass] ;
	// we need to format this into kbps, Mbps, etc..
	var raw = Number(value);
	var number, unit;
	if (raw/1000 < 1.) {
	    number = raw;
	    unit = "bps";
	} else if ((raw/1000000) < 1.) {
	    number = raw/1000;
	    unit = "kbps";
	} else {
	    number = raw/1000000;
	    unit = "Mbps";
	}
	var nice = number.toLocaleString() + " " + unit;
	return [ nice, klass ];
    }

    this.set_display = function(display) {
	var selector = '#livetable_container #row'+this.id;
	display ? $(selector).show() : $(selector).hide();
    }

}

var ident = function(d) { return d; };
var get_node_id = function(node){return node.id;}
var get_node_data = function(node){return node.cells_data;}
// rewriting info should happen in update_from_news
var get_html = function(tuple) {return tuple[0];}
var get_class = function(tuple) {return tuple[1];}

//////////////////////////////
function LiveTable() {

    this.nodes = [];
    
    this.init = function() {
	this.init_dom();
	this.init_nodes();
	this.init_sidecar_socket_io();
    }

    this.init_dom = function () {
	var containers = d3.selectAll('#livetable_container');
	var head = containers.append('thead').attr('class', 'livetable_header');
	var body = containers.append('tbody').attr('class', 'livetable_body');
	var foot = containers.append('tfoot').attr('class', 'livetable_header');

	var self = this;
	var header_rows = d3.selectAll('.livetable_header').append('tr')
	    .attr('class', 'all')
	    .on('click', function(){self.toggle_view_mode();})
	;
	header_rows.append('th').html('#');
	header_rows.append('th').html('Availability');
	header_rows.append('th').html('On/Off');
	header_rows.append('th').html('Ping');
	header_rows.append('th').html('Ssh');
	header_rows.append('th').html('Last O.S.');
	if (livetable_show_rxtx_rates) {
	    header_rows.append('th').html('wlan0-rx').attr('class','rxtx');
	    header_rows.append('th').html('wlan0-tx').attr('class','rxtx');
	    header_rows.append('th').html('wlan1-rx').attr('class','rxtx');
	    header_rows.append('th').html('wlan1-tx').attr('class','rxtx');
	}
	
    }

    this.init_nodes = function () {
	for (var i=0; i < nb_nodes; i++) { 
	    this.nodes[i] = new TableNode(i+1);
	}
    }

    this.locate_node_by_id = function(id) {
	return this.nodes[id-1];
    }
    
    /* mode is either 'all' or 'alive' */
    this.view_mode = 'all';
    this.toggle_view_mode = function () {
	this.view_mode = (this.view_mode == 'all') ? 'alive' : 'all';
	this.display_nodes(this.view_mode);
	$(".livetable_header tr").toggleClass('all');
    }
    this.display_nodes = function(mode) {
	for (var i in this.nodes) {
	    var node=this.nodes[i];
	    var display = (mode=='all') ? true : (node.is_alive());
	    node.set_display(display);
	}
    }

    this.animate_changes = function(nodes_info) {
	var tbody = d3.select("tbody.livetable_body");
	// row update selection
	var rows = tbody.selectAll('tr')
	    .data(this.nodes, get_node_id);
	////////// create rows as needed
	rows.enter()
	    .append('tr')
	    .attr('id', function(node){ return 'row'+node.id;})
	;
	// this is a nested selection like in http://bost.ocks.org/mike/nest/
	var cells = rows.selectAll('td')
	    .data(get_node_data);
	// in this context d is the 'datum' attached to a <td> which
	// however this will be the DOM element
	cells.enter()
	    .append('td')
	// attach a click event on the first column only
	    .each(function(d, i) {
		if (i==0) {
		    // I'm using DOM/jquery here because the datum d here
		    //  is a tuple (html,class) so this is useless
		    $(this).click(function() {
			$(this).parent().attr('style', 'display:none');
		    })
		}
	    })
	;
	////////// update existing ones from cells_data
	cells.html(get_html)
	    .attr('class', get_class)
	return;
    }

    ////////// socket.io business
    this.handle_json_status = function(json) {
	try {
	    var node_infos = JSON.parse(json);
//	    console.log("handle_json_status - incoming " + node_infos.length + " node infos");
	    // first we write this data into the TableNode structures
	    for (var i=0; i < node_infos.length; i++) {
		var node_info = node_infos[i];
		var id = node_info['id'];
		var node = this.locate_node_by_id(id);
		if (node != undefined)
		    node.update_from_news(node_info);
		else
		    console.log("livetable: could not locate node id " + id + " - ignored");
	    }
	    this.animate_changes(node_infos);
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
    // name it for debugging from the console
    the_livetable = new LiveTable();
    the_livetable.init();
})
