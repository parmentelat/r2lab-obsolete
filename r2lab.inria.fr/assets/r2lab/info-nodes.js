// -*- js-indent-level:4 -*-

/* for eslint */
/*global $ */   
/*global getCookie */    /* from xhttp-django.js */
/*eslint no-unused-vars: ["error", { "varsIgnorePattern": "info_nodes" }]*/

"use strict";

let panel_name = 'nodes_details_modal';

function pad(str){
    let max = 2
    str = str.toString();
    str = str.length < max ? pad("0" + str, max) : str;
    return str
}

/* actually used outside of this module */
function info_nodes(node) {
    get_info(pad(node))
}


function post_request (urlpath, request, callback) {
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", urlpath, true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    let csrftoken = getCookie('csrftoken');
    xhttp.setRequestHeader("X-CSRFToken", csrftoken);
    xhttp.send(JSON.stringify(request));
    xhttp.onreadystatechange = function(){callback(xhttp);};
}


function get_info(node) {
    let request = {"file" : {'info' : node}};
    post_request('/files/get', request, function(xhttp) {
	if (xhttp.readyState == 4 && xhttp.status == 200) {
	    let info = JSON.parse(xhttp.responseText);
	    if (info) {
		show(node, info)
	    } else {
		alert("Something went wrong in recovery nodes information.")
	    }
	}
    });
}


function create_tabs() {
    $('#node_details_content').html('<ul id="nodes_tabs" class="nav nav-tabs"></ul>'
				    + '<div id="nodes_tabs_content" class="tab-content"></div>');
}


function remove_tabs() {
    $('#node_details_content').html('<br><p>No info available yet.</p>');
}


function create_slider(tab_file, tab_name) {
    let path = 'files/nodes/'
    let imgs = ''

    $.each(tab_file, function (i, file) {
	imgs = imgs + '<img data-image="'+ path + file +'">'
    });

    let tab_body = '<div id="gallery" style="display:none;">' + imgs + '</div>';

    $('#nodes_tabs').append('<li class="active"><a data-toggle="tab" href="#tab_gal">'
			    + tab_name +'</a></li>');
    $('#nodes_tabs_content').append('<div id="tab_gal" class="tab-pane fade active in"><br>'
				    + tab_body +'</div>');

    $("#gallery").unitegallery({
  	gallery_theme: "slider",
	slider_enable_zoom_panel: true,
	slider_scale_mode: "down",
    });
}


function set_info(node, info) {
    let infos   = $.parseJSON(info);
    let tabs    = 0;

    try {
	tabs = infos[node].length;
    } catch (e) {
	undefined; /* to please eslint */
    }

    if(tabs > 0)
	create_tabs();
    else
	remove_tabs();

    $('#node_details_title').html("Node <b>" + node + "</b> Technical Details");
    for(let index = 0; index < tabs; index++) {
	let active1 = '';
	let active2 = '';
	if (index == 0){
	    active1 = 'active';
	    active2 = 'in active';
	}

	let tab_name = infos[node][index]["tab"];
	let tab_file = infos[node][index]["file"];
	let tab_body = infos[node][index]["content"];

	if(tab_body == 'undefined' || tab_body == '' || tab_body == null){
	    tab_body = '<br><p>No info about this yet.</p>';
	}
	if($.isArray(tab_file)){
	    // $('#nodes_tabs').append('<li class="'+ active1 +'"><a data-toggle="tab" href="#tab_'+ index +'">'+ tab_name +'</a></li>');
	    create_slider(tab_file, tab_name)
	} else {
	    $('#nodes_tabs').append('<li class="'+ active1 +'"><a data-toggle="tab" href="#tab_'+ index +'">'+ tab_name +'</a></li>');
	    $('#nodes_tabs_content').append('<div id="tab_'+ index +'" class="tab-pane fade'+ active2 +'">'+ tab_body +'</div>');
	}
    }
}


function show(node, info) {
    set_info(node, info)
    $('#'+panel_name).modal('toggle');
}
