/* would need something cleaner .. */
$(document).ready(function() {

    var display_keys = function(domid) {
	var keysdiv = $("#" + domid);
	// create 1 div for the list of keys, and one for the add-key button
	var id_list = "keyslist-" + domid;
	var id_add = "keyadd-" + domid;
	keysdiv.html("<div id='" + id_list + "'>");
	keysdiv.append("<div id='" + id_add + "'>");
	var div_list = $("#" + id_list);
	var div_add = $("#" + id_add);
	// header for the list of keys
	div_list.append("<div class='row key-header'>"
			+ "<div class='col-md-10'>Public Key</div>"
			+ "<div class='col-md-2'>&nbsp;</div>"
			+ "</div>");
	div_add.html("<div class='row'>"
		     + "<div class='col-md-12 add-key-area'>"
		     + "<label class='btn btn-primary' for='key-file-selector'>"
		     + "<input id='key-file-selector' type='file' style='display:none;'>"
		     + "Select public key file to add"
		     + "</label>"
		     + "</div>"
		     + "</div>");
	document.getElementById('key-file-selector').addEventListener('change', add_key_from_file, false);

	post_xhttp_django('/keys/get', {}, function(xhttp) {
	    if (xhttp.readyState == 4 && xhttp.status == 200) {
		var keys = JSON.parse(xhttp.responseText);
		if (keys.length) {
		    keys.forEach(function(key){
			var ssh_key = key['ssh_key'];
			var uuid = key['uuid'];
			var delete_id = "delete-key-" + uuid;
			var delete_button = "<span class='fa fa-remove in-red' data-toggle='tooltip' title='delete'"
			    + "id='" + delete_id + "'></span>";
			div_list.append("<div class='row'>"
					+ "<div class='col-md-10 key-detail'>" + ssh_key + "</div>"
					+ "<div class='col-md-2'>" + delete_button + "</div>"
					+ "</div>");
			$("#"+delete_id).click(function() { delete_key(uuid);});
		    })
		} else {
		    div_list.append("<div class='row in-red'>You have no known key yet, please upload one !</div>");
		}
	    }
	    $('[data-toggle="tooltip"]').tooltip();
	});
    }


    var delete_key = function(key_uuid) {
	var request = { "uuid" : key_uuid };
	post_xhttp_django('/keys/delete', request, function(xhttp) {
	    if (xhttp.readyState == 4 && xhttp.status == 200) {
		display_keys("livekeys-container");
		// decoding
		var answer = JSON.parse(xhttp.responseText);
		console.log("answer from /keys/delete");
		console.log(answer);
	    }});
    }

    var add_key_from_file = function(e) {
	var file = e.target.files[0];
	if (!file) {
	    console.log("add_key_from_file - missed");
	    return;
	}
	var reader = new FileReader();
	reader.onload = function(e) {
	    var key = e.target.result;
	    add_key(key);
	};
	reader.readAsText(file);
    }

    var add_key = function(key) {
	var request = { "key" : key };
	post_xhttp_django('/keys/add', request, function(xhttp) {
            if (xhttp.readyState == 4 && xhttp.status == 200) {
		display_keys("livekeys-container");
		// decoding
		var answer = JSON.parse(xhttp.responseText);
		console.log("answer from /keys/add");
		console.log(answer);
	    }})
    }

    function main(){
	display_keys("livekeys-container");
    }


    main();
});
