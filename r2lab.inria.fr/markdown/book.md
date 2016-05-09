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
          <h4 align="center">drag & drop booking</h4>
        </div>
        <div style="clear:both"></div>
      </div>
      <div id="manage_slices">
        <a href="#" data-toggle="modal" data-target="#slice_modal">manage your slices</a>
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
      <script type="text/javascript" src="/assets/r2lab/omfrest.js"></script>
      <script type="text/javascript" src="/assets/r2lab/liveleases-book.js"></script>
      <div id="current-slice" data-current-slice-color="#000" data-current-slice-name="onelab.inria.mario.script"></div>
    </div>
  </div>

  <!-- PARTIAL MODAL FOR SLICES - USED IN RUN OR BOOK -->
  <script type="text/javascript" src="/assets/r2lab/liveslices.js"></script>
  <style type="text/css"> @import url("/assets/r2lab/liveslices.css"); </style>
  <div class="modal fade" id="slice_modal" tabindex="-1" role="dialog" aria-labelledby="myModalSlice">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
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

<br/>

<div class="alert alert-danger" role="alert" markdown="1">
<strong>Important note!</strong>
<br/>
R2lab platform is reset every night. A time slot from <strong>3 a.m.</strong> until
<strong>5 a.m.</strong> is reserved to execute this job.
All times on this website are expressed wrt the <strong>CET timezone</strong>, which is UTC+1 in winter, and UTC+2 in summer.

<br/>
In any case, please make sure to save your experiments once you are done, as the next user will probably reload an image on your nodes.
</div>

</div>
