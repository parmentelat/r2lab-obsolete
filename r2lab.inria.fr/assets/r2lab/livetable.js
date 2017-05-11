"use strict";

// sidecar_url global variable is defined in template sidecar-url.js
// from sidecar_url as defined in settings.py

//global - mostly for debugging and convenience
let the_livetable;

////////// configurable
let livetable_options = {

    nb_nodes : 37,
    
    fedora_badge : '<img src="/assets/img/fedora-logo.png">',
    ubuntu_badge : '<img src="/assets/img/ubuntu-logo.png">',
    other_badge : '<img src="/assets/img/other-logo.png">',

    ////////// must be in sync with r2lab-sidecar.js
    // the 2 socket.io channels that are used
    channels : {
	chan_nodes : 'info:nodes',
	chan_nodes_request : 'request:nodes',
    },

    // obsolete
    livetable_show_rxtx_rates : false,

    debug : false,
}


function livetable_debug(...args) {
    if (livetable_options.debug)
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
let TableNode = function (id) {
    this.id = id;

    this.cells_data = [
	[ span_html(id, 'badge pointer'), '' ],	// id
	undefined,				// avail
	undefined,				// on/off
	undefined,				// usrp-on-off
	undefined,				// ping
	undefined,				// ssh
	undefined,				// os_release
	undefined,				// uname
	undefined				// image_radical
    ];

    // fully present nodes
    this.is_alive = function() {
	return this.cmc_on_off == 'on'
	    && this.control_ping == 'on'
	    && this.control_ssh == 'on'
	    && this.available != 'ko';
    }

    // nodes worth being followed when clicking on the table banner
    this.is_worth = function() {
	return (   this.cmc_on_off == 'on'
		   || this.usrp_on_off == 'on'
		   || this.control_ping == 'on'
		   || this.control_ssh == 'on' )
	    && this.available != 'ko';
    }

    // node_info is a dict coming through socket.io in JSON
    // simply copy the fields present in this dict in the local object
    // for further usage in animate_changes
    // don't bother if no change is detected
    this.update_from_news = function(node_info) {
	let modified = false;
	for (let prop in node_info) {
	    if (node_info[prop] != this[prop]) {
		this[prop] = node_info[prop];
		modified = true;
		livetable_debug(`node_info[${prop}] = ${node_info[prop]}`);
	    }
	}

	if (! modified) {
	    // livetable_debug(`no change on ${node_info.id} - exiting`);
	    return;
	} else {
	    livetable_debug(`id = ${node_info.id} ->`, node_info);
	}

	// then rewrite actual representation in cells_data
	// that will contain a list of ( html_text, class )
	// used by the d3 mechanism to update the <td> elements in the row
	let col = 1
	// available
	this.cells_data[col++] =
	    (this.available == 'ko') ?
	    [ span_html('', 'fa fa-ban'), 'error' ] :
	    [ span_html('', 'fa fa-check'), 'ok' ];
	// on/off
	this.cells_data[col++] =
	    this.cmc_on_off == 'fail' ? [ 'N/A', 'error' ]
	    : this.cmc_on_off == 'on' ? [ span_html('', 'fa fa-toggle-on'), 'ok' ]
	    : [ span_html('', 'fa fa-toggle-off'), 'ko' ];
	// usrp
	this.cells_data[col++] = this.usrp_cell();
	// ping
	this.cells_data[col++] =
	    this.control_ping == 'on' ? [ span_html('', 'fa fa-link'), 'ok' ]
	    : [ span_html('', 'fa fa-unlink'), 'ko' ];
	// ssh
	this.cells_data[col++] =
	    this.control_ssh == 'on' ? [ span_html('', 'fa fa-circle'), 'ok' ]
	    : [ span_html('', 'fa fa-circle-o'), 'ko' ];
	//
	this.cells_data[col++] = this.release_cell(this.os_release);
	this.cells_data[col++] = this.uname_cell(this.uname);
	this.cells_data[col++] = this.image_cell(this.image_radical);
	// optional
	if (livetable_options.show_rxtx_rates) {
	    this.cells_data[col++] = this.rxtx_cell(this.wlan0_rx_rate);
	    this.cells_data[col++] = this.rxtx_cell(this.wlan0_tx_rate);
	    this.cells_data[col++] = this.rxtx_cell(this.wlan1_rx_rate);
	    this.cells_data[col++] = this.rxtx_cell(this.wlan1_tx_rate);
	}
	livetable_debug(`after update_from_news on id=${node_info.id} -> `,
			this.cells_data);
    }

    this.usrp_cell = function() {
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

    this.release_cell = function(os_release) {
	// use a single css class for now
	let klass = 'os';
	if (os_release == undefined)
	    return [ "n/a", klass ];
	if (os_release.startsWith('fedora'))
	    return [ livetable_options.fedora_badge + ' ' + os_release + ' ', klass ];
	else if (os_release.startsWith('ubuntu'))
	    return [ livetable_options.ubuntu_badge + ' ' + os_release + ' ', klass ];
	else if (os_release == 'other')
	    return [ livetable_options.other_badge + ' (ssh OK)', klass ];
	else
	    return [ 'N/A', klass ];
    }

    this.uname_cell = function(uname) {
	return [ uname, 'os' ];
    }

    this.image_cell = function(image_radical) {
	let klass = 'image';
	if (image_radical == undefined)
	    return [ "n/a", klass ];
	return [ image_radical, klass ];
    }

    // raw data is bits/s
    this.rxtx_cell = function(value) {
	let klass = 'rxtx';
	// forget about nodes that are not fully operational
	if ((value == undefined) || (! this.is_alive()))
	    return ["-", klass] ;
	// we need to format this into kbps, Mbps, etc..
	let raw = Number(value);
	let number, unit;
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
	let nice = number.toLocaleString() + " " + unit;
	return [ nice, klass ];
    }

    this.set_display = function(display) {
	let selector = '#livetable_container #row' + this.id;
	display ? $(selector).show() : $(selector).hide();
    }

}

let ident = function(d) { return d; };
let get_node_id = function(node){return node.id;}
let get_node_data = function(node){return node.cells_data;}
// rewriting info should happen in update_from_news
let get_html = function(tuple) {return (tuple === undefined) ? 'n/a' : tuple[0];}
let get_class = function(tuple) {return (tuple === undefined) ? '' : tuple[1];}

//////////////////////////////
function LiveTable() {

    this.nodes = [];

    this.init = function() {
	this.init_dom();
	this.init_nodes();
	this.init_sidecar_socket_io();
    }

    this.init_dom = function () {
	let containers = d3.selectAll('#livetable_container');
	let head = containers.append('thead').attr('class', 'livetable_header');
	let body = containers.append('tbody').attr('class', 'livetable_body');
	let foot = containers.append('tfoot').attr('class', 'livetable_header');

	let self = this;
	let header_rows = d3.selectAll('.livetable_header').append('tr')
	    .attr('class', 'all')
	    .on('click', function(){self.toggle_view_mode();})
	;
	header_rows.append('th').html('node');
	header_rows.append('th').html('avail.');
	header_rows.append('th').html('on/off');
	header_rows.append('th').html('usrp');
	header_rows.append('th').html('ping');
	header_rows.append('th').html('ssh');
	header_rows.append('th').html('last O.S.');
	header_rows.append('th').html('last uname');
	header_rows.append('th').html('last image');
	if (livetable_options.show_rxtx_rates) {
	    header_rows.append('th').html('w0-rx').attr('class','rxtx');
	    header_rows.append('th').html('w0-tx').attr('class','rxtx');
	    header_rows.append('th').html('w1-rx').attr('class','rxtx');
	    header_rows.append('th').html('w1-tx').attr('class','rxtx');
	}

    }

    this.init_nodes = function () {
	for (let i=0; i < livetable_options.nb_nodes; i++) {
	    this.nodes[i] = new TableNode(i+1);
	}
    }

    this.locate_node_by_id = function(id) {
	return this.nodes[id-1];
    }

    /* mode is either 'all' or 'worth' */
    this.view_mode = 'all';
    this.toggle_view_mode = function () {
	this.view_mode = (this.view_mode == 'all') ? 'worth' : 'all';
	this.display_nodes(this.view_mode);
	$(".livetable_header tr").toggleClass('all');
    }
    this.display_nodes = function(mode) {
	for (let i in this.nodes) {
	    let node=this.nodes[i];
	    let display = (mode=='all') ? true : (node.is_worth());
	    node.set_display(display);
	}
    }

    // this code uses d3 nested selections
    // I had to tweak it when adopting d3-v4 as per 
    // http://stackoverflow.com/questions/39861603/d3-js-v4-nested-selections
    // not that I have understood the bottom of it, but it works again..
    this.animate_changes = function(nodes_info) {
	livetable_debug("animate_changes");
	let tbody = d3.select("tbody.livetable_body");
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
    this.handle_json_status = function(json) {
	// xxx somehow we get noise in the mix
	if (json == "" || json == null) {
	    console.log("Bloops..");
	    return;
	}
	try {
	    let node_infos = JSON.parse(json);
	    livetable_debug(`handle_json_status - incoming ${node_infos.length} node infos`);
	    // first we write this data into the TableNode structures
	    for (let i=0; i < node_infos.length; i++) {
		let node_info = node_infos[i];
		let id = node_info['id'];
		let node = this.locate_node_by_id(id);
		if (node != undefined)
		    node.update_from_news(node_info);
		else
		    console.log(`livetable: could not locate node id ${id} - ignored`);
	    }
	    this.animate_changes(node_infos);
	} catch(err) {
	    if (json != "") {
		console.log(`Could not apply news - ignored  - JSON has ${json.length} chars`);
		console.log(err.stack);
	    }
	}
    }

    this.init_sidecar_socket_io = function() {
	livetable_debug(`livetable is connecting to sidecar server at ${sidecar_url}`);
	this.sidecar_socket = io(sidecar_url);
	// what to do when receiving news from sidecar
	let { chan_nodes } = livetable_options.channels;
	let lab = this;
	this.sidecar_socket.on(chan_nodes, function(json){
	    livetable_debug(`livetable is receiving on ${chan_nodes}`);
            lab.handle_json_status(json);
	});
	this.request_complete_from_sidecar();
    }

    // request sidecar for initial status on the signalling channel
    // content is not actually used by sidecar server
    // could maybe send some client id instead
    this.request_complete_from_sidecar = function() {
	let { chan_nodes_request } = livetable_options.channels;
	this.sidecar_socket.emit(chan_nodes_request, 'INIT');
    }

}

// autoload
$(function() {
    // name it for debugging from the console
    the_livetable = new LiveTable();
    the_livetable.init();
})
