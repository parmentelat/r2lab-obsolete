skip_header: True
---
This is a temporary page to demonstrate and test how to post slice-action requests back to the django server

This is a unit test; all data is hard-coded in the page itself

See also `slices/view.py`

<!-- this exposes the getCookie function -->
<script type="text/javascript" src="/assets/r2lab/omfrest.js"></script>

---
<div id="get-slice"><p>Click this paragraph to get slices details (hard-wired list)</p>
<p id='add-response'>Result here</p>
</div>

<script>
// an example of how to retrieve slices
var get_slice = function() {
    var request = {
       "names" : [ "onelab.testwd.another_slice", "onelab.upmc.infocom.demo2016"],
	    };
    post_omfrest_request('/slices/get', request, function(xhttp) {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
	  // decoding
	  var responses = JSON.parse(xhttp.responseText);
	  // can come in handy to browse the structure
	  console.log(responses);
	  // but we will only show the gist of it, name and expiration
	  names = [];
	  for (i=0; i<responses.length; i++) {
	      var response = responses[i];
	      slicename = response['resource_response']['resource']['name'];
	      expiration = response['resource_response']['resource']['valid_until'];
              names = names + " " + slicename + "[ -> " + expiration + "]";
	  }
	  $("#add-response").html(names);
      }});
}
$(function(){$('#get-slice').click(get_slice);})
</script>

---
<div id="update-slice"><p>Click this paragraph to update the just-added slice</p>
<p id='update-response'>Result here</p>
</div>

<script>
// an example of how to update a slice
var update_slice = function() {
    var request = { 
    		    "uuid" : added_slice_uuid,
                    "valid_from": "2016-02-20T11:00:00Z",
                    "valid_until": "2016-02-20T12:00:00Z"
		    };
    post_omfrest_request('/slices/update', request, function(xhttp) {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
          document.getElementById("update-response").innerHTML = xhttp.responseText;
	  // decoding
	  var responses = JSON.parse(xhttp.responseText);
	  console.log(responses);
      }});
}
$(function(){$('#update-slice').click(update_slice);})
</script>



---
<div id="delete-slice"><p>Click this paragraph to delete the just-added slice</p>
<p id='delete-response'>Result here</p>
</div>

<script>
// an example of how to delete a slice
var delete_slice = function() {
    var request = { 
    		    "uuid" : added_slice_uuid,
		    };
    post_omfrest_request('/leases/delete', request, function(xhttp) {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
          document.getElementById("delete-response").innerHTML = xhttp.responseText;
	  // decoding
	  var responses = JSON.parse(xhttp.responseText);
	  console.log(responses);
      }});
}
$(function(){$('#delete-slice').click(delete_slice);})
</script>
