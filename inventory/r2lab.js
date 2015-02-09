/* output from r2lab.py */
node_specs=[
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
pillar_specs=[
{ id: 'left', i:3, j:1 },
{ id: 'right', i:5, j:1 },
];

/* set to 0 to keep only node ids (remove coords) */
verbose = 1;
verbose = 0;

/******************************/
/* the space around the walls in the canvas */
offset_x=40;
offset_y=40;

/* distance between nodes */
space_x = 70;
space_y = 80;
/* distance between nodes and walls */
margin_x = 20;
margin_y = 20;
/* total number of rows and columns */
steps_x = 8;
steps_y = 4;

/* the attributes for drawing the walls 
   as well as the inside of the room */
walls_attr=
    {
        gradient: '90-#526c7a-#64a0c1',
        stroke: '#3b4449',
        'stroke-width': 5,
        'stroke-linejoin': 'round',
        rotation: -90
    };
/* the attributes of nodes */
node_radius = 8;
node_attr={fill:'white'};

/* the attributes of the pillars */
pillar_radius = 12;
pillar_attr = walls_attr;

/* intermediate - the overall room size */
room_x = steps_x*space_x + 2*margin_x;
room_y = steps_y*space_y + 2*margin_y;

function grid_to_canvas (i, j) {
    return [i*space_x+offset_x+margin_x,
	    (steps_y-j)*space_y+offset_y+margin_y];
}

/******************************/
function Node (node_spec) {
    this.id = node_spec['id'];
    /* i and j refer to a logical grid */
    this.i = node_spec['i'];
    this.j = node_spec['j'];

    /* compute actual coordinates */
    var coords = grid_to_canvas (this.i, this.j);
    this.x = coords[0];
    this.y = coords[1];
    
    this.graphic = function(paper) {
	var node = paper.circle(this.x, this.y,
				       node_radius, node_radius);
	node.attr (node_attr);
	var id = this.id;
	node.click(function(){
	    console.log("Clicked on node "+id);
	});
	var label = ""; label += this.id;
	if (verbose) label += "["+ this.i + "x" + this.j+"]";
	var label_obj = paper.text(this.x+10, this.y+10, label);
	return node;
    }

    return this;

}
    
function Pillar(pillar_spec) {
    this.id = pillar_spec['id'];
    /* i and j refer to a logical grid */
    this.i = pillar_spec['i'];
    this.j = pillar_spec['j'];
    var coords = grid_to_canvas(this.i, this.j);
    this.x = coords[0];
    this.y = coords[1];

    this.graphic = function(paper) {
	var pillar = paper.rect (this.x-pillar_radius, this.y-pillar_radius,
			     2*pillar_radius, 2*pillar_radius);
	pillar.attr(pillar_attr);
	var id = this.id;
	pillar.click(function(){
	    console.log("Clicked on pillar "+id);
	});
	return pillar;
    }

    return this;
}


/******************************/
/* our mental model is y increase to the top, not to the bottom */
function line_x(x) {return "l " + x + " 0 ";}
function line_y(y) {return "l 0 " + -y + " ";}

function walls_path() {
    var path="";
    path += "M " + (room_x+offset_x) + " " + (room_y+offset_y) + " ";
    path += line_x(-(7*space_x+2*margin_x));
    path += line_y(3*space_y);
    path += line_x(-1*space_x);
    path += line_y(space_y+2*margin_y);
    path += line_x(2*space_x+2*margin_x);
    path += line_y(-space_y);
    path += line_x(4*space_x-2*margin_x);
    path += line_y(space_y);
    path += line_x(2*space_x+2*margin_x);
    path += "z";
    return path;
}

/******************************/
function r2lab() {
    var canvas_x = room_x +2*offset_x;
    var canvas_y = room_y +2*offset_y;
    var paper = new Raphael(document.getElementById('canvas_container'),
			    canvas_x, canvas_y, offset_x, offset_y);

    if (verbose) console.log("canvas_x = " + canvas_x);

    var walls = paper.path(walls_path());
    walls.attr(walls_attr);

    var pillar_len = pillar_specs.length;
    for (var i=0; i < pillar_len; i++) {
	pillar = Pillar(pillar_specs[i]);
	pillar.graphic(paper);
    }


    var node_len = node_specs.length;
    for (var i=0; i < node_len; i++) {
	node = Node(node_specs[i]);
	node.graphic(paper);
    }
	
}

window.onload = function() {
    r2lab();
}
