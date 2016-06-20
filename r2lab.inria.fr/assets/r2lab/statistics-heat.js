window.requestAnimationFrame = window.requestAnimationFrame || window.mozRequestAnimationFrame ||
                               window.webkitRequestAnimationFrame || window.msRequestAnimationFrame;


var heat = simpleheat('heat').data(data).max(20),
    frame;

function draw() {
    heat.radius(45, 35);
    // set gradient colors as {0.4: 'blue', 0.65: 'lime', 1: 'red'}
    // heat.gradient({0.4: 'blue', 0.65: 'lime', 1: 'red'});
    var minOpacity = 0.1;
    heat.draw(minOpacity);
    frame = null;
}

draw();
