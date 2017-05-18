"use strict";

//
// this code is the common ground for both livetable and livehardware
//
// sidecar_url global variable is defined in template sidecar-url.js
// from sidecar_url as defined in settings.py
//

////////// configurable
let livecolumns_options = {

    nb_nodes : 37,
    
    ////////// must be in sync with r2lab-sidecar.js
    // the 2 socket.io channels that are used
    channels : {
	chan_nodes : 'info:nodes',
	chan_nodes_request : 'request:nodes',
    },

    debug : false,
}


function livecolumns_debug(...args) {
    if (livecolumns_options.debug)
	console.log(...args);
}

// quick'n dirty helper to create <span> tags inside the <td>
// d3 should allow us to do that more nicely but I could not figure it out yet
function span_html(text, cls) {
    let tag = cls ? ` class='${cls}'` : "";
    return `<span${tag}>${text}</span>`;
}


//////////////////////////////
// nodes are dynamic
// their table row and cells get created through d3 enter mechanism
function LiveColumnsNode (id) {
    this.id = id;
}

// node_info is a dict coming through socket.io in JSON
// simply copy the fields present in this dict in the local object
// for further usage in animate_changes; 
// don't bother if no change is detected
LiveColumnsNode.prototype.update_from_news = function(node_info) {
    let modified = false;
    for (let prop in node_info) {
	if (node_info[prop] != this[prop]) {
	    this[prop] = node_info[prop];
	    modified = true;
	    livecolumns_debug(`node_info[${prop}] = ${node_info[prop]}`);
	}
    }
    
    if (! modified) {
	// livecolumns_debug(`no change on ${node_info.id} - exiting`);
	return;
    } else {
	livecolumns_debug(`id = ${node_info.id} ->`, node_info);
    }
    
    // this must be implemented for each view, and adjust this.cells_data
    this.compute_cells_data();
    livecolumns_debug(`after update_from_news on id=${node_info.id} -> `,
		      this.cells_data);
}

LiveColumnsNode.prototype.cell_available = function() {
    return (this.available == 'ko') ?
	[ span_html('', 'fa fa-ban'), 'error' ] :
	[ span_html('', 'fa fa-check'), 'ok' ];
}

LiveColumnsNode.prototype.cell_on_off = function() {
    return (this.cmc_on_off == 'fail') ? [ 'N/A', 'error' ]
	: this.cmc_on_off == 'on' ? [ span_html('', 'fa fa-toggle-on'), 'ok' ]
	: [ span_html('', 'fa fa-toggle-off'), 'ko' ];
}

LiveColumnsNode.prototype.cell_usrp = function() {
    let alt_text = "";
    alt_text += (this.gnuradio_release) ? "gnuradio_release = "
	+ this.gnuradio_release : "no gnuradio installed";
    let text = this.usrp_type || 'none';
    text += ' ';
    text += (this.usrp_on_off == 'on')
	? span_html('', 'fa fa-toggle-on')
	: span_html('', 'fa fa-toggle-off') ;
    let cell = '<span title="' + alt_text + '">' + text + '</span>';
    let klass = (this.usrp_on_off == 'on') ? 'ok'
	: (this.usrp_on_off == 'off') ? 'ko' : 'error';
    return [cell, klass];
}

LiveColumnsNode.prototype.is_worth = function() {
    return true;
}

LiveColumnsNode.prototype.set_display = function(display) {
    let selector = 'tbody.livecolumns_body #row' + this.id;
    display ? $(selector).show() : $(selector).hide();
}

let ident = function(d) { return d; };
let get_node_id = function(node){return node.id;}
let get_node_data = function(node){return node.cells_data;}
// rewriting info should happen in update_from_news
let get_html = function(tuple) {return (tuple === undefined) ? 'n/a' : tuple[0];}
let get_class = function(tuple) {return (tuple === undefined) ? '' : tuple[1];}

//////////////////////////////
function LiveColumns() {
    this.nodes = [];
    /* mode is either 'all' or 'worth' */
    this.view_mode = 'all';
}

LiveColumns.prototype.init = function() {
    let headers = this.init_table();
    // needs to be written
    this.init_headers(headers);
    // needs to be written
    this.init_nodes();
    this.init_sidecar_socket_io();
}

LiveColumns.prototype.init_table = function () {
    let containers = d3.selectAll(`#${this.domid}`);
    let head = containers.append('thead').attr('class', 'livecolumns_header');
    let body = containers.append('tbody').attr('class', 'livecolumns_body');
    let foot = containers.append('tfoot').attr('class', 'livecolumns_header');
    
    let self = this;
    let headers = d3.selectAll('.livecolumns_header').append('tr')
	.attr('class', 'all')
	.on('click', function(){self.toggle_view_mode();})
    ;
    return headers;
}

LiveColumns.prototype.locate_node_by_id = function(id) {
    return this.nodes[id-1];
}

LiveColumns.prototype.toggle_view_mode = function () {
    console.log("display_nodes", this.view_mode);
    this.view_mode = (this.view_mode == 'all') ? 'worth' : 'all';
    this.display_nodes(this.view_mode);
    $(".livecolumns_header tr").toggleClass('all');
}

LiveColumns.prototype.display_nodes = function(mode) {
    for (let node of this.nodes) {
	let display = (mode=='all') ? true : (node.is_worth());
	node.set_display(display);
    }
}

// this code uses d3 nested selections
// I had to tweak it when adopting d3-v4 as per 
// http://stackoverflow.com/questions/39861603/d3-js-v4-nested-selections
// not that I have understood the bottom of it, but it works again..
LiveColumns.prototype.animate_changes = function(nodes_info) {
    livecolumns_debug("animate_changes");
    let tbody = d3.select("tbody.livecolumns_body");
    // row update selection
    let rows = tbody.selectAll('tr')
	.data(this.nodes, get_node_id);
    ////////// create rows as needed
    let rowsenter = rows.enter()
	.append('tr')
	.attr('id', function(node){ return 'row' + node.id;})
    ;
    // the magic here is to pass rowsenter to the merge method
    // instead of rows
    let cells =
	rows.merge(rowsenter)
	.selectAll('td')
	.data(get_node_data);
    
    cells
	.enter()
	.append('td')
    // attach a click event on the first column only
	.each(function(d, i) {
	    if (i==0) {
		// I'm using DOM/jquery here because the datum d here
		//  is a tuple (html, class) so this is useless
		$(this).click(function() {
		    $(this).parent().attr('style', 'display:none');
		})
	    }
	})
	.merge(cells)
	.html(get_html)
	.attr('class', get_class);
}

////////// socket.io business
LiveColumns.prototype.handle_json_status = function(json) {
    // xxx somehow we get noise in the mix
    if (json == "" || json == null) {
	console.log("Bloops..");
	return;
    }
    try {
	let node_infos = JSON.parse(json);
	livecolumns_debug(`handle_json_status - incoming ${node_infos.length} node infos`);
	// first we write this data into the TableNode structures
	for (let i=0; i < node_infos.length; i++) {
	    let node_info = node_infos[i];
	    let id = node_info['id'];
	    let node = this.locate_node_by_id(id);
	    if (node != undefined)
		node.update_from_news(node_info);
	    else
		console.log(`livecolumns: could not locate node id ${id} - ignored`);
	}
	this.animate_changes(node_infos);
    } catch(err) {
	if (json != "") {
	    console.log(`Could not apply news - ignored  - JSON has ${json.length} chars`);
	    console.log(err.stack);
	}
    }
}

LiveColumns.prototype.init_sidecar_socket_io = function() {
    livecolumns_debug(`livecolumns is connecting to sidecar server at ${sidecar_url}`);
    this.sidecar_socket = io(sidecar_url);
    // what to do when receiving news from sidecar
    let { chan_nodes } = livecolumns_options.channels;
    let lab = this;
    this.sidecar_socket.on(chan_nodes, function(json){
	livecolumns_debug(`livecolumns is receiving on ${chan_nodes}`);
        lab.handle_json_status(json);
    });
    this.request_complete_from_sidecar();
}

// request sidecar for initial status on the signalling channel
// content is not actually used by sidecar server
// could maybe send some client id instead
LiveColumns.prototype.request_complete_from_sidecar = function() {
    let { chan_nodes_request } = livecolumns_options.channels;
    this.sidecar_socket.emit(chan_nodes_request, 'INIT');
}
