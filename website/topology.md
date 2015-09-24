title: Topology
tab: platform
---

R2Lab testbed project offers a hight quality anechoic room for your experiments. Following are the details of the anechoic room.

### Layout

Below is the ground plan layout of the anechoic room which provide thirty-seven wireless nodes distributed in a **≈ 90m<sup>2</sup>** room.

The nodes are arranged in grid with ≈1.0m (vertical) and ≈1.15m (horizontal) of distance between them, except by the nodes 12, 16, 17, 20 and 23, 24, 27 which are the nodes surrounding the columns room.

<left>
	<img src="assets/img/status.png" style="width:950px; height:592px;"/><br>
	<!-- <center> Fig. 1 - Resources status</center> -->
</left>

<br>

### Livemap

Frequently a routine checks the availability of our resource/nodes platform. In order to allow real time and multiple information concerning R2lab platform, our live map keep the users posted about the state of each resource/node concerning technical infos, incidents and operational details.<br>
- The red/green round informs if the node responds or not a ping at the experiment interface.
- The round O.S. brand informs that the node is turned on and running the referenced O.S..
- The node is turned off when only the number is presented in the map.

<div id="livemap_container"></div>

<h3>Status</h3>

Complementary to the live map above, this status table present an alternative format the queries results.
- The <b>availability</b> column: 
	Reports that the node are controllable or not. In fail case the node could be physically powered off or in maintenance.
- The <b>on/off</b> column:
	Reports that the node is ready to be used or not.
- The <b>ping</b> column: 
	Reports that the node answers a single ping at the experiment interface.
- The <b>O.S</b> column:
	Reports that the node responds a ssh connection sending back the operational system release.
<br>

The table with these queries are presented below.

<div id="div_error" class="alert alert-danger" role="alert">
  One or more problem may block the proper running:<br>
</div>

<!-- MUST BE GENERATED AUTOMATICALLY -->
<table id="results_table" class="table table-condensed">
  <thead>
    <tr>
      <th id="cl_01">node<br><font style="font-weight:normal; font-size:xx-small;">last update</font></th>
      <th id="cl_02">availability</th>
      <th id="cl_03">on/off</th>
      <th id="cl_04">ping</th>
      <th id="cl_05">O.S.</th>
    </tr>
  </thead>
  <tbody id="t_body"></tbody>
</table>

<script type="text/javascript" src="info_files.json"></script>
<!-- <script type="text/javascript" src="load_results.json"></script> -->
<!-- <script type="text/javascript" src="reset_results.json"></script> -->
<script type="text/javascript" src="info_results.json"></script>
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
  //$("#results_table").show();

  try {
    var data_info_files       = JSON.parse(info_files);       // get the last update information  
    var data_alive_results    = JSON.parse(alive_results);    // alive consider the CM card
    var data_multiple_results = JSON.parse(multiple_results); // must be 'status' on Nepi
    var data_answer_results   = JSON.parse(answer_results);   // consider the answer for a single ping
    var data_info_results     = JSON.parse(info_results);     // check the SO version  
  }
  catch(err) {
    //$("#results_table").hide();
    $("#div_error").show();
    $("#div_error").append( '<ul><li>One or more file information were not loaded correctly</li></ul>' );
  }


  //Last update info at the table header
  try {
    cl_02 = data_info_files['alive_results'].last_modified;
    cl_03 = data_info_files['multiple_results'].last_modified;
    cl_04 = data_info_files['answer_results'].last_modified;
    cl_05 = data_info_files['info_results'].last_modified;

    $("#cl_02").append( '<br><font style="font-weight:normal; font-size:xx-small;">'+cl_02+'</font>');
    $("#cl_03").append( '<br><font style="font-weight:normal; font-size:xx-small;">'+cl_03+'</font>');
    $("#cl_04").append( '<br><font style="font-weight:normal; font-size:xx-small;">'+cl_04+'</font>');
    $("#cl_05").append( '<br><font style="font-weight:normal; font-size:xx-small;">'+cl_05+'</font>');
  }
  catch(err) {
    $("#div_error").show();
    $("#div_error").append( '<ul><li>Info file informations were not loaded correctly</li></ul>' );
  }

  var total_nodes = 38;
  var table_content = '';
  
  for (var key=1; key < total_nodes; key++) {
    table_content += '<tr>';

    if (key < 10)
      key = '0'+key;

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


    //Fourth column
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


    //Fifth column
    try {
      res = data_info_results[key].info;

      if (res == 'fail'){
        table_content += '<td><span class="label label-default">ignored</span></td>';
      }
      else if (res.indexOf('ubuntu') >= 0){

        table_content += 'data<td><img src="assets/img/ub.png" height="20" width="20">&nbsp;<font style="font-size:x-small;">'+res+'</font></td>';
      }
      else if (res.indexOf('fedora') >= 0){

        table_content += '<td><img src="assets/img/fd.png" height="20" width="20">&nbsp;<font style="font-size:x-small;">'+res.replace(' (twenty one)','');+'</font></td>';
      }
      
    }
    catch(err) {
      table_content += '<td><span class="label label-default">ignored</span></td>';  
    }

    table_content += '</tr>';
  }

  $("#t_body").append(table_content);

</script>

<hr />
<table class="table table-condensed livetable">
  <thead>
    <tr>
      <th></th>
      <th>Availability</th>
      <th>On/Off</th>
      <th>Ping</th>
      <th>O.S.</th>
    </tr>
  </thead>
  <!-- hook for livetable.js -->
  <tbody id="livetable_container">
    <tr>
      <td><span class="badge label-default">01</span></td>
      <td class="ok"></td>
      <td class="on"></td>
      <td class="ping_ok"></td>
      <td class="os"><img src="assets/img/ub.png" height="20" width="20"><br>ubuntu 14.10</td>
    </tr>
    <tr>
      <td><span class="badge label-default">02</span></td>
      <td class="ko"></td>
      <td class="off"></td>
      <td class="ping_ko"></td>
      <td class="os"><img src="assets/img/fd.png" height="20" width="20"><br>fedora 21</td>
    </tr>
  </tbody>
</table>


</html>
