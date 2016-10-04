panel_name = 'node_details'

function pad(str){
  max = 2
  str = str.toString();
  str = str.length < max ? pad("0" + str, max) : str;
  return str
}


function info_nodes(node) {
  get_info(pad(node))
}


function post_request (urlpath, request, callback) {
  var xhttp = new XMLHttpRequest();
  xhttp.open("POST", urlpath, true);
  xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  var csrftoken = getCookie('csrftoken');
  xhttp.setRequestHeader("X-CSRFToken", csrftoken);
  xhttp.send(request);
  xhttp.onreadystatechange = function(){callback(xhttp);};
}


function get_info(node) {
  var request = node;
  post_request('/nodes/get', request, function(xhttp) {
    if (xhttp.readyState == 4 && xhttp.status == 200) {
      info = JSON.parse(xhttp.responseText);
      if (info) {
        show(node, info)
      } else {
        alert("Something went wrong in recovery nodes information.")
      }
    }
  });
}


function create_tabs() {
  $('#node_details_content').html('<ul id="nodes_tabs" class="nav nav-tabs"></ul><div id="nodes_tabs_content" class="tab-content"></div>');
}


function remove_tabs() {
  $('#node_details_content').html('<br><p>No info available yet.</p>');
}


function create_slider(tab_file) {
  var path = 'assets/img/'
  var imgs = ''

  $.each(tab_file, function (i, file) {
    imgs = imgs + '<img data-image="'+ path + file +'">'
  });

  var tab_body = '\
  <div id="gallery" style="display:none;">\
  '+ imgs +'\
  </div>\
  ';

  $('#nodes_tabs').append('<li class=""><a data-toggle="tab" href="#tab_gal">Images Gallery</a></li>');
  $('#nodes_tabs_content').append('<div id="tab_gal" class="tab-pane fade"><br>'+ tab_body +'</div>');

  jQuery("#gallery").unitegallery({
		gallery_theme: "slider"
	});
}


function set_info(node, info) {
  var infos   = $.parseJSON(info);
  var tabs    = 0;
  var content = [];

  try {
    tabs = infos[node].length;
  } catch (e) {
    ;
  }

  if(tabs > 0)
    create_tabs();
  else
    remove_tabs();

  $('#node_details_title').html("Node <b>" + node + "</b> Thechinical Details");
  for(index = 0; index < tabs; index++) {
    var active1 = '';
    var active2 = '';
    if(index == 0){
      active1 = 'active';
      active2 = 'in active';
    }

    tab_name = infos[node][index]["tab"];
    tab_file = infos[node][index]["file"];
    tab_body = infos[node][index]["content"];

    if(tab_body == 'undefined' || tab_body == '' || tab_body == null){
      tab_body = '<br><p>No info about this yet.</p>';
    }
    $('#nodes_tabs').append('<li class="'+ active1 +'"><a data-toggle="tab" href="#tab_'+ index +'">'+ tab_name +'</a></li>');
    $('#nodes_tabs_content').append('<div id="tab_'+ index +'" class="tab-pane fade'+ active2 +'">'+ tab_body +'</div>');

    if($.isArray(tab_file)){
      create_slider(tab_file)
    }
  }
}


function show(node, info) {
  set_info(node, info)

  $('#'+panel_name).modal('toggle');
}
