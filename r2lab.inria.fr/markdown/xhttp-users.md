skip_header: True
---
This is a temporary page to demonstrate and test how to post user-action requests back to the django server

This is a unit test; all data is hard-coded in the page itself

See also `users/view.py`

<!-- this exposes the getCookie function -->
<script type="text/javascript" src="/assets/r2lab/xhttp-django.js"></script>

---
<div id="getall-div"><p>Click this paragraph to get the complete list of users</p>
<ul id='getall'><li>Results here</li></ul>
</div>

---
<div id="get1-div"><p>Click this paragraph to get one user details (hard-wired urn)</p>
<ul id='get1'><li>Results here</li></ul>
</div>

---
<div id="getme-div"><p>Click this paragraph to get details for the logged in user</p>
<ul id='getme'><li>Results here</li></ul>
</div>

<script>
// an example of how to retrieve users
var get_users = function(id, urn) {
    var sel = "#"+id;
    var request = {};
    if (urn) request['urn'] = urn;
    post_xhttp_django('/users/get', request, function(xhttp) {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
	 // decoding
	 var responses = JSON.parse(xhttp.responseText);
	 $(sel+">li").remove();
	 // can come in handy to browse the structure
	 console.log("responses=", responses);
	 // but we will only show the gist of it, name and expiration
	 responses.forEach(function(response) {
	   var urn = response['urn'];
	   var label = "<b>urn = " + urn + "</b><ul>";
	   response['accounts'].forEach(function(account) {
	     label += "<li> in slice " + account['name'] +
	     " valid_until " + account['valid_until'] + "</li>";
	   });
	   label += "</ul>";
           $(sel).append("<li>"+label+"</li>");
           console.log(label);
         });
      }
    })
}
$(function(){
  $('#getall-div').click(function() {
    get_users('getall');});
  $('#get1-div').click(function() {
    get_users("get1", "urn:publicid:IDN+onelab:inria+user+walid_dabbous");});
  $('#getme-div').click(function() {
    get_users("getme", r2lab_hrn);});
});
</script>
