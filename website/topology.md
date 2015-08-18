title: Topology
tab: platform
---

R2Lab testbed project offers a hight quality anechoic room for your experiments. Following are the details of the anechoic room.

###Layout

Below is the ground plan layout of the anechoic room which provide thirty-seven wireless nodes distributed in a **≈ 90m<sup>2</sup>** room.

The nodes are arranged in grid with ≈1.0m (vertical) and ≈1.15m (horizontal) of distance between them. Except by the nodes 12, 16, 17, 20 and 23, 24, 27 or the nodes sorrounding the columns room.

<center>
	<img src="assets/img/status.png" style="width:950px; height:592px;"/><br>
	Fig. 1 - Resources status
</center>

<br>

###Status
The status table below inform the availability of each node in our platform.

<div id="div_error" class="alert alert-danger" role="alert">
  One or more problem may block the proper running:<br>
</div>

<!-- MUST BE GENERATED AUTOMATICALLY -->
<table class="table table-condensed">
  <thead>
    <tr>
      <th id="t11">node</th>
      <th id="t12">availability</th>
      <th id="t13">ping</th>
      <th id="t14">on/off</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th id="t21" scope="row">10</th>
      <td id="t22"></td>
      <td id="t23"></td>
      <td id="t24"></td>
    </tr>
    <tr>
      <th id="t31" scope="row">26</th>
      <td id="t32"></td>
      <td id="t33"></td>
      <td id="t34"></td>
    </tr>
  </tbody>
</table>

#<script type="text/javascript" src="load_results.json"></script>
#<script type="text/javascript" src="reset_results.json"></script>
<script type="text/javascript" src="alive_results.json"></script>
<script type="text/javascript" src="answer_results.json"></script>
<script type="text/javascript" src="multiple_results.json"></script>

<script type="text/javascript">
  
  $("#div_error").hide()

  try {
    var data_alive_results = JSON.parse(alive_results);
    res = data_alive_results[0][10].alive
    if (res == 'alive'){
      $("#t22").append( '<span class="label label-success">available</span>' );
    }
    else{
      $("#t22").append( '<span class="label label-danger">'+res+'</span>' );
    }
  }
  catch(err) {
    $("#div_error").show();
    $("#div_error").append( '<ul><li>Alive file fails</li></ul>' );
  }

  try {
    var data_alive_results = JSON.parse(alive_results);
    res = data_alive_results[0][26].alive
    if (res == 'alive'){
      $("#t32").append( '<span class="label label-success">available</span>' );
    }
    else{
      $("#t32").append( '<span class="label label-danger">'+res+'</span>' );
    }
  }
  catch(err) {
    $("#div_error").show();
    $("#div_error").append( '<ul><li>Alive file fails</li></ul>' );
  }

  
  try {
    var data_multiple_results = JSON.parse(multiple_results);
    res = data_multiple_results[0][10].status
    if (res == 'on'){
      $("#t24").append( '<span class="label label-success">'+res+'</span>' );
    }
    else{
      $("#t24").append( '<span class="label label-danger">'+res+'</span>' );
    }
  }
  catch(err) {
    $("#div_error").show();
    $("#div_error").append( '<ul><li>Multiple file fails</li></ul>' );
  }

  try {
    var data_multiple_results = JSON.parse(multiple_results);
    res = data_multiple_results[0][26].status
    if (res == 'on'){
      $("#t34").append( '<span class="label label-success">'+res+'</span>' );
    }
    else{
      $("#t34").append( '<span class="label label-danger">'+res+'</span>' );
    }
  }
  catch(err) {
    $("#div_error").show();
    $("#div_error").append( '<ul><li>Multiple file fails</li></ul>' );
  }


  try {
    var data_answer_results = JSON.parse(answer_results);
    res = data_answer_results[0][10].answer
    if (res == 'answer'){
      $("#t23").append( '<span class="label label-success">yes</span>' );
    }
    else{
      $("#t23").append( '<span class="label label-danger">fail</span>' );
    }
  }
  catch(err) {
    $("#div_error").show();
    $("#div_error").append( '<ul><li>Answer file fails</li></ul>' );
  }

  try {
    var data_answer_results = JSON.parse(answer_results);
    res = data_answer_results[0][26].status
    if (res == 'answer'){
      $("#t33").append( '<span class="label label-success">yes</span>' );
    }
    else{
      $("#t33").append( '<span class="label label-danger">fail</span>' );
    }
  }
  catch(err) {
    $("#div_error").show();
    $("#div_error").append( '<ul><li>Answer file fails</li></ul>' );
  }

</script>
