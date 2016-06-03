skip_header: True
---
This is a temporary page to demonstrate and test how to post slice-action requests back to the django server

This is a unit test; all data is hard-coded in the page itself

See also `slices/view.py`

<!-- this exposes the getCookie function -->
<script type="text/javascript" src="/assets/r2lab/omfrest.js"></script>

---
<div id="get2-div"><p>Click this paragraph to get slices details (hard-wired list)</p>
<ul id='get2'><li>Results here</li></ul>
</div>

---
<div id="getall-div"><p>Click this paragraph to get the complete list of slices</p>
<ul id='getall'><li>Results here</li></ul>
</div>

<script>
// an example of how to retrieve slices
var get_slices = function(id, names) {
    var sel = "#"+id;
    var request = {};
    if (names) request['names'] = names;
    post_omfrest_request('/slices/get', request, function(xhttp) {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
	  // decoding
	  var responses = JSON.parse(xhttp.responseText);
	  $(sel+">li").remove();
	  // can come in handy to browse the structure
	  console.log("responses=", responses);
	  // but we will only show the gist of it, name and expiration
	  for (i = 0; i < responses.length; i++) {
	      var response = responses[i];
	      var slicename = response['name'];
	      var expiration = response['valid_until'];
	      var label = "name=" + slicename + ", expiration=" + expiration;
	      $(sel).append("<li>"+label+"</li>");
	      console.log(label);
	  }
      }});
}
$(function(){
  $('#get2-div').click(function() {
    get_slices("get2", [ "onelab.inria.mario.tutorial", "onelab.upmc.infocom.demo2016"])});
  $('#getall-div').click(function() {
    get_slices('getall');});
});
</script>

----
<div id="renew-div"><p>Click here to renew slice (hard-wired name)</p>
<p id='renew-response'>Result here</p>
</div>

<script>
// an example of how to renew a slice
var renew_slice = function() {
    var request = { 
    		    "name" : "onelab.inria.r2lab.naoufal",
		  };
    post_omfrest_request('/slices/renew', request, function(xhttp) {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
          document.getElementById("renew-response").innerHTML = xhttp.responseText;
	  // decoding
	  var answer = JSON.parse(xhttp.responseText);
	  console.log(answer);
      }});
}
$(function(){$('#renew-div').click(renew_slice);})
</script>
