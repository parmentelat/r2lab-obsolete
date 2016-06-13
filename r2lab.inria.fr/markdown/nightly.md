<script type="text/javascript" src="/assets/r2lab/omfrest.js"></script>
<script>
var get_file = function() {
  var request = {
    "file" : 'nigthly'
  };
  post_omfrest_request('/files/get', request, function(xhttp) {
    if (xhttp.readyState == 4 && xhttp.status == 200) {
      var answer = JSON.parse(xhttp.responseText);
      $.each(answer, function (index, value) {
        console.log(value);
      });
    }
  });
}

get_file();

</script>
