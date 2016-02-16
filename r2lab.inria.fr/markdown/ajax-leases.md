---
This is a temporary page to demonstrate how to post lease-action requests back to the django server

---
<div id="ajax-lease"><p>Click this paragraph to POST a fake JSON request to the /leases/add/ URL</p>
<p id='response'>Result will show up here (see <code>leases/view.py</code>)</p>
</div>

<!-- this exposes the getCookie function -->
<script type="text/javascript" src="/plugins/ajax-leases.js"></script>

<script>
// an example of how to create a lease
var ajax_lease = function() {
    var request = { 
    		    "slicename" : 'onelab.inria.mario.tutorial',
                    "valid_from": "2016-02-16T22:30:00Z",
                    "valid_until": "2016-02-16T23:00:00Z"
		    };
    post_lease_request('add', request, function(xhttp) {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
          document.getElementById("response").innerHTML = xhttp.responseText;
	  // decoding
	  var answer = JSON.parse(xhttp.responseText);
	  console.log("message = " + answer['message']);
      }});
}
$(function(){$('#ajax-lease').click(ajax_lease);})
</script>
