title: R2lab Experimenter Page
tab: run
skip_header: yes
require_login: true

<div id="chat-container"></div>
<script type="text/javascript" src="/assets/r2lab/chat.js"></script>
<style type="text/css"> @import url("/assets/r2lab/chat.css"); </style>

<div class="container">
  <div class="row">
    <div class="col-md-12">
      <div id='messages' style="display: none" class="" role="alert">
        <a class="close" onclick="$('.alert').hide()">×</a>
      </div>
      <div id='loading' style="display: none" class="alert alert-info" role="alert">
        <strong>Be patient!</strong> Loading informations from server...
      </div>
    </div>
  </div>
  <br />
  <div class="row" id="all">
    <div class="col-md-2 no_padding" >
      <div id="wrap">
        <div id="manage_slices">
          <button type="button" data-toggle="modal" data-target="#slice_modal" class="fc-button fc-state-default fc-corner-left fc-corner-right sd">manage your slices</button>
        </div>
        <div id="my-slices">
          <h4 align="center">drag & drop booking</h4>
        </div>
        <div style="clear:both"></div>
      </div>
    </div>
    <div class="col-md-3 personal_col">
      <div id="calendar"></div>
      <script type="text/javascript" src="/assets/js/moment.min.js"></script>
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
    <div id="livemap_container">Click a node for more details; see also <a href="status.md#livemap:legend">this page for a legend</a></div>
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

<!-- PARTIAL MODAL FOR SLICES - USED IN RUN OR BOOK -->
<script type="text/javascript" src="/assets/r2lab/liveslices.js"></script>
<style type="text/css"> @import url("/assets/r2lab/liveslices.css"); </style>
<div class="modal fade" id="slice_modal" tabindex="-1" role="dialog" aria-labelledby="myModalSlice">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
	  <span aria-hidden="true">&times;</span>
	</button>
        <h4 class="modal-title" id="myModalSlice">Manage Slices</h4>
      </div>
      <div class="modal-body" id="list-slices">
        ...
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
      </div>
    </div>
  </div>
</div>


<!-- PARTIAL MODAL FOR NODES DETAILS - USED IN RUN OR STATUS -->

<script type='text/javascript' src='/assets/js/ug/ug-common-libraries.js'></script>
<script type='text/javascript' src='/assets/js/ug/ug-functions.js'></script>
<script type='text/javascript' src='/assets/js/ug/ug-slider.js'></script>
<script type='text/javascript' src='/assets/js/ug/ug-sliderassets.js'></script>
<script type='text/javascript' src='/assets/js/ug/ug-touchslider.js'></script>
<script type='text/javascript' src='/assets/js/ug/ug-zoomslider.js'></script>
<script type='text/javascript' src='/assets/js/ug/ug-video.js'></script>
<script type='text/javascript' src='/assets/js/ug/ug-gallery.js'></script>
<script type='text/javascript' src='/assets/js/ug/ug-carousel.js'></script>
<script type='text/javascript' src='/assets/js/ug/ug-api.js'></script>
<link rel='stylesheet' href='/assets/css/ug/unite-gallery.css' type='text/css' />
<script type='text/javascript' src='/assets/js/ug/ug-theme-slider.js'></script>
<link rel='stylesheet' href='/assets/css/ug/ug-theme-default.css' type='text/css' />


<script type="text/javascript" src="/assets/r2lab/info_nodes.js"></script>
<div class="modal fade" id="node_details" tabindex="-1" role="dialog" aria-labelledby="myModalSlice">
  <div class="modal-dialog modal-lg" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
	  <span aria-hidden="true">&times;</span>
	</button>
        <h4 class="modal-title" id="node_details_title">Technical Details</h4>
      </div>
      <div class="modal-body" id="node_details_content">
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
      </div>
    </div>
  </div>
</div>
