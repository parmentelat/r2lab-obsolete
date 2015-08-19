title: Topology
tab: platform
---

R2Lab testbed project offers a hight quality anechoic room for your experiments. Following are the details of the anechoic room.

###Layout

Below is the ground plan layout of the anechoic room which provide thirty-seven wireless nodes distributed in a **≈ 90m<sup>2</sup>** room.

The nodes are arranged in grid with ≈1.0m (vertical) and ≈1.15m (horizontal) of distance between them. Except by the nodes 12, 16, 17, 20 and 23, 24, 27 or the nodes surrounding the columns room.

<center>
	<img src="assets/img/status.png" style="width:950px; height:592px;"/><br>
	Fig. 1 - Resources status
</center>

<br>

###Status
Frequently a routine checks the availability of our resource/nodes platform. Three items are checked: if the node is available correctly (availability column); if the node answer a single ping (ping column); which are the node status (on/off column). <br>
The status table of these queries are presented below.

<div id="div_error" class="alert alert-danger" role="alert">
  One or more problem may block the proper running:<br>
</div>

<!-- MUST BE GENERATED AUTOMATICALLY -->
<table class="table table-condensed">
  <thead>
    <tr>
      <th>node</th>
      <th>availability</th>
      <th>ping</th>
      <th>on/off</th>
    </tr>
  </thead>
  <tbody id="t_body"></tbody>
</table>

<!-- <script type="text/javascript" src="load_results.json"></script> -->
<!-- <script type="text/javascript" src="reset_results.json"></script> -->
<script type="text/javascript" src="alive_results.json"></script>
<script type="text/javascript" src="answer_results.json"></script>
<script type="text/javascript" src="multiple_results.json"></script>

<script type="text/javascript">
  
  Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
  };

  $("#div_error").hide();

  try {
    var data_alive_results    = JSON.parse(alive_results);    // alive consider the CM card
    var data_multiple_results = JSON.parse(multiple_results); // must be 'status' on Nepi
    var data_answer_results   = JSON.parse(answer_results);   // answer consider the answer for a single ping 
  }
  catch(err) {
    $("#div_error").show();
    $("#div_error").append( '<ul><li>One or more file information were not loaded correctly</li></ul>' );
  }

  var total_nodes = 38;
  var table_content = '';
  
  for (var key=1; key < total_nodes; key++) {
    table_content += '<tr>';
    
    //Fist column
    table_content += '<th scope="row">'+ key +'</th>';

    //Second column
    try {
      res = data_alive_results[key].alive;  
      
      if (res == 'alive'){
        table_content += '<td><span class="label label-success">available</span></td>';
      }
      else {
        table_content += '<td><span class="label label-danger">unavailable</span></td>';
      }
    }
    catch(err) {
      table_content += '<td><span class="label label-default">ignored</span></td>';  
    }

    //Third column
    try {
      res = data_answer_results[key].answer;

      if (res == 'answer'){
        table_content += '<td><span class="label label-success">yes</span></td>';
      }
      else {
        table_content += '<td><span class="label label-danger">fail</span></td>';
      }
    }
    catch(err) {
      table_content += '<td><span class="label label-default">ignored</span></td>';  
    }

    //Fourth column
    try {
      res = data_multiple_results[key].status;

      if (res == 'on'){
        table_content += '<td><span class="label label-success">on</span></td>';
      }
      else if (res == 'off'){
        table_content += '<td><span class="label label-danger">off</span></td>';
      }
      else {
        table_content += '<td><span class="label label-warning">unreachable</span></td>';
      }
    }
    catch(err) {
      table_content += '<td><span class="label label-default">ignored</span></td>';  
    }

    table_content += '</tr>';
  }

  $("#t_body").append(table_content);

</script>
