title: R2lab Scheduler
tab: book
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
    <div class="col-md-10">
      <div id="calendar"></div>
      <script type="text/javascript" src="/assets/js/moment.min.js"></script>
      <script type="text/javascript" src="/assets/js/jquery-ui.fullcalendar-custom.min.js"></script>
      <script type="text/javascript" src="/assets/js/fullcalendar.min.js"></script>
      <script type="text/javascript" src="/assets/js/jquery.cookie-v141.min.js"></script>
      <style type="text/css"> @import url("/assets/css/fullcalendar.css"); </style>

      <style type="text/css"> @import url("/assets/r2lab/liveleases-book.css"); </style>
      <script type="text/javascript" src="/assets/r2lab/liveleases-book.js"></script>
      <div id="current-slice" data-current-slice-color="#000" data-current-slice-name="onelab.inria.mario.script"></div>
    </div>
  </div>

<br/>

<div class="alert alert-danger" role="alert" markdown="1">
**Important note!**

R2lab platform is reset every night. A time slot from **3AM** until
**4AM** is reserved to execute this routine.
All times on this website are expressed wrt the CET timezone, which is UTC+1 in winter, and UTC+2 in summer.

Please, make sure all your experiments are saved before. You can check
[here](tuto-02-shell-tools.md#main) how to do it.
</div>

</div>

