/* output from r2lab.py */
id_to_coord=[
{ id: 1, x:8, y:0 },
{ id: 2, x:8, y:1 },
{ id: 3, x:8, y:2 },
{ id: 4, x:8, y:3 },
{ id: 5, x:8, y:4 },
{ id: 6, x:7, y:0 },
{ id: 7, x:7, y:1 },
{ id: 8, x:7, y:2 },
{ id: 9, x:7, y:3 },
{ id: 10, x:7, y:4 },
{ id: 11, x:6, y:0 },
{ id: 12, x:6, y:1 },
{ id: 13, x:6, y:2 },
{ id: 14, x:6, y:3 },
{ id: 15, x:6, y:4 },
{ id: 16, x:5, y:0 },
{ id: 17, x:5, y:2 },
{ id: 18, x:5, y:3 },
{ id: 19, x:4, y:0 },
{ id: 20, x:4, y:1 },
{ id: 21, x:4, y:2 },
{ id: 22, x:4, y:3 },
{ id: 23, x:3, y:0 },
{ id: 24, x:3, y:2 },
{ id: 25, x:3, y:3 },
{ id: 26, x:2, y:0 },
{ id: 27, x:2, y:1 },
{ id: 28, x:2, y:2 },
{ id: 29, x:2, y:3 },
{ id: 30, x:2, y:4 },
{ id: 31, x:1, y:0 },
{ id: 32, x:1, y:1 },
{ id: 33, x:1, y:2 },
{ id: 34, x:1, y:3 },
{ id: 35, x:1, y:4 },
{ id: 36, x:0, y:3 },
{ id: 37, x:0, y:4 },
];

/* set to 0 to keep only node ids (remove coords) */
verbose = 1;
verbose = 0;

/******************************/
offset_x=40;
offset_y=40;

space_x = 70;
space_y = 80;
margin_x = 20;
margin_y = 20;
steps_x = 8;
steps_y = 4;

total_x = steps_x*space_x + 2*margin_x;
total_y = steps_y*space_y + 2*margin_y;

walls_attr=
    {
        gradient: '90-#526c7a-#64a0c1',
        stroke: '#3b4449',
        'stroke-width': 5,
        'stroke-linejoin': 'round',
        rotation: -90
    };
node_radius = 8;
node_attr={fill:'white'};

pillar_radius = 12;
pillar_attr = walls_attr;

/* our mental model is y increase to the top, not to the bottom */
function line_x(x) {return "l " + x + " 0 ";}
function line_y(y) {return "l 0 " + -y + " ";}

function walls_path() {
    var path="";
    path += "M " + (total_x+offset_x) + " " + (total_y+offset_y) + " ";
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

function pillar(paper,i,j) {
    var coord = node_coord(i, j);
    var x=coord[0]; var y=coord[1];
    var pillar = paper.rect (x-pillar_radius, y-pillar_radius,
			     2*pillar_radius, 2*pillar_radius);
    pillar.attr(pillar_attr);
    return pillar;
}


function node_coord (i, j) {
    return [i*space_x+offset_x+margin_x, (steps_y-j)*space_y+offset_y+margin_x];
}

function node(paper,id, i,j) {
    var coord = node_coord(i, j);
    var x=coord[0]; var y=coord[1];
    var node_circle = paper.circle(x, y, node_radius, node_radius);
    node_circle.attr (node_attr);
    node_circle.click(function(){
	console.log("Clicked on node "+id);
    });
    var label = ""; label += id;
    if (verbose) label += "["+ i + "x" + j+"]";
    var label_obj = paper.text(x+10, y+10, label);
    return node_circle;
}
    

/******************************/
function r2lab() {
    var canvas_x = total_x +2*offset_x;
    var canvas_y = total_y +2*offset_y;
    var paper = new Raphael(document.getElementById('canvas_container'),
			    canvas_x, canvas_y, offset_x, offset_y);

    if (verbose) console.log("canvas_x = " + canvas_x);

    var walls = paper.path(walls_path());
    walls.attr(walls_attr);

    pillar_right = pillar(paper, 5, 1);
    pillar_left = pillar(paper, 3, 1);


    /* draw a whole grid 
    for (var i=0; i<=steps_x; i++)
	for (var j=0; j<=steps_y; j++)
	    node(paper,i,j);
    */
    var node_len = id_to_coord.length;
    for (var i=0; i < node_len; i++) {
	node_dict=id_to_coord[i];
	node(paper, node_dict['id'], node_dict['x'], node_dict['y']);
    }
	
}

window.onload = function() {
    r2lab();
}
