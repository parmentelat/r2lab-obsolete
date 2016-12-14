skip_header: True
---
This is a temporary page to demonstrate and test how to post lease-action requests back to the django server

This is a unit test; all data is hard-coded in the page itself

See also `leases/view.py`

<!-- this exposes the getCookie function -->
<script type="text/javascript" src="/assets/r2lab/xhttp-django.js"></script>

---
<div id="add-lease"><p>Click this paragraph to add a lease</p>
<p id='add-response'>Result here</p>
</div>

<script>
var added_lease_uuid;
// an example of how to add a lease
var add_lease = function() {
    var request = { 
    		    "slicename" : 'onelab.inria.r2lab.admin',
                    "valid_from": "2016-02-20T08:00:00Z",
                    "valid_until": "2016-02-20T09:00:00Z"
		    };
    post_xhttp_django('/leases/add', request, function(xhttp) {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
          document.getElementById("add-response").innerHTML = xhttp.responseText;
	  // decoding
	  var answer = JSON.parse(xhttp.responseText);
	  console.log(answer);
	  added_lease_uuid = answer['uuid'];
	  console.log("stored uuid = " + added_lease_uuid);
      }});
}
$(function(){$('#add-lease').click(add_lease);})
</script>



---
<div id="update-lease"><p>Click this paragraph to update the just-added lease</p>
<p id='update-response'>Result here</p>
</div>

<script>
// an example of how to update a lease
var update_lease = function() {
    var request = { 
    		    "uuid" : added_lease_uuid,
                    "valid_from": "2016-02-20T11:00:00Z",
                    "valid_until": "2016-02-20T12:00:00Z"
		    };
    post_xhttp_django('/leases/update', request, function(xhttp) {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
          document.getElementById("update-response").innerHTML = xhttp.responseText;
	  // decoding
	  var answer = JSON.parse(xhttp.responseText);
	  console.log(answer);
      }});
}
$(function(){$('#update-lease').click(update_lease);})
</script>



---
<div id="delete-lease"><p>Click this paragraph to delete the just-added lease</p>
<p id='delete-response'>Result here</p>
</div>

<script>
// an example of how to delete a lease
var delete_lease = function() {
    var request = { 
    		    "uuid" : added_lease_uuid,
		    };
    post_xhttp_django('/leases/delete', request, function(xhttp) {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
          document.getElementById("delete-response").innerHTML = xhttp.responseText;
	  // decoding
	  var answer = JSON.parse(xhttp.responseText);
	  console.log(answer);
      }});
}
$(function(){$('#delete-lease').click(delete_lease);})
</script>



