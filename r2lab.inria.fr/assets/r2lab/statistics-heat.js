$(document).ready(function() {
  var version = '1.0';



  var draw = function(data, max) {
      var heat = simpleheat('heat').data(data).max(max+.3), frame;
      //heat.radius(40, 35);//really round
      heat.radius(50, 45);
      // set gradient colors as {0.4: 'blue', 0.65: 'lime', 1: 'red'}
      // heat.gradient({0.4: 'blue', 0.65: 'lime', 1: 'red'});
      var minOpacity = 0.1;
      heat.draw(minOpacity);
      frame = null;

      var heat1 = simpleheat('heat1').data(data).max(max+.3), frame;
      heat1.radius(65, 60);
      // set gradient colors as {0.4: 'blue', 0.65: 'lime', 1: 'red'}
      // heat.gradient({0.4: 'blue', 0.65: 'lime', 1: 'red'});
      var minOpacity = 0.1;
      heat1.draw(minOpacity);
      frame = null;
  }



  var map_node = function() {
    map = [];
    var c = [38, 125, 210, 298, 383, 470, 557, 642, 729]; //columns
    var l = [45, 150, 255, 360, 463]; //lines
    var n = 0; //node
    //ignoring holes in a square map [col, line]
    var holes = ['3,1', '3,4', '4,4', '5,1', '5,4', '8,0', '8,1', '8,2'];
    $.each(c, function (cc, vc) {
      $.each(l, function (ll, vl) {
        n++;
        $.inArray(String(cc+','+ll), holes) > -1 ? n-- : map.push({'id': n, 'c':vc, 'l':vl});
      });
    });
    return map;
  }



  var build_heat_chart = function(data) {

    val = new Array(38).fill(0);
    $.each(data, function (index, value) {
      $.each(value['data'], function (i, v) {
        val[i] = val[i] + 1;
      });
    });
    var max = Math.max.apply(Math, val);

    map = map_node();
    $.each(map, function (i, v) {
      data.push([ v['c'], v['l'], val[v['id']] ]); //[[c[1],l[1], 1], ... or [col pos, lin pos, value]
    });
    draw(data, max);
  }



  var post_request = function(urlpath, request, callback) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", urlpath, true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    var csrftoken = getCookie('csrftoken');
    xhttp.setRequestHeader("X-CSRFToken", csrftoken);
    xhttp.send(JSON.stringify(request));
    xhttp.onreadystatechange = function(){callback(xhttp);};
  }



 var main = function() {
  console.log("statistics-heat version " + version);

  var request = {"file" : 'nigthly'};
  post_request('/files/get', request, function(xhttp) {
    if (xhttp.readyState == 4 && xhttp.status == 200) {
      answer = JSON.parse(xhttp.responseText);
      if (answer)
        build_heat_chart(answer);
    }
  });
 }



 main();
});
