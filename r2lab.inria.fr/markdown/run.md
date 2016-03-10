title: R2lab Experimenter Page
tab: run
skip_header: yes
<!--float_menu_template: r2lab/float-menu-slices.html-->

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
    <div class="col-md-2">
      <div id="wrap">
        <div id="my-slices">
          <h4 align="center">drag & drop slices</h4>
        </div>
        <div style="clear:both"></div>
      </div>
    </div>
    <div class="col-md-3 personal_col">
      <div id="calendar"></div>
      <script type="text/javascript" src="/assets/js/moment.min.js"></script>
      <script type="text/javascript" src="/assets/js/jquery-ui.fullcalendar-custom.min.js"></script>
      <script type="text/javascript" src="/assets/js/fullcalendar.min.js"></script>
      <style type="text/css"> @import url("/assets/css/fullcalendar.css"); </style>

      <style type="text/css"> @import url("/assets/r2lab/liveleases.css"); </style>
      <script type="text/javascript" src="/assets/r2lab/liveleases.js"></script>
      <div id="current-slice" data-current-slice-color="#000" data-current-slice-name="onelab.inria.mario.script"></div>
    </div>
    <div class="col-md-7">
    <div id="livemap_container"></div>
    <script type="text/javascript" src="/assets/r2lab/livemap.js"></script>
    <style type="text/css"> @import url("/assets/r2lab/livemap.css"); </style>
    <script>
    livemap_show_rxtx_rates = true;
    livemap_space_x = livemap_space_y = 60;
    livemap_radius_unavailable = 24;
    livemap_radius_ok = 18;
    livemap_radius_pinging = 12;
    livemap_radius_warming = 6;
    livemap_radius_ko = 0;
    livemap_margin_x = 5;
    livemap_margin_y = 20;
    livemap_padding_x = 87;
    livemap_padding_y = 87;
    </script>
    <div id="actions"></div>
    </div>
  </div>
  <div class="row">
    <div class="col-md-12">
      <br/>
      <table class="table table-condensed" id='livetable_container'> </table>
      <script type="text/javascript" src="/assets/r2lab/livetable.js"></script>
      <script>livetable_show_rxtx_rates = true;</script>
      <style type="text/css"> @import url("/assets/r2lab/livetable.css"); </style>
    </div>
  </div>    
</div>
