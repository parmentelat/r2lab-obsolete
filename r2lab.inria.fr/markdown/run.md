title: R2lab Experimenter Page
tab: run
skip_header: yes
float_menu_template: r2lab/float_menu-slices.html

# Warning : this page is work in progress !

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
  <div class="row" id="all" style="display: none">
    <div class="col-md-2">
      <div id="wrap">
        <div id="my-slices">
          <h4 align="center">drag & drop slices</h4>
        </div>
        <div style="clear:both"></div>
      </div>
    </div>
    <div class="col-md-4">
      <div id="calendar"></div>
      <style type="text/css"> @import url("/plugins/liveleases/css/fullcalendar.css"); </style>
      <script type="text/javascript" src="/plugins/liveleases/js/moment.min.js"></script>
      <script type="text/javascript" src="/plugins/liveleases/js/jquery-ui.custom.min.js"></script>
      <script type="text/javascript" src="/plugins/liveleases/js/fullcalendar.min.js"></script>
      <style type="text/css"> @import url("/plugins/liveleases/css/calendar.css"); </style>
      <script type="text/javascript" src="/plugins/liveleases/js/calendar.js"></script>
      <div id="current-slice" data-current-slice-color="#000" data-current-slice-name="onelab.inria.mario.script"></div>
    </div>
    <div class="col-md-6">
    <div id="livemap_container"></div>
    <script type="text/javascript" src="/plugins/livemap.js"></script>
    <script>
    livemap_show_rxtx_rates = true;
    livemap_space_x = livemap_space_y = 60;
    livemap_radius_unavailable = 18;
    livemap_radius_ok = 13.5;
    livemap_radius_pinging = 9;
    livemap_radius_warming = 4.5;
    livemap_radius_ko = 0;
    livemap_margin_x = 5;
    livemap_margin_y = 5;

    livemap_padding_x = 40;
    livemap_padding_y = 40;
    </script>
    <style type="text/css"> @import url("/plugins/livemap.css"); </style>
    <div id="actions"></div>
    </div>
  </div>
</div>
---
<table class="table table-condensed" id='livetable_container'> </table>
<script type="text/javascript" src="/plugins/livetable.js"></script>
<script>livetable_show_rxtx_rates = true;</script>
<style type="text/css"> @import url("/plugins/livetable.css"); </style>
