title: R2lab Experimenter Page
tab: run
skip_header: yes
require_login: true

<!-- turn it off because freenode is down and that causes the page to hang -->
<!--<div id="chat-container"></div>-->
<script type="text/javascript" src="/assets/r2lab/chat.js"></script>
<style type="text/css"> @import url("/assets/r2lab/chat.css"); </style>

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
    <div class="col-md-2 no_padding" >
      <div id="wrap">
        <div id="manage_slices_keys">
          <button type="button" data-toggle="modal" data-target="#slices_keys_modal"
	          class="fc-button fc-state-default fc-corner-left fc-corner-right sd">
		  slices & keys <span class='fa fa-gear'></span>
	  </button>
        </div>
        <div id="my-slices"></div>
        <div style="clear:both"></div>
      </div>
    </div>
    <div class="col-md-3 personal_col">
      <div id="calendar"></div>
      <script type="text/javascript" src="/assets/js/moment.min.js"></script>
      <script type="text/javascript" src="/assets/js/moment-round.js"></script>
      <script type="text/javascript" src="/assets/js/jquery-ui.fullcalendar-custom.min.js"></script>
      <script type="text/javascript" src="/assets/js/fullcalendar.min.js"></script>
      <script type="text/javascript" src="/assets/js/jquery.cookie-v141.min.js"></script>
      <style type="text/css"> @import url("/assets/css/fullcalendar.css"); </style>

      <style type="text/css"> @import url("/assets/r2lab/liveleases-common.css"); </style>
      <style type="text/css"> @import url("/assets/r2lab/liveleases-run.css"); </style>
      <script type="text/javascript" src="/assets/r2lab/xhttp-django.js"></script>
      <script type="text/javascript" src="/assets/r2lab/liveleases-common.js"></script>      
      <script type="text/javascript" src="/assets/r2lab/liveleases-run.js"></script>
      <div id="current-slice" data-current-slice-color="#000"></div>
    </div>
    <div class="col-md-7">
    <div id="livemap_container">Click a node for more details;
    see also <a href="status.md#livemap:legend">this page for a legend</a></div>
    <script type="text/javascript" src="/assets/r2lab/livemap.js"></script>
    <style type="text/css"> @import url("/assets/r2lab/livemap.css"); </style>
    <script>
//    livemap_show_rxtx_rates = true;
    livemap_space_x = 72;
    livemap_space_y = 87;
    livemap_radius_unavailable = 21;
    livemap_radius_ok = 16;
    livemap_radius_pinging = 10;
    livemap_radius_warming = 4;
    livemap_radius_ko = 0;
    livemap_margin_x = 5;
    livemap_margin_y = 20;
    livemap_padding_x = 35;
    livemap_padding_y = 35;
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
      <script type="text/javascript" src="/assets/r2lab/livetable.js"></script>
      <script>
      //livetable_show_rxtx_rates = true;
      </script>
      <style type="text/css"> @import url("/assets/r2lab/livetable.css"); </style>
    </div>
  </div>    
</div>

<!-- defines slices_keys_modal -->
<< include r2lab/slices-keys-modal.html >>

<!-- defines node_details_modal -->
<< include r2lab/nodes-details-modal.html >>
