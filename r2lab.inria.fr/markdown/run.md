title: R2lab Experimenter Page
tab: run
skip_header: yes
require_login: true

<!-- in a first implementation, we were creating the webchat iframe upon page load
     it was suboptimal though, as e.g. freenode being down would cause our page to hang
     so now the chat plugin comes in 2 parts, one for the actual chat area,
     and one for the button to enable it -->
<script type="text/javascript" src="/assets/r2lab/chat.js"></script>
<style type="text/css"> @import url("/assets/r2lab/chat.css"); </style>
<div id="chat-container"></div>

<div class="container">
 <div class="row">
  <div class="col-md-12">
   <div id='messages' style="display: none" class="" role="alert">
    <a class="close" onclick="$('.alert').hide()">×</a>
   </div>
   <div id='loading' style="display: none" class="alert alert-info" role="alert">
    <strong>Be patient!</strong> Loading information from server...
   </div>
  </div>
 </div>
 <br />
 <div class="row" id="all">
  <div class="col-md-2 no-padding" >
<!-- the button to access slices_keys_modal -->
<< include r2lab/slices-keys-button.html >>
    <div id="my-slices" class="run"></div>
    <div style="clear:both"></div>
   </div>
  </div>
  <div class="col-md-3 leases-run-width">
   <div id="liveleases_container" class="run"></div>
   <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.18.1/moment.min.js"></script>
   <script type="text/javascript" src="/assets/js/moment-round.js"></script>
   <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js"></script>
   <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/fullcalendar/3.4.0/fullcalendar.min.js"></script>
   <style type="text/css"> @import url("https://cdnjs.cloudflare.com/ajax/libs/fullcalendar/3.4.0/fullcalendar.min.css"); </style>

   <style type="text/css"> @import url("/assets/r2lab/liveleases.css"); </style>
   <script type="text/javascript" src="/assets/r2lab/xhttp-django.js"></script>
   <script type="text/javascript" src="/assets/r2lab/liveleases.js"></script>
   <div id="current-slice" data-current-slice-color="#000"></div>
  </div>
  <div class="col-md-7">
   <div id="livemap_container">Click a node for more details;
    see also <a href="status.md#livemap:legend">this page for a legend</a>
    <span id="chat-button"></span>
   </div>
   <script type="text/javascript" src="/assets/r2lab/livemap.js"></script>
   <style type="text/css"> @import url("/assets/r2lab/livemap.css"); </style>
   <script>
    // override livemap default settings 
    Object.assign(livemap_options, {
      space_x : 72,
      space_y : 87,
      radius_unavailable : 21,
      radius_ok : 16,
      radius_pinging : 10,
      radius_warming : 4,
      radius_ko : 0,
      margin_x : 5,
      margin_y : 20,
      padding_x : 35,
      padding_y : 35,
//    debug : true,
   });
  </script>
  <div id="actions"></div>
 </div>
</div>

  <hr/>
  See also <a href="status.md#livetable:legend">this page for a legend</a>; try clicking anywhere in the header or footer to focus on nodes of interest.

  <div class="row">
    <div class="col-md-12">
      <br/>
      <table class="table table-condensed" id='livetable_container'> </table>
      <script type="text/javascript" src="/assets/r2lab/livecolumns.js"></script>
      <script type="text/javascript" src="/assets/r2lab/livetable.js"></script>
    <script>
    // override livetable default settings 
    Object.assign(livetable_options, {
    //      debug : true,
    });
    </script>
      <style type="text/css"> @import url("/assets/r2lab/livecolumns.css"); </style>
      <style type="text/css"> @import url("/assets/r2lab/livetable.css"); </style>
    </div>
  </div>    
</div>

<!-- defines slices_keys_modal -->
<< include r2lab/slices-keys-modal.html >>

<!-- defines node_details_modal -->
<< include r2lab/nodes-details-modal.html >>
