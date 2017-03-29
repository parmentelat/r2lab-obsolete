/* would need something cleaner .. */
var delete_key = function(uuid) {
    console.log("would delete key id " + uuid);
}

$(document).ready(function() {

    var display_keys = function(domid) {
	var body = $("#" + domid);
	body.html("<div class='row key-header'>"
		  + "<div class='col-md-1'>Id</div>"
                  + "<div class='col-md-9'>Public Key</div>"
                  + "<div class='col-md-2'>&nbsp;</div>"
                  + "</div>");
	body.append("<div class='row'>"
		    + "ADD KEY BUTTON HERE"
		    + "</div>");
	post_xhttp_django('/keys/get', {}, function(xhttp) {
	    if (xhttp.readyState == 4 && xhttp.status == 200) {
		var keys = JSON.parse(xhttp.responseText);
		if (keys) {
		    keys.forEach(function(key){
			var ssh_key = key['ssh_key'];
			var uuid = key['uuid'];
			var delete_button = "<a href='#' rel='tooltip' title='delete'>"
			    + "<span class='fa fa-remove in-red' onClick=delete_key('" + uuid + "')></span>"
			    + "</a>";
			body.append("<div class='row'>"
				    + "<div class='col-md-1'>" + uuid + "</div>"
				    + "<div class='col-md-9 key-detail'>" + ssh_key + "</div>"
				    + "<div class='col-md-2'>" + delete_button + "</div>"
				    + "</div>");
			$('a').tooltip();
		    })
		} else {
		    body.append("<div class='row in-red'>No known key for now !</div>");
		}
	    }
	})
    }

    function main(){
	display_keys("list-keys");
    }

    main();
});
