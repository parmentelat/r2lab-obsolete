/* must be in sync with r2lab-server.js */
var sidecar_port_number = 8000;

/**** the 2 socket.io channels that are used ****/
/* this is where actual JSON status is sent */
var channel = 'r2lab-news';
/* this one is used for triggering a broadcast of the complete status */
var signalling = 'r2lab-signalling';

/* output from livemap-prep.py */
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
/* the  two pillars - this is manual */
var pillar_specs = [
{ id: 'left', i:3, j:1 },
{ id: 'right', i:5, j:1 },
];

//global - mostly for debugging and convenience
var the_r2lab;

/* set to 0 to keep only node ids (remove coords) */
var verbose = 1;
var verbose = 0;

/******************************/
/* the space around the walls in the canvas */
var margin_x = 50, margin_y = 50;

/* distance between nodes */
var space_x = 80, space_y = 80;
/* distance between nodes and walls */
var padding_x = 40, padding_y = 40;
/* total number of rows and columns */
var steps_x = 8, steps_y = 4;

/* the attributes for drawing the walls 
   as well as the inside of the room */
var walls_radius = 30, 
    walls_style =
    {
        fill: '90-#425790-#64a0c1'
	/*'90-#526c7a-#64a0c1'*/ /*'90-bbc1d0-f0d0e4'*/,
        stroke: '#3b4449',
        'stroke-width': 6,
        'stroke-linejoin': 'round',
	'stroke-miterlimit': 8
    };
/* the initial attributes of nodes */
var node_radius = 16,
    node_label_style = {
	'font-family': 'monaco',
	'font-size': 16
    }
/* free - busy */
/*
free_node_style={
    gradient: '0-#cfc-beb-cfc',
    'fill-opacity': 0.5
};
busy_node_style={
    gradient: '0-#fcc-ebb-fcc',
    'fill-opacity': 0.5
};
*/
var free_node_fill = 'lightgreen', busy_node_fill = 'red';
var on_node_radius = 18, off_node_radius = 0;

/* the attributes of the pillars */
var pillar_radius = 16,
    pillar_style = JSON.parse(JSON.stringify(walls_style));
pillar_style['fill'] = '#101030';

/* intermediate - the overall room size */
var room_x = steps_x*space_x + 2*padding_x, room_y = steps_y*space_y + 2*padding_y;

function grid_to_canvas (i, j) {
    return [i*space_x+margin_x+padding_x,
	    (steps_y-j)*space_y+margin_y+padding_y];
}

/******************************/
function Node (node_spec) {
    this.id = node_spec['id'];
    /* i and j refer to a logical grid */
    this.i = node_spec['i'];
    this.j = node_spec['j'];
    this.busy = 0;
    this.on = 1;

    /* compute actual coordinates */
    var coords = grid_to_canvas (this.i, this.j);
    this.x = coords[0];
    this.y = coords[1];
    
    this.clicked = function () {
	console.log("clicked on node " + this.id + " - tmp for dbg, this does a manual refresh");
	the_r2lab.request_complete_from_sidecar();
    }

    // initial display won't show anything about status
    // this is expected to be updated later on
    this.display = function(paper) {
	this.circle = paper.circle(this.x, this.y,
				   node_radius, node_radius);

	var label = ""; label += this.id;
	if (verbose) label += "["+ this.i + "x" + this.j+"]";
	this.label = paper.text(this.x, this.y, label);
	this.label.attr(node_label_style);

	/* setting id on the svg elts */
	this.circle.node.setAttribute('class', 'node-circle');
	this.label.node.setAttribute('class', 'node-text');

	// arm click callbacks
	var self = this;
	var clicked = function(){self.clicked();};
	this.circle.click(clicked);
	this.label.click(clicked);
    }

    /* 
       node_info is a struct coming through socket.io in JSON
       currently we know about
       {
        'id' : this is how this node instance is located
        'status' : 'on' and 'off'
        'busy' : 'busy' or 'free'
           to be extended/tweaked...
       }
    */
    this.update_from_news = function(node_info) {
	if (node_info.status != undefined)
	    this.status = (node_info.status == 'on') ? 1 : 0;
	if (node_info.busy != undefined)
	    this.busy = (node_info.busy == 'busy') ? 1 : 0;
    }
}

function Pillar(pillar_spec) {
    this.id = pillar_spec['id'];
    /* i and j refer to a logical grid */
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
	    console.log("Clicked on pillar "+id);
	});
	return pillar;
    }
}


/******************************/
/* our mental model is y increase to the top, not to the bottom 
 * also, using l (relative) instead of L (absolute) is simpler
 * but it keeps roundPathCorners from rounding.js from working fine
 * keep it this way from now, a class would help keep track here
*/
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
/*    console.log("path   ="+path);
    console.log("radius ="+walls_radius);
    path = roundPathCorners(path, walls_radius, false);
    console.log("rounded="+path);*/
    return path;
}

/******************************/
function R2Lab() {
    var canvas_x = room_x +2*margin_x;
    var canvas_y = room_y +2*margin_y;
    var paper = new Raphael(document.getElementById('canvas_container'),
			    canvas_x, canvas_y, margin_x, margin_y);

    if (verbose) console.log("canvas_x = " + canvas_x);

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
	    this.nodes[i].display(paper);
	}
    }


    this.locate_node_by_id = function(id) {
	for (var i=0; i< this.nodes.length; i++)
	    if (this.nodes[i].id == id)
		return this.nodes[i];
    }
    
    this.handle_json_status = function(json) {
	var nodes_info = JSON.parse(json);
	// first we write this data into the Node structures
	for (var i=0; i < nodes_info.length; i++) {
	    var node_info = nodes_info[i];
	    var id = node_info['id'];
	    var node = this.locate_node_by_id(id);
	    node.update_from_news(node_info);
	}
	this.animate_changes();
    }

    this.animate_changes = function() {
	console.log('animate with ' + this.nodes.length + 'nodes in this.nodes');
	var circles = d3.selectAll('.node-circle')
	    .data(this.nodes)
	    .transition()
	    .duration(500)
	    .attr('r',
		  function(node) {return node.status ? on_node_radius : off_node_radius;});
	var labels = d3.selectAll('.node-text')
	    .data(this.nodes)
	    .transition()
	    .duration(500)
	    .attr('fill',
		  function(node) {return node.busy ? busy_node_fill : free_node_fill;});
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
	/* what to do when receiving news from sidecar */
	var lab=this;
	this.sidecar_socket.on(channel, function(json){
            lab.handle_json_status(json);
	});
	this.request_complete_from_sidecar();
    }

    /* 
       request sidecar for initial status on the signalling channel
       content is not actually used by sidecar server
       could maybe send some client id instead
    */
    this.request_complete_from_sidecar = function() {
	this.sidecar_socket.emit(signalling, 'INIT');
    }
	
}

/* autoload */
$(function() {
    the_r2lab = new R2Lab();
    the_r2lab.init_nodes();
    the_r2lab.init_sidecar_socket_io();
})
