$(document).ready(function() {
  var version = '1.0';


  function sortObject(o) {
    //console.log(Object.keys(o).map(Number).sort((a,b)=>a-b));
    // console.log(Object.keys(o).sort().reduce((r, k) => (r[k] = o[k], r), {}));
    // return Object.keys(o).sort().reduce((r, k) => (r[k] = o[k], r), {});
    return Object.keys(o).sort();
  }


  function post_request (urlpath, request, callback) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", urlpath, true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    var csrftoken = getCookie('csrftoken');
    xhttp.setRequestHeader("X-CSRFToken", csrftoken);
    xhttp.send(JSON.stringify(request));
    xhttp.onreadystatechange = function(){callback(xhttp);};
  }


  function get_detail() {
    var request = {"file" : 'detail'};
    post_request('/files/get', request, function(xhttp) {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
        info = JSON.parse(xhttp.responseText);
        if (info) {
          show(info)
        } else {
          alert("Something went wrong in recovery nodes information.")
        }
      }
    });
  }


  function ext(str) {
    return str.split('.').pop();
  }


  function has_attr(infos, node, attr){
    var found = [false, false];
    $.each(info[node], function (id, val) {
      if(val['attribute'] == attr){
        found = [true, val['value']];
        return;
      }
    });
    return found;
  }


  function pad(str){
    max = 2
    str = str.toString();
    str = str.length < max ? pad("0" + str, max) : str;
    return str
  }


  function show(infos) {
    var thead = []
    var order = sortObject(infos);
    var table = ''
    var head  = ''
    var body  = ''

    $("#comparative").html('');
    if(order.length == 0){
      $("#comparative").html('<tr><td>no info available yet</td></tr>');
    }

    $.each(order, function (id, val) {
      $.each(infos[val], function (i, v) {
        thead.push($.trim(v['attribute']));
      });
    });
    thead = $.unique(thead.sort());

    head =  '<tr class="dt_head">';
    head += '<th>Node</th>';
    $.each(thead, function (id, val) {
      head += '<th>'+ val +'</th>'
    });
    head += '<th><span style="cursor: pointer; color: #525252;" alt="reset nodes" onclick="reset_node();"><span class="glyphicon glyphicon-repeat text-success" aria-hidden="true"></span></span></th>';
    head += '</tr>';

    $.each(order, function (id, node) {
      body += '<tr id="line_'+node+'" class="">';
      body += '<td style="font:15px helveticaneue, Arial, Tahoma, Sans-serif;"><span class="custom-badge" onclick="info_nodes('+pad(node)+');">'+node+'</span></td>'

      // body += '<td class="dt_left"><span class="badge" onclick="info_nodes('+node+');">'+ node +'</span></td>';
      $.each(thead, function (i, attr) {

        res = has_attr(infos, node, attr);
        if(res[0]) {
          if($.inArray(ext(res[1]), ['jpg', 'png', 'jpeg']) !== -1) {
            body += '<td class="dt_value">'+ res[1] +'</td>';
            //body += '<td class="dt_value"><a href="#">'+ res[1] +'</a></td>';
          }
          else{
            body += '<td class="dt_value">'+ res[1] +'</td>';
          }
        } else {
          body += '<td>-</td>';
        }
      });
      body += '<td><span style="cursor: pointer; color: #525252;" alt="remove node" onclick="remove_node('+node+');"><span class="glyphicon glyphicon-trash red" aria-hidden="true"></span></span></td>';
      body += '</tr>';
    });

    table = '<thead>'+head+'</thead>'+'<tbody>'+body+'</tbody>'
    $("#comparative").append(table)
  }


  function main() {
    console.log("get nodes details version " + version);
    get_detail();
  }


  main();
});

function show_image(img) {
  $('#big_image_content').html('<img src="'+img+'">');
  $('#big_photo').modal('toggle');
}

function remove_node(node) {
  $('#line_'+pad(node)).removeClass('show-line');
  $('#line_'+pad(node)).addClass('hide-line');
}

function reset_node() {
  $('[id^=line_]').removeClass('hide-line');
  $('[id^=line_]').addClass('show-line');
}