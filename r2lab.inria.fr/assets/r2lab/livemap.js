// xxx todo
// there are way too many globals in this code..
// we should have a single livemap object with everything else shoved in there

////////// configurable
// the space around the walls in the canvas
var livemap_margin_x = 50, livemap_margin_y = 50;

// distance between nodes
var livemap_space_x = 80, livemap_space_y = 80;
// distance between nodes and walls
var livemap_padding_x = 40, livemap_padding_y = 40;

// size for rendering nodes status
livemap_radius_unavailable = 24;
livemap_radius_ok = 18;
livemap_radius_pinging = 12;
livemap_radius_warming = 6;
livemap_radius_ko = 0;

// see http://stackoverflow.com/questions/14984007/how-do-i-include-a-font-awesome-icon-in-my-svg
// and http://stackoverflow.com/questions/12882885/how-to-add-nbsp-using-d3-js-selection-text-method/12883617#12883617
// parmentelat ~/git/Font-Awesome/less $ grep 'fa-var-plane' variables.less
// @fa-var-plane: "\f072";
var livemap_icon_plane_content = "\uf072";
var livemap_icon_phone_content = "\uf095";
var livemap_icon_question_content = "\uf128";

////////// must be in sync with sidecar.js
// the socket.io channels that are used -- see sidecar/AA-overview.md
var chan_nodes = 'info:nodes';
var chan_nodes_request = 'request:nodes';
var chan_phones = 'info:phones';
var chan_phones_request = 'request:phones';

// sidecar_url var is defined in template sidecar-url.js
// from sidecar_url as defined in settings.py

////////// status details
// fields that this widget knows about concerning each node
// * available: missing, or 'ok' : node is expected to be usable; if 'ko' a very visible red circle shows up
// * cmc_on_off: 'on' or 'off' - nodes that fail will be treated as 'ko', better use 'available' instead
// * control_ping: 'on' or 'off'
// * control_ssh: 'on' or 'off'
// * os_release: fedora* ubuntu* with/without gnuradio, .... or 'other'
// * wlan0_rx_rate: and similar with wlan1 and tx: bit rate in Mbps, expected to be in the [0, 20] range a priori

////////// nodes positions - originally output from livemap-prep.py
mapnode_specs = [
    { id: 1, i:0, j:4 },
    { id: 2, i:0, j:3 },
    { id: 3, i:0, j:2 },
    { id: 4, i:0, j:1 },
    { id: 5, i:0, j:0 },
    { id: 6, i:1, j:4 },
    { id: 7, i:1, j:3 },
    { id: 8, i:1, j:2 },
    { id: 9, i:1, j:1 },
    { id: 10, i:1, j:0 },
    { id: 11, i:2, j:4 },
    { id: 12, i:2, j:3 },
    { id: 13, i:2, j:2 },
    { id: 14, i:2, j:1 },
    { id: 15, i:2, j:0 },
    { id: 16, i:3, j:4 },
    { id: 17, i:3, j:2 },
    { id: 18, i:3, j:1 },
    { id: 19, i:4, j:4 },
    { id: 20, i:4, j:3 },
    { id: 21, i:4, j:2 },
    { id: 22, i:4, j:1 },
    { id: 23, i:5, j:4 },
    { id: 24, i:5, j:2 },
    { id: 25, i:5, j:1 },
    { id: 26, i:6, j:4 },
    { id: 27, i:6, j:3 },
    { id: 28, i:6, j:2 },
    { id: 29, i:6, j:1 },
    { id: 30, i:6, j:0 },
    { id: 31, i:7, j:4 },
    { id: 32, i:7, j:3 },
    { id: 33, i:7, j:2 },
    { id: 34, i:7, j:1 },
    { id: 35, i:7, j:0 },
    { id: 36, i:8, j:1 },
    { id: 37, i:8, j:0 },
];
////////// the  two pillars - this is manual
var pillar_specs = [
    { id: 'left', i:3, j:3 },
    { id: 'right', i:5, j:3 },
];

var mapphone_specs = [
    {id : 1, i : 0.5, j : 4.2 },
];

//global - mostly for debugging and convenience
var the_livemap;

//////////////////// configuration
// total number of rows and columns
var steps_x = 8, steps_y = 4;

//// static area
// walls and inside
var walls_radius = 30;

// pillars - derived from the walls
var pillar_radius = 16;

var livemap_debug = false;

//////////////////////////////////////// nodes
// the overall room size
var room_x = steps_x*livemap_space_x + 2*livemap_padding_x, room_y = steps_y*livemap_space_y + 2*livemap_padding_y;

// translate i, j into actual coords
function grid_to_canvas (i, j) {
    return [i*livemap_space_x + livemap_margin_x + livemap_padding_x,
	    (steps_y-j)*livemap_space_y + livemap_margin_y + livemap_padding_y];
}

//////////////////////////////
// our mental model is y increase to the top, not to the bottom
// also, using l (relative) instead of L (absolute) is simpler
// but it keeps roundPathCorners from rounding.js from working fine
// keep it this way from now, a class would help keep track here
function line_x(x) {return "l " + x + " 0 ";}
function line_y(y) {return "l 0 " + -y + " ";}

function walls_path() {
    var path="";
    path += "M " + (room_x+livemap_margin_x) + " " + (room_y+livemap_margin_y) + " ";
    path += line_x(-(7*livemap_space_x+2*livemap_padding_x));
    path += line_y(3*livemap_space_y);
    path += line_x(-1*livemap_space_x);
    path += line_y(livemap_space_y+2*livemap_padding_y);
    path += line_x(2*livemap_space_x+2*livemap_padding_x);
    path += line_y(-livemap_space_y);
    path += line_x(4*livemap_space_x-2*livemap_padding_x);
    path += line_y(livemap_space_y);
    path += line_x(2*livemap_space_x+2*livemap_padding_x);
    path += "Z";
    return path;
}

function walls_style(selection) {
    selection
	.attr('stroke', '#3b4449')
	.attr('stroke-width',  '6px')
	.attr('stroke-linejoin', 'round')
	.attr('stroke-miterlimit', 8)
    ;
}

// obj_info is a dict coming through socket.io in JSON
// simply copy the fieds present in this dict in the local object
// for further usage in animate_nodes_changes
function update_obj_from_info(obj, obj_info){
    var modified = false;
    for (var prop in obj_info)
	if (obj_info[prop] != obj[prop]) {
	    obj[prop] = obj_info[prop];
	    modified = true;
	}
    return modified;
}

// locating a record by id in a list
function locate_by_id(list_objs, id) {
    for (var i=0; i< list_objs.length; i++)
	if (list_objs[i].id == id)
	    return list_objs[i];
    console.log("ERROR: livemap: locate_by_id: id=" + id + " was not found");
}

//////////////////////////////
var MapPhone = function(phone_spec) {
    this.id = phone_spec['id'];
    this.i = phone_spec['i'];
    this.j = phone_spec['j'];
    var coords = grid_to_canvas(this.i, this.j);
    this.x = coords[0];
    this.y = coords[1];

    this.text = function(){
	if (this.airplane_mode == 'on')
	    return livemap_icon_plane_content;
	else if (this.airplane_mode == 'off')
	    return livemap_icon_phone_content;
	else
	    return livemap_icon_question_content;
    }

}

//////////////////////////////
// nodes are dynamic
// their visual rep. get created through d3 enter mechanism
var MapNode = function (node_spec) {
    this.id = node_spec['id'];
    // i and j refer to a logical grid
    this.i = node_spec['i'];
    this.j = node_spec['j'];
    // compute actual coordinates
    var coords = grid_to_canvas (this.i, this.j);
    this.x = coords[0];
    this.y = coords[1];

    // status details are filled upon reception of news

    this.is_available = function() {
	return this.available != 'ko';
    }

    this.is_alive = function() {
	return this.cmc_on_off == 'on'
	    && this.control_ping == 'on'
	    && this.control_ssh != 'off'
	    && this.available != 'ko';
    }

    // shift label south-east a little
    // we cannot just add a constant to the radius
    this.text_offset = function(radius) {
	return Math.max(5, 12-radius/2);
    }
    this.text_x = function() {
	if ( ! this.is_available()) return this.x;
	var radius = this.node_status_radius();
	var delta = this.text_offset(radius);
	return this.x + ((radius == 0) ? 0 : (radius + delta));
    }
    this.text_y = function() {
	if ( ! this.is_available()) return this.y;
	var radius = this.node_status_radius();
	var delta = this.text_offset(radius);
	return this.y + ((radius == 0) ? 0 : (radius + delta));
    }


    ////////// node radius
    // this is how we convey most of the info
    // when turned off, the node's circle vanishes
    // when it's on but does not yet answer ping, a little larger
    // when answers ping, still larger
    // when ssh : full size with OS badge
    // but animate.py does show that
    this.node_status_radius = function() {
	// completely off
	if (this.cmc_on_off != 'on')
	    return livemap_radius_ko;
	// does not even ping
	else if (this.control_ping != 'on')
	    return livemap_radius_warming;
	// pings but cannot get ssh
	else if (this.control_ssh != 'on')
	    return livemap_radius_pinging;
	// ssh is answering
	else
	    return livemap_radius_ok;
    }

    // right now this is visible only for intermediate radius
    // let's show some lightgreen for the 2/3 radius (ssh is up)
    this.text_color = function() {
	return '#555';
    }

    // luckily this is not rendered when a filter is at work
    this.node_status_color = function() {
	var radius = this.node_status_radius();
	return (radius == livemap_radius_pinging) ? d3.rgb('#71edb0').darker() :
	    (radius == livemap_radius_warming) ? d3.rgb('#f7d8dd').darker() :
	    '#bbb';
    }

    // showing an image (or not, if filter is undefined)
    // depending on the OS
    this.node_status_filter = function() {
	var filter_name;
	// only set a filter with full-fledged nodes
	if (! this.is_alive())
	    return undefined;
	// remember infos might be incomplete
	else if (this.os_release == undefined)
	    return undefined;
	else if (this.os_release.indexOf('other') >= 0)
	    filter_name = 'other-logo';
	else if (this.os_release.indexOf('fedora') >= 0)
	    filter_name = 'fedora-logo';
	else if (this.os_release.indexOf('ubuntu') >= 0)
	    filter_name = 'ubuntu-logo';
	else
	    return undefined;
	return "url(#" + filter_name + ")";
    }

    // a missing 'available' means the node is OK
    this.unavailable_display = function() {
	if ((this.available == undefined)
	    || (this.available == "ok"))
	    return "none";
	else
	    return "on";
    }

    ////////// show an icon only if usrp_type is defined
    this.usrp_status_display = function() {
	return (this.usrp_type) ? "on" : "none";
    }

    this.usrp_status_filter = function() {
	var filter_name;
	if ( ! this.usrp_type )
	    return undefined;
	else if (this.usrp_on_off == 'on')
	    filter_name = 'gnuradio-logo-icon-green';
	else if (this.usrp_on_off == 'off')
	    filter_name = 'gnuradio-logo-icon-red';
	else
	    return undefined;
	return "url(#" + filter_name + ")";
    }

    // full size for the usrp-icon
    // this is arbitrary but has the right width/height ratio
    usrp_w = 13;
    usrp_h = 23;
    // on and off units get rendered each at their size
    usrp_on_ratio = .90;
    usrp_off_ratio = .70;
    // the radius of the circle that we need to leave free
    this.overall_radius = function() {
	var r = this.node_status_radius();
	if (! this.is_available())
	    return r;
	// node is off, we need to keep space for the label
	if (r == 0)
	    return 10;
	return r;
    }
    // how much we move from the north-east intersection
    // with node radius circle
    usrp_delta_x = 2;
    usrp_delta_y = 3;
    // 0.7 stands for sin(pi/2)
    this.usrp_offset_x = function() {
	return this.overall_radius() * 0.7 + usrp_delta_x;
    }
    this.usrp_offset_y = function() {
	return this.overall_radius() * 0.7 + usrp_delta_y;
    }
    this.usrp_x = function() {
	return this.x + this.usrp_offset_x(); }
    this.usrp_y = function() {
	return this.y - (this.usrp_offset_y() + this.usrp_h()); }
    this.usrp_w = function() {
	return usrp_w * (this.usrp_on_off == "on" ? usrp_on_ratio : usrp_off_ratio); }
    this.usrp_h = function() {
	return usrp_h * (this.usrp_on_off == "on" ? usrp_on_ratio : usrp_off_ratio); }

}

var get_obj_id = function(node) {return node.id;}

//////////////////////////////
function LiveMap() {
    var canvas_x = room_x + 2 * livemap_margin_x;
    var canvas_y = room_y + 2 * livemap_margin_y;
    var svg =
	d3.select('div#livemap_container')
	.append('svg')
	.attr('width', canvas_x)
	.attr('height', canvas_y)
    ;
    // we insert a g to flip the walls upside down
    // too lazy to rewrite this one
    var g =
	svg.append('g')
	.attr('id', 'walls_upside_down')
	.attr('transform', 'translate(' + canvas_x + ',' + canvas_y + ')' + ' ' +  'rotate(180)')
    ;

    var walls = g.append('path')
	.attr('d', walls_path())
	.attr('id', 'walls')
	.attr('fill', '#fdfdfd')
	.call(walls_style)
    ;

    console.log('inside pillar_specs =', pillar_specs);
    pillar_specs.forEach(function(spec) {
	var coords = grid_to_canvas(spec.i, spec.j);
	svg.append('rect')
	    .attr('id', 'pillar-' + spec.id)
	    .attr('class', 'pillar')
	    .attr('x', coords[0] - pillar_radius)
	    .attr('y', coords[1] - pillar_radius)
	    .attr('width', 2*pillar_radius)
	    .attr('height', 2*pillar_radius)
	    .attr('fill', '#101030')
	    .call(walls_style)
	;
    });

    this.init = function() {
	this.init_nodes();
	this.init_phones();
	this.init_sidecar_socket_io();
    }

    //////////////////// nodes
    this.init_nodes = function () {
	this.nodes = [];
	for (var i=0; i < mapnode_specs.length; i++) {
	    this.nodes[i] = new MapNode(mapnode_specs[i]);
	}
    }

    //////////////////// phones
    this.init_phones = function () {
	this.phones = [];
	for (var i=0; i < mapphone_specs.length; i++) {
	    this.phones[i] = new MapPhone(mapphone_specs[i]);
	}
    }

    //////////////////// nodes
    this.handle_nodes_json = function(json) {
	var livemap = this;
	return this.handle_incoming_json("node", this.nodes, json,
					 function() { livemap.animate_nodes_changes();});
    }

    this.handle_phones_json = function(json) {
	var livemap = this;
	return this.handle_incoming_json("phone", this.phones, json,
					 function() { livemap.animate_phones_changes();});
    }

    //////////////////// generic way to handle incoming json
    // apply changes to internal data and then apply callback
    // that will reflect the changes visually
    this.handle_incoming_json = function(type, list_objs, json, callback) {
	// xxx somehow we get noise in the mix
	if (json == "" || json == null) {
	    console.log("node json fragment is empty..");
	    return;
	}
	try {
	    var infos = JSON.parse(json);
	    if (livemap_debug) {
		console.log("*** " + new Date() + " DBG Received info about " + infos.length + " " + type + "(s)");
		console.log(infos);
		console.log("*** DBG end");
	    }
	    // first we write this data into the MapNode structures
	    var livemap = this;
	    infos.forEach(function(info) {
		var id = info['id'];
		var obj = locate_by_id(list_objs, id);
		if (obj != undefined)
		    update_obj_from_info(obj, info);
		else
		    console.log("livemap: could not locate " + type + " id " + id + " - ignored");
	    });
	    callback();
	} catch(err) {
	    console.log("*** Could not handle news for " + type + " - ignored JSON has " + json.length + " chars");
	    console.log(err.stack);
	    console.log("***");
	}
    }

    //////////////////// the nodes graphical layout
    this.animate_nodes_changes = function() {
	var svg = d3.select('div#livemap_container svg');
	var animation_duration = 850;
	var circles = svg.selectAll('circle.node-status')
	    .data(this.nodes, get_obj_id);
	// circles show the overall status of the node
	circles.enter()
	    .append('circle')
	    .attr('class', 'node-status')
	    .attr('id', function(node){return node.id;})
	    .attr('cx', function(node){return node.x;})
	    .attr('cy', function(node){return node.y;})
	    .on('click', function() {
		// call an external function (located in info-nodes.js) to show de nodes details
		info_nodes(this.id)
	    })
	;
	circles.transition()
	    .duration(animation_duration)
	    .attr('r', function(node){return node.node_status_radius();})
	    .attr('fill', function(node){return node.node_status_color();})
	    .attr('filter', function(node){return node.node_status_filter();})
	;
	// labels show the nodes numbers
	var labels = svg.selectAll('text')
	    .data(this.nodes, get_obj_id);
	labels.enter()
	    .append('text')
	    .attr('class', 'node-label')
	    .text(get_obj_id)
	    .attr('x', function(node){return node.x;})
	    .attr('y', function(node){return node.y;})
	    .attr('id', function(node){return node.id;})
	    .on('click', function() {
		//call a externa function (located in info-nodes.js) to show de nodes details
		info_nodes(this.id)
	    })
	;
	labels.transition()
	    .duration(animation_duration)
	    .attr('fill', function(node){return node.text_color();})
	    .attr('x', function(node){return node.text_x();})
	    .attr('y', function(node){return node.text_y();})
	;

	// how to display unavailable nodes
	var unavailables = svg.selectAll('circle.unavailable')
	    .data(this.nodes, get_obj_id);
	unavailables.enter()
	    .append('circle')
	    .attr('class', 'unavailable')
	    .attr('cx', function(node){return node.x;})
	    .attr('id', function(node){return node.id;})
	    .attr('cy', function(node){return node.y;})
	    .attr('r', function(node){return livemap_radius_unavailable;})
	    .on('click', function() {
		//call a externa function (located in info-nodes.js) to show de nodes details
		info_nodes(this.id)
	    })
	;
	unavailables.transition()
	    .duration(animation_duration)
	    .attr('display', function(node){return node.unavailable_display();})
	;

	// these rectangles are placeholders for the various icons
	// that are meant to show usrp status
	usrp_w = 13;
	usrp_h = 23;
	usrp_offset_x = 17;
	usrp_offset_y = 10;
	var usrp_rects = svg.selectAll('rect.usrp-status')
	    .data(this.nodes, get_obj_id);
	usrp_rects.enter()
	    .append('rect')
	    .attr('class', 'usrp-status')
	    .attr('id', function(node){return node.id;})
	    .attr('stroke-width', '1px')
	;
	usrp_rects.transition()
	    .duration(animation_duration)
	    .attr('display', function(node){return node.usrp_status_display();})
	    .attr('filter', function(node){return node.usrp_status_filter();})
	    .attr('x', function(node){return node.usrp_x();})
	    .attr('y', function(node){return node.usrp_y();})
	    .attr('width', function(node){return node.usrp_w();})
	    .attr('height', function(node){return node.usrp_h();})
	;
    }

    //////////////////// convenience / helpers
    // filters nice_float(for background)s
    this.declare_image_filter = function (id_filename, suffix) {
	// create defs element if not yet present
	if ( ! $('#livemap_container svg defs').length) {
	    d3.select('#livemap_container svg').append('defs');
	}
	// create filter in there
        var defs = d3.select("#livemap_container svg defs");
        var filter = defs.append("filter")
            .attr("id", id_filename)
	    .attr("x", "0%")
	    .attr("y", "0%")
	    .attr("width", "100%")
	    .attr("height", "100%")
	;
        filter.append("feImage")
	    .attr("xlink:href", "../assets/img/" + id_filename
		  + "." + suffix);
    }

    this.declare_image_filter('fedora-logo', 'png');
    this.declare_image_filter('ubuntu-logo', 'png');
    this.declare_image_filter('other-logo', 'png');
    this.declare_image_filter('gnuradio-logo-icon-green', 'svg');
    this.declare_image_filter('gnuradio-logo-icon-red', 'svg');

    //////////////////// phones graphical layout
    this.animate_phones_changes = function() {
	var svg = d3.select('div#livemap_container svg');
	var animation_duration = 850;

	var w = 20;
	var h = 20;
	var r = 2;
	var squares = svg.selectAll('rect.phone-status')
	    .data(this.phones, get_obj_id);
	// simple square repr. for now, with an airplane in the middle
	squares.enter()
	    .append('rect')
	    .attr('class', 'phone-status')
	    .attr('id', function(phone){return phone.id;})
	    .attr('x', function(phone){return phone.x - w/2;})
	    .attr('y', function(phone){return phone.y - h/2;})
	    .attr('rx', r)
	    .attr('ry', r)
	    .attr('width', w)
	    .attr('height', h)
	// in .css at some point
	    .attr('stroke-width', 1)
	    .attr('stroke', 'black')
	    .attr('fill', 'none')
	;

	var texts = svg.selectAll('text.phone-status')
	    .data(this.phones, get_obj_id);

	texts.enter()
	    .append('text')
	    .attr('class', 'phone-status')
	    .attr('x', function(phone){return phone.x;})
	    .attr('y', function(phone){return phone.y;})
	    .attr('dy', h*.1)
	    .attr('font-family', 'FontAwesome')
	    .attr('font-size', h*1)
	    .attr('textLength', w*.8)
	    .attr('lengthAdjust', 'spacingAndGlyphs')
	;
	texts.transition()
	    .text(function(phone){ return phone.text();})
	;

    }

    //////////////////// socket.io business
    this.init_sidecar_socket_io = function() {
	if (livemap_debug)
	    console.log("livemap is connecting to sidecar server at " + sidecar_url);
	this.sidecar_socket = io(sidecar_url);
	// what to do when receiving news from sidecar
	var lab = this;
	////////// nodes
	if (livemap_debug)
	    console.log("arming callback on channel " + chan_nodes);
	this.sidecar_socket.on(chan_nodes, function(json){
            lab.handle_nodes_json(json);
	});
	// request the first complete copy of the sidecar db
	if (livemap_debug)
	    console.log("requesting complete status on channel " + chan_nodes_request);
	this.sidecar_socket.emit(chan_nodes_request, 'INIT');
	////////// phones
	if (livemap_debug)
	    console.log("arming callback on channel " + chan_phones);
	this.sidecar_socket.on(chan_phones, function(json){
            lab.handle_phones_json(json);
	});
	// request the first complete copy of the sidecar db
	if (livemap_debug)
	    console.log("requesting complete status on channel " + chan_phones_request);
	this.sidecar_socket.emit(chan_phones_request, 'INIT');
    }

}

// autoload
$(function() {
    the_livemap = new LiveMap();
    the_livemap.init();
})
