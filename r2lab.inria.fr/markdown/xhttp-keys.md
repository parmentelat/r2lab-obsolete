skip_header: True
---

This is a temporary page to demonstrate and test how to post key-action requests back to the django server

This is a unit test; all data is hard-coded in the page itself

See also `keys/views.py`

<!-- this exposes the getCookie function -->
<script type="text/javascript" src="/assets/r2lab/xhttp-django.js"></script>

<h1>List</h1>

<div id="get-key"><p>Click this paragraph to list the keys for hard-wired user</p>
<p id='get-keys'>Result here</p>
</div>

<script>
var get_keys = function() {
    var request = {
    /* empty record for get_keys; user is deduced from logged-in user */
    }
    post_xhttp_django('/keys/get/', request, function(xhttp) {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            console.log(xhttp.responseText);
	    var rendered_keys = "<ul>";
	    // decoding
	    var keys = JSON.parse(xhttp.responseText);
	    keys.forEach(function(key){
	       rendered_keys += "<li>[id=" + key['key_id'] + "]<br/>" + key['key'] + "</li>";
	    })
            $("#get-keys").html(rendered_keys);
	    
	    console.log("answer=" + xhttp.responseText);
      }});
}
$(function(){$('#get-key').click(get_keys);})
</script>

******************************

<h1>Add</h1>

<label class="btn btn-primary" for="my-file-selector">
    <input id="my-file-selector"
    type="file" style="display:none;" onchange="$('#upload-file-info').html($(this).val());">
    Select public key file 
</label>
<span class='label label-info' id="upload-file-info"></span>

<h3>Contents of the file:</h3>
<pre id="file-content"></pre>

<h3>AddKey result</h3>
<span id="add-response"></span>


<script>
// an example of how to add a key
function displayContents(contents) {
  $('#file-content').html(contents);
}
var add_key = function(key) {
    displayContents(key);
    var request = { "key" : key };
    post_xhttp_django('/keys/add', request, function(xhttp) {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            document.getElementById("add-response").innerHTML = xhttp.responseText;
	    // decoding
	    var answer = JSON.parse(xhttp.responseText);
	    console.log("answer=" + answer);
	    added_key_uuid = answer['uuid'];
	}})
}
function addKeyFromFile(e) {
  var file = e.target.files[0];
  if (!file) {
    console.log("addKeyFromFile - missed");
    return;
  }
  console.log("addKeyFromFile");
  var reader = new FileReader();
  reader.onload = function(e) {
    var key = e.target.result;
    add_key(key);
  };
  reader.readAsText(file);
}
$(function(){document.getElementById('my-file-selector').addEventListener('change', addKeyFromFile, false)});
</script>


******************************

<h1>Delete</h1>

---
<div id="delete-key"><p>Click this paragraph to delete the just-added key</p>
<p id='delete-response'>Result here</p>
</div>

<script>
// an example of how to delete a key
var delete_key = function() {
    var request = { "uuid" : added_key_uuid };
    post_xhttp_django('/keys/delete', request, function(xhttp) {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
          document.getElementById("delete-response").innerHTML = xhttp.responseText;
	  // decoding
	  var answer = JSON.parse(xhttp.responseText);
	  console.log(answer);
      }});
}
$(function(){$('#delete-key').click(delete_key);})
</script>
