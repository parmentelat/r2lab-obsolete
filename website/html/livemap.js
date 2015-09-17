////////// must be in sync with r2lab-sidecar.js 
// the 2 socket.io channels that are used
// (1) this is where actual JSON status is sent
var channel = 'r2lab-news';
// (2) this one is used for triggering a broadcast of the complete status
var signalling = 'r2lab-signalling';
// port number
var sidecar_port_number = 8000;

////////// originally output from livemap-prep.py 
var node_specs = [
{ id: 1, i:8, j:0 },
{ id: 2, i:8, j:1 },
{ id: 3, i:8, j:2 },
{ id: 4, i:8, j:3 },
{ id: 5, i:8, j:4 },
{ id: 6, i:7, j:0 },
{ id: 7, i:7, j:1 },
{ id: 8, i:7, j:2 },
{ id: 9, i:7, j:3 },
{ id: 10, i:7, j:4 },
{ id: 11, i:6, j:0 },
{ id: 12, i:6, j:1 },
{ id: 13, i:6, j:2 },
{ id: 14, i:6, j:3 },
{ id: 15, i:6, j:4 },
{ id: 16, i:5, j:0 },
{ id: 17, i:5, j:2 },
{ id: 18, i:5, j:3 },
{ id: 19, i:4, j:0 },
{ id: 20, i:4, j:1 },
{ id: 21, i:4, j:2 },
{ id: 22, i:4, j:3 },
{ id: 23, i:3, j:0 },
{ id: 24, i:3, j:2 },
{ id: 25, i:3, j:3 },
{ id: 26, i:2, j:0 },
{ id: 27, i:2, j:1 },
{ id: 28, i:2, j:2 },
{ id: 29, i:2, j:3 },
{ id: 30, i:2, j:4 },
{ id: 31, i:1, j:0 },
{ id: 32, i:1, j:1 },
{ id: 33, i:1, j:2 },
{ id: 34, i:1, j:3 },
{ id: 35, i:1, j:4 },
{ id: 36, i:0, j:3 },
{ id: 37, i:0, j:4 },
];

// the  two pillars - this is manual
var pillar_specs = [
{ id: 'left', i:3, j:1 },
{ id: 'right', i:5, j:1 },
];

//global - mostly for debugging and convenience
var the_r2lab;

//////////////////// configuration
// the space around the walls in the canvas
var margin_x = 50, margin_y = 50;

// distance between nodes
var space_x = 80, space_y = 80;
// distance between nodes and walls
var padding_x = 40, padding_y = 40;
// total number of rows and columns
var steps_x = 8, steps_y = 4;

//// static area 
// walls and inside
var walls_radius = 30, 
    walls_style =
    {
        fill: 'fdfdfd',
	//'90-#526c7a-#64a0c1'
	//'90-bbc1d0-f0d0e4'
        stroke: '#3b4449',
        'stroke-width': 6,
        'stroke-linejoin': 'round',
	'stroke-miterlimit': 8
    };

// pillars - derived from the walls
var pillar_radius = 16,
    pillar_style = JSON.parse(JSON.stringify(walls_style));
pillar_style['fill'] = '#101030';

//// nodes


////////////////////////////////////////
// the overall room size
var room_x = steps_x*space_x + 2*padding_x, room_y = steps_y*space_y + 2*padding_y;

// translate i, j into actual coords
function grid_to_canvas (i, j) {
    return [i*space_x + margin_x + padding_x,
	    (steps_y-j)*space_y + margin_y + padding_y];
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
    path += "M " + (room_x+margin_x) + " " + (room_y+margin_y) + " ";
    path += line_x(-(7*space_x+2*padding_x));
    path += line_y(3*space_y);
    path += line_x(-1*space_x);
    path += line_y(space_y+2*padding_y);
    path += line_x(2*space_x+2*padding_x);
    path += line_y(-space_y);
    path += line_x(4*space_x-2*padding_x);
    path += line_y(space_y);
    path += line_x(2*space_x+2*padding_x);
    path += "Z";
    return path;
}

//////////////////////////////
// pillars are static and get created in a procedural fashion using raphael
function Pillar(pillar_spec) {
    this.id = pillar_spec['id'];
    // i and j refer to a logical grid
    this.i = pillar_spec['i'];
    this.j = pillar_spec['j'];
    var coords = grid_to_canvas(this.i, this.j);
    this.x = coords[0];
    this.y = coords[1];

    this.display = function(paper) {
	var pillar = paper.rect (this.x-pillar_radius, this.y-pillar_radius,
			     2*pillar_radius, 2*pillar_radius);
	pillar.attr(pillar_style);
	var id = this.id;
	pillar.click(function(){
	    console.log("Clicked on pillar " + this.id + " - tmp for dbg, this does a manual refresh");
	    the_r2lab.request_complete_from_sidecar();
	});
	return pillar;
    }
}

//////////////////////////////
// nodes are dynamic
// their visual rep. get created through d3 enter mechanism
var Node = function (node_spec) {
    this.id = node_spec['id'];
    // i and j refer to a logical grid 
    this.i = node_spec['i'];
    this.j = node_spec['j'];
    // compute actual coordinates
    var coords = grid_to_canvas (this.i, this.j);
    this.x = coords[0];
    this.y = coords[1];
    
    // status details are filled upon reception of news

    // node_info is a dict coming through socket.io in JSON
    // simply copy the fieds present in this dict in the local object
    // for further usage in animate_changes
    this.update_from_news = function(node_info) {
	for (var prop in node_info)
	    if (node_info[prop] != undefined)
		this[prop] = node_info[prop];
	// prepare a 4-items data list for ticks
	// the order is important
	this.rxtx = [ this.wlan0_rx_rate, this.wlan0_tx_rate,
		      this.wlan1_rx_rate, this.wlan1_tx_rate, ];
    }

    this.is_alive = function() {
	return this.cmc_on_off == 'on'
	    && this.control_ping == 'on'
	    && this.os_release != 'fail';
    }

    // shift label south-east a little
    // we cannot just add a constant to the radius
    this.text_offset = function(radius) {
	return Math.max(5, 12-radius/2);
    }
    this.text_x = function() {
	var radius = this.radius();
	var delta = this.text_offset(radius);
	return this.x + ((radius == 0) ? 0 : (radius + delta));
    }	    
    this.text_y = function() {
	var radius = this.radius();
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
    this.radius = function() {
	var node_radius_ok = 18,
	    node_radius_pinging = 12,
	    node_radius_warming = 6,
	    node_radius_ko = 0;
	// completely off
	if (this.cmc_on_off == 'off')
	    return node_radius_ko;
	// does not even ping
	else if (this.control_ping == 'off')
	    return node_radius_warming;
	// pings but cannot get ssh
	else if (this.os_release == 'fail')
	    return node_radius_pinging;
	// ssh is answering
	else
	    return node_radius_ok;
    }

    // right now this is visible only for intermediate radius
    // let's show some lightgreen for the 2/3 radius (ssh is up)
    this.text_color = function() {
	return '#555';
    }

    // luckily this is not rendered when a filter is at work
    this.circle_color = function() {
	var radius = this.radius();
	return (radius == 12) ? '#71edb0' :
	    (radius == 6) ? '#f7d8dd' : '#bbb';
//	var fedora_color = '#05285e',
//	    ubuntu_color = '#de4915',
//	    unknown_color = '#ccc';
//	if (this.os_release.indexOf('fedora') >= 0)
//	    return fedora_color;
//	else if (this.os_release.indexOf('ubuntu') >= 0)
//	    return ubuntu_color;
//	else return unknown_color;
    }

    // showing an image (or not, if filter is undefined)
    // depending on the OS
    this.circle_filter = function() {
	var filter_name;
	if (this.os_release.indexOf('other') >= 0)
	    filter_name = 'other_logo';
	else if (this.os_release.indexOf('fedora') >= 0)
	    filter_name = 'fedora_logo';
	else if (this.os_release.indexOf('ubuntu') >= 0)
	    filter_name = 'ubuntu_logo';
	else 
	    return undefined;
	return "url(#" + filter_name + ")";
    }

}

var ident = function(d) { return d; };
var get_node_id = function(node) {return node.id;}

//////////////////////////////
function R2Lab() {
    var canvas_x = room_x + 2 * margin_x;
    var canvas_y = room_y + 2 * margin_y;
    var paper = new Raphael(document.getElementById('livemap_container'),
			    canvas_x, canvas_y, margin_x, margin_y);

    this.walls = paper.path(walls_path());
    this.walls.attr(walls_style);

    this.pillars=[];
    this.nb_pillars = pillar_specs.length;
    for (var i=0; i < this.nb_pillars; i++) {
	this.pillars[i] = new Pillar(pillar_specs[i]);
	this.pillars[i].display(paper);
    }

    this.node_specs = node_specs;
    this.nb_nodes = node_specs.length;
    this.nodes = [];

    this.init_nodes = function () {
	for (var i=0; i < this.nb_nodes; i++) { 
	    this.nodes[i] = new Node(node_specs[i]);
	}
    }


    this.locate_node_by_id = function(id) {
	for (var i=0; i< this.nodes.length; i++)
	    if (this.nodes[i].id == id)
		return this.nodes[i];
    }
    
    this.handle_json_status = function(json) {
	// xxx somehow we get nois in the mix
	if (json == "") {
	    console.log("Bloops..");
	    return;
	}
	try {
	    var nodes_info = JSON.parse(json);
	    // first we write this data into the Node structures
	    for (var i=0; i < nodes_info.length; i++) {
		var node_info = nodes_info[i];
		var id = node_info['id'];
		var node = this.locate_node_by_id(id);
		node.update_from_news(node_info);
	    }
	    this.animate_changes();
	} catch(err) {
	    console.log("Could not apply news - ignored  - JSON=<<" + json + ">>");
	    console.log(err.stack);
	}
    }

    this.animate_changes = function() {
	var svg = d3.select('div#livemap_container svg');
	var circles = svg.selectAll('circle')
	    .data(this.nodes, get_node_id);
	circles.enter()
	    .append('circle')
	    .attr('class', 'node-circle')
	    .attr('cx', function(node){return node.x;})
	    .attr('cy', function(node){return node.y;})
	;
	circles
	    .transition()
	    .duration(500)
	    .attr('r', function(node){return node.radius();})
	    .attr('stroke', function(node){return node.circle_color();})
	    .attr('filter', function(node){return node.circle_filter();})
	    .attr('opacity', .5)
	;
	var labels = svg.selectAll('text')
	    .data(this.nodes, get_node_id);
	labels.enter()
	    .append('text')
	    .attr('class', 'node-label')
	    .text(get_node_id)
	    .attr('x', function(node){return node.x;})
	    .attr('y', function(node){return node.y;})
	;
	labels
	    .transition()
	    .duration(1000)
	    .attr('fill', function(node){return node.text_color();})
	    .attr('x', function(node){return node.text_x();})
	    .attr('y', function(node){return node.text_y();})
	;

	var ticks_groups = svg.selectAll('g.ticks')
	    .data(this.nodes, get_node_id);
	ticks_groups.enter()
	    .append('g')
	    .attr("transform",
		  function(node){ return "translate(" + node.x + "," + node.y + ")";})
	    .attr('class', 'ticks')
	;
	ticks_groups
	    .attr('display', function(node) {
		return node.is_alive() ? "on" : "none";
	    })
	;
	var ticks = ticks_groups.selectAll('rect')
	    .data(function(node){return node.rxtx;});
	ticks.enter()
	    .append('rect')
	    .attr('class', function(d, i) {return 'rxtx' + i;})
	    .attr('width',3)
	    .attr('x', function(node){return node.x;})
	    .attr('y', function(node){return node.y;})
	    .attr('stroke', '#bbb')
	    .attr('fill', '#fff')
	;
	var alpha = 70;
	ticks
	    .transition()
	    .duration(100)
	// this might be undefined, but should still work 
	    .attr('height', ident)
	// each rxtx tick is included in a <g> already at the right position
	// we set a rotate angle to get the desired effect
	// + a translation that puts the tick off the center
	// compute angle
	// 0 : 90-alpha
	// 1 : 90+alpha
	// 2 & 3 : 0 & 1 + 180 resp.
	    .attr('transform',
		  function(data, i){
		      var even = i%2 ? 1 : -1;
		      var half_rounds = Math.floor(i/2);
		      var angle = (90+even*(90-alpha)) + half_rounds*180;
		      return "rotate(" + angle + ")" + " translate(0, 22)";})
	;
	;
    }

    // filters nice_float(for background)s
    this.declare_image_filter = function (id_filename) {
//	console.log('decl. fil. ' + id_filename);
	// create defs element if not yet present
	if ( ! $('#livemap_container svg defs').length) {
	    console.log("creating defs");
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
	    .attr("xlink:href", id_filename + ".png");
    }

    this.declare_image_filter('fedora_logo');
    this.declare_image_filter('ubuntu_logo');
    this.declare_image_filter('other_logo');

    ////////// socket.io business
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
    the_r2lab = new R2Lab();
    the_r2lab.init_nodes();
    the_r2lab.init_sidecar_socket_io();
})
