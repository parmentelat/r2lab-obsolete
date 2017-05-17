"use strict";

// xxx todo
// there are way too many globals in this code..
// we should have a single livemap object with everything else shoved in there

//global - mostly for debugging and convenience
let the_livemap;

////////// configurable
let livemap_options = {
    // the space around the walls in the canvas
    margin_x : 50, margin_y : 50,

    // distance between nodes
    space_x : 80, space_y : 80,

    // distance between nodes and walls
    padding_x : 40, padding_y : 40,

    // size for rendering nodes status
    radius_unavailable : 24,
    radius_ok : 18,
    radius_pinging : 12,
    radius_warming : 6,
    radius_ko : 0,

    //// static area
    // pillars - derived from the walls
    pillar_radius : 16,

    // usrp thingy
    // full size for the usrp-icon; this is arbitrary but has the right width/height ratio
    usrp_width : 13,
    usrp_height : 23,
    // on and off units get rendered each at their size
    usrp_on_ratio : .90,
    usrp_off_ratio : .70,
    // how much we move from the north-east intersection
    // with node radius circle
    usrp_delta_x : 2,
    usrp_delta_y : 3,
    

    // see http://stackoverflow.com/questions/14984007/how-do-i-include-a-font-awesome-icon-in-my-svg
    // and http://stackoverflow.com/questions/12882885/how-to-add-nbsp-using-d3-js-selection-text-method/12883617#12883617
    // parmentelat ~/git/Font-Awesome/less $ grep 'fa-var-plane' variables.less
    // @fa-var-plane: "\f072";
    icon_plane_content : "\uf072",
    icon_phone_content : "\uf095",
    icon_question_content : "\uf128",

    ////////// must be in sync with sidecar.js
    // the socket.io channels that are used -- see sidecar/AA-overview.md
    channels : {
	chan_nodes : 'info:nodes',
	chan_nodes_request : 'request:nodes',
	chan_phones : 'info:phones',
	chan_phones_request : 'request:phones',
    },

    debug : false,
}

function livemap_debug(...args) {
    if (livemap_options.debug)
	console.log(...args);
}

// sidecar_url var is defined in template sidecar-url.js
// from sidecar_url as defined in settings.py

////////// status details
// fields that this widget knows about concerning each node
// * available: missing, or 'ok' : node is expected to be usable; if 'ko' a very visible red circle shows up
// * cmc_on_off: 'on' or 'off' - nodes that fail will be treated as 'ko', better use 'available' instead
// * control_ping: 'on' or 'off'
// * control_ssh: 'on' or 'off'
// * os_release: fedora* ubuntu* with/without gnuradio, .... or 'other'

let livemap_geometry = {

    ////////// nodes positions - originally output from livemap-prep.py
    mapnode_specs : [
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
    ],

    ////////// the  two pillars - this is manual
    pillar_specs : [
	{ id: 'left', i:3, j:3 },
	{ id: 'right', i:5, j:3 },
    ],

    mapphone_specs : [
	{id : 1, i : 0.5, j : 4.2 },
    ],

    //////////////////// configuration
    // total number of rows and columns
    steps_x : 8, steps_y : 4,

    // the overall room size
    // xxx check this actually takes into account options when redefined later on
    room_x : function () {
	return this.steps_x*livemap_options.space_x + 2*livemap_options.padding_x
    },
    room_y : function () {
	return this.steps_y*livemap_options.space_y + 2*livemap_options.padding_y
    },

    // translate i, j into actual coords
    grid_to_canvas : function (i, j) {
	return [i*livemap_options.space_x + livemap_options.margin_x + livemap_options.padding_x,
		(this.steps_y-j)*livemap_options.space_y + livemap_options.margin_y + livemap_options.padding_y];
    },

    //////////////////////////////
    // our mental model is y increase to the top, not to the bottom
    // also, using l (relative) instead of L (absolute) is simpler
    // but it keeps roundPathCorners from rounding.js from working fine
    // keep it this way from now, a class would help keep track here
    line_x : function(x) {return `l ${x} 0 `;},
    line_y : function(y) {return `l 0 ${-y} `;},

    walls_path : function() {
	let path="";
	path += "M " + (this.room_x()+livemap_options.margin_x) + " " + (this.room_y()+livemap_options.margin_y) + " ";
	path += this.line_x(-(7*livemap_options.space_x+2*livemap_options.padding_x));
	path += this.line_y(3*livemap_options.space_y);
	path += this.line_x(-1*livemap_options.space_x);
	path += this.line_y(livemap_options.space_y+2*livemap_options.padding_y);
	path += this.line_x(2*livemap_options.space_x+2*livemap_options.padding_x);
	path += this.line_y(-livemap_options.space_y);
	path += this.line_x(4*livemap_options.space_x-2*livemap_options.padding_x);
	path += this.line_y(livemap_options.space_y);
	path += this.line_x(2*livemap_options.space_x+2*livemap_options.padding_x);
	path += "Z";
	return path;
    },

    walls_style : function(selection) {
	selection
	    .attr('stroke', '#3b4449')
	    .attr('stroke-width',  '6px')
	    .attr('stroke-linejoin', 'round')
	    .attr('stroke-miterlimit', 8)
	;
    },
}

////////////////////////////////////////
// helpers
// locating a record by id in a list
function locate_by_id (list_objs, id) {
    for (let i=0; i< list_objs.length; i++) {
	if (list_objs[i].id == id) {
	    return list_objs[i];
	}
    }
    console.log(`ERROR: livemap: locate_by_id: id= ${id} was not found`);
}

    
// obj_info is a dict coming through socket.io in JSON
// simply copy the fieds present in this dict in the local object
// for further usage in animate_nodes_changes
function update_obj_from_info(obj, obj_info){
    let modified = false;
    for (let prop in obj_info) {
	if (obj_info[prop] != obj[prop]) {
            obj[prop] = obj_info[prop];
            modified = true;
	}
    }
    return modified;
}

//////////////////////////////
let MapPhone = function(phone_spec) {
    this.id = phone_spec['id'];
    this.i = phone_spec['i'];
    this.j = phone_spec['j'];
    let coords = livemap_geometry.grid_to_canvas(this.i, this.j);
    this.x = coords[0];
    this.y = coords[1];

    this.text = function(){
	if (this.airplane_mode == 'on')
	    return livemap_options.icon_plane_content;
	else if (this.airplane_mode == 'off')
	    return livemap_options.icon_phone_content;
	else
	    return livemap_options.icon_question_content;
    }

}

//////////////////////////////
// nodes are dynamic
// their visual rep. get created through d3 enter mechanism
let MapNode = function (node_spec) {
    this.id = node_spec['id'];
    // i and j refer to a logical grid
    this.i = node_spec['i'];
    this.j = node_spec['j'];
    // compute actual coordinates
    let coords = livemap_geometry.grid_to_canvas (this.i, this.j);
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
	let radius = this.node_status_radius();
	let delta = this.text_offset(radius);
	return this.x + ((radius == 0) ? 0 : (radius + delta));
    }
    this.text_y = function() {
	if ( ! this.is_available()) return this.y;
	let radius = this.node_status_radius();
	let delta = this.text_offset(radius);
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
	    return livemap_options.radius_ko;
	// does not even ping
	else if (this.control_ping != 'on')
	    return livemap_options.radius_warming;
	// pings but cannot get ssh
	else if (this.control_ssh != 'on')
	    return livemap_options.radius_pinging;
	// ssh is answering
	else
	    return livemap_options.radius_ok;
    }

    // right now this is visible only for intermediate radius
    // let's show some lightgreen for the 2/3 radius (ssh is up)
    this.text_color = function() {
	return '#555';
    }

    // luckily this is not rendered when a filter is at work
    this.node_status_color = function() {
	let radius = this.node_status_radius();
	return (radius == livemap_options.radius_pinging) ? d3.rgb('#71edb0').darker() :
	    (radius == livemap_options.radius_warming) ? d3.rgb('#f7d8dd').darker() :
	    '#bbb';
    }

    // showing an image (or not, if filter is undefined)
    // depending on the OS
    this.node_status_filter = function() {
	let filter_name;
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
    this.has_usrp = function() {
	return (this.usrp_type || 'none') != 'none';
    }
    this.usrp_status_display = function() {
	return (this.has_usrp()) ? "on" : "none";
    }

    this.usrp_status_filter = function() {
	let filter_name;
	if ( ! this.has_usrp() )
	    return undefined;
	else if (this.usrp_on_off == 'on')
	    filter_name = 'gnuradio-logo-icon-green';
	else if (this.usrp_on_off == 'off')
	    filter_name = 'gnuradio-logo-icon-red';
	else
	    return undefined;
	return "url(#" + filter_name + ")";
    }

    // the radius of the circle that we need to leave free
    this.overall_radius = function() {
	let r = this.node_status_radius();
	if (! this.is_available())
	    return r;
	// node is off, we need to keep space for the label
	if (r == 0)
	    return 10;
	return r;
    }

    // 0.7 stands for sin(pi/2)
    this.usrp_offset_x = function() {
	let {usrp_delta_x} = livemap_options;
	return this.overall_radius() * 0.7 + usrp_delta_x;
    }
    this.usrp_offset_y = function() {
	let {usrp_delta_y} = livemap_options;
	return this.overall_radius() * 0.7 + usrp_delta_y;
    }
    this.usrp_x = function() {
	return this.x + this.usrp_offset_x(); }
    this.usrp_y = function() {
	return this.y - (this.usrp_offset_y() + this.usrp_h()); }
    this.usrp_w = function() {
	let {usrp_width, usrp_on_ratio, usrp_off_ratio} = livemap_options;
	return usrp_width * (this.usrp_on_off == "on" ? usrp_on_ratio : usrp_off_ratio); }
    this.usrp_h = function() {
	let {usrp_height, usrp_on_ratio, usrp_off_ratio} = livemap_options;
	return usrp_height * (this.usrp_on_off == "on" ? usrp_on_ratio : usrp_off_ratio); }

}

let get_obj_id = function(node) {return node.id;}

//////////////////////////////
function LiveMap() {
    let canvas_x = livemap_geometry.room_x() + 2 * livemap_options.margin_x;
    let canvas_y = livemap_geometry.room_y() + 2 * livemap_options.margin_y;
    let svg =
	d3.select('div#livemap_container')
	.append('svg')
	.attr('width', canvas_x)
	.attr('height', canvas_y)
    ;
    // we insert a g to flip the walls upside down
    // too lazy to rewrite this one
    let g =
	svg.append('g')
	.attr('id', 'walls_upside_down')
	.attr('transform', 'translate(' + canvas_x + ',' + canvas_y + ')' + ' ' +  'rotate(180)')
    ;

    let walls = g.append('path')
	.attr('d', livemap_geometry.walls_path())
	.attr('id', 'walls')
	.attr('fill', '#fdfdfd')
	.call(livemap_geometry.walls_style)
    ;

    let {pillar_radius} = livemap_options;

    livemap_geometry.pillar_specs.forEach(function(spec) {
	let coords = livemap_geometry.grid_to_canvas(spec.i, spec.j);
	svg.append('rect')
	    .attr('id', 'pillar-' + spec.id)
	    .attr('class', 'pillar')
	    .attr('x', coords[0] - pillar_radius)
	    .attr('y', coords[1] - pillar_radius)
	    .attr('width', 2*pillar_radius)
	    .attr('height', 2*pillar_radius)
	    .attr('fill', '#101030')
	    .call(livemap_geometry.walls_style)
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
	let mapnode_specs = livemap_geometry.mapnode_specs;
	for (let i=0; i < mapnode_specs.length; i++) {
	    this.nodes[i] = new MapNode(mapnode_specs[i]);
	}
    }

    //////////////////// phones
    this.init_phones = function () {
	this.phones = [];
	let mapphone_specs = livemap_geometry.mapphone_specs;
	for (let i=0; i < mapphone_specs.length; i++) {
	    this.phones[i] = new MapPhone(mapphone_specs[i]);
	}
    }

    //////////////////// nodes
    this.handle_nodes_json = function(json) {
	let livemap = this;
	return this.handle_incoming_json(
	    "node", this.nodes, json,
	    function() { livemap.animate_nodes_changes();});
    }

    this.handle_phones_json = function(json) {
	let livemap = this;
	return this.handle_incoming_json(
	    "phone", this.phones, json,
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
	    let infos = JSON.parse(json);
	    livemap_debug(`*** ${new Date()} Received info about ${infos.length} ${type}(s)`,
			  infos)
	    // first we write this data into the MapNode structures
	    let livemap = this;
	    infos.forEach(function(info) {
		let id = info['id'];
		let obj = locate_by_id(list_objs, id);
		if (obj != undefined)
		    update_obj_from_info(obj, info);
		else
		    console.log(`livemap: could not locate ${type} id ${id} - ignored`);
	    });
	    callback();
	} catch(err) {
	    console.log(`*** Could not handle news for ${type} - ignored JSON has ${json.length} chars`);
	    console.log(err.stack);
	    console.log("***");
	}
    }

    //////////////////// the nodes graphical layout
    this.animate_nodes_changes = function() {
	let svg = d3.select('div#livemap_container svg');
	let animation_duration = 750;
	let circles = svg.selectAll('circle.node-status')
	    .data(this.nodes, get_obj_id);
	// circles show the overall status of the node
	circles
	  .enter()
	    .append('circle')
	    .attr('class', 'node-status')
	    .attr('id', function(node){return node.id;})
	    .attr('cx', function(node){return node.x;})
	    .attr('cy', function(node){return node.y;})
	    .on('click', function() {
		// call an external function (located in info-nodes.js)
		// to show de nodes details
		info_nodes(this.id)
	    })
          .merge(circles)
	    .transition()
	    .duration(animation_duration)
	    .attr('r', function(node){return node.node_status_radius();})
	    .attr('fill', function(node){return node.node_status_color();})
	    .attr('filter', function(node){return node.node_status_filter();})
	;

	// labels show the nodes numbers
	let labels = svg.selectAll('text')
	    .data(this.nodes, get_obj_id);

	labels
	  .enter()
	    .append('text')
	    .attr('class', 'node-label')
	    .text(get_obj_id)
	    .attr('x', function(node){return node.x;})
	    .attr('y', function(node){return node.y;})
	    .attr('id', function(node){return node.id;})
	    .on('click', function() {
		//call a external function (located in info-nodes.js)
		// to show de nodes details
		info_nodes(this.id)
	    })
	  .merge(labels)
	    .transition()
	    .duration(animation_duration)
	    .attr('fill', function(node){return node.text_color();})
	    .attr('x', function(node){return node.text_x();})
	    .attr('y', function(node){return node.text_y();})
	;

	// how to display unavailable nodes
	let unavailables = svg.selectAll('circle.unavailable')
	    .data(this.nodes, get_obj_id);
	unavailables
	  .enter()
	    .append('circle')
	    .attr('class', 'unavailable')
	    .attr('cx', function(node){return node.x;})
	    .attr('id', function(node){return node.id;})
	    .attr('cy', function(node){return node.y;})
	    .attr('r', function(node){return livemap_options.radius_unavailable;})
	    .on('click', function() {
		//call a external function (located in info-nodes.js)
		// to show de nodes details
		info_nodes(this.id)
	    })
	  .merge(unavailables)
	    .transition()
	    .duration(animation_duration)
	    .attr('display', function(node){
		return node.unavailable_display();})
	;

	// these rectangles are placeholders for the various icons
	// that are meant to show usrp status
	let usrp_rects = svg.selectAll('rect.usrp-status')
	    .data(this.nodes, get_obj_id);
	usrp_rects
	  .enter()
	    .append('rect')
	    .attr('class', 'usrp-status')
	    .attr('id', function(node){return node.id;})
	    .attr('stroke-width', '1px')
	    .attr('x', function(node){return node.usrp_x();})
	    .attr('y', function(node){return node.usrp_y();})
	  .merge(usrp_rects)
	    .transition()
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
        let defs = d3.select("#livemap_container svg defs");
        let filter = defs.append("filter")
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
	livemap_debug("in animate_phones_changes");
	let svg = d3.select('div#livemap_container svg');
	let animation_duration = 850;

	let w = 20;
	let h = 20;
	let r = 2;
	let squares = svg.selectAll('rect.phone-status')
	    .data(this.phones, get_obj_id);
	// simple square repr. for now, with an airplane in the middle
	squares
	  .enter()
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

	let texts = svg.selectAll('text.phone-status')
	    .data(this.phones, get_obj_id);

	texts
	  .enter()
	    .append('text')
	    .attr('class', 'phone-status')
	    .attr('x', function(phone){return phone.x;})
	    .attr('y', function(phone){return phone.y;})
	    .attr('dy', h*.1)
	    .attr('font-family', 'FontAwesome')
	    .attr('font-size', h*1)
	    .attr('textLength', w*.8)
	    .attr('lengthAdjust', 'spacingAndGlyphs')
          .merge(texts)
	    .transition()
	    .duration(.5)
	    .text(function(phone){ return phone.text();})
	;

    }

    //////////////////// socket.io business
    this.init_sidecar_socket_io = function() {
	livemap_debug(`livemap is connecting to sidecar server at ${sidecar_url}`);
	this.sidecar_socket = io(sidecar_url);
	// what to do when receiving news from sidecar
	let { chan_nodes, chan_nodes_request,
	      chan_phones, chan_phones_request} = livemap_options.channels;
	let lab = this;
	////////// nodes
	livemap_debug(`arming callback on channel ${chan_nodes}`);
	this.sidecar_socket.on(chan_nodes, function(json){
            lab.handle_nodes_json(json);
	});
	// request the first complete copy of the sidecar db
	livemap_debug(`requesting complete status on channel ${chan_nodes_request}`);
	this.sidecar_socket.emit(chan_nodes_request, 'INIT');
	////////// phones
	livemap_debug(`arming callback on channel ${chan_phones}`);
	this.sidecar_socket.on(chan_phones, function(json){
            lab.handle_phones_json(json);
	});
	// request the first complete copy of the sidecar db
	livemap_debug(`requesting complete status on channel ${chan_phones_request}`);
	this.sidecar_socket.emit(chan_phones_request, 'INIT');
    }

}

// autoload
// again, recording this unique instance in the_livemap
// is for debugging convenience only 
$(function() {
    the_livemap = new LiveMap();
    the_livemap.init();
})
