title: Statistics
tab: platform
---
<div class="container">
  <div class="row" markdown="1">
    <div class="col-md-12">
      <h3>Statistics on nodes health</h3>
      The testbed routinely runs a thorough raincheck procedure, to make
      sure that all is in order.  Historically, this was performed every
      night during the early stages; maturity is now such that we feel
      comfortable with running it only twice a week
      <a href="/book.md">see the booking page
      for details</a>.

      In any case, below is a summary of the issues found since Jan. 2016.

      <script type="text/javascript" src="/assets/r2lab/xhttp-django.js"></script>
      <script src="http://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
      <script src="/assets/js/moment.min.js"></script>
      <script src="/assets/js/underscore-min.js"></script>
      <style type="text/css"> @import url("/assets/css/daterangepicker.css"); </style>
      <script src="/assets/js/daterangepicker.js"></script>
      <script type="text/javascript" src="/assets/r2lab/range-calendar.js"></script>
      <script src="/assets/js/chartlib/src/charts/Chart.Heat.js"></script>
      <script type="text/javascript" src="/assets/r2lab/charts.js"></script>
      <style type="text/css"> @import url("/assets/r2lab/charts.css"); </style>
      <script src="/assets/js/chartlib/dist/Chart.bundle.min.js"></script>
    </div>
  </div>
</div>

<div class="container">
  <div class="row">
    <div class="col-lg-12">
      <div style="width: 100%">
        <div id="line-chart-tooltip"></div>
        <canvas id="line" height="250" width="700"></canvas>
      </div>
    </div>
    <!-- <div class="col-lg-1"> -->
      <!-- <br><br>select a range date<br>
      <input type="text" id="range_calendar" class="form-control"> -->
    <!-- </div> -->
  </div>

  <div class="row">
    <div class="col-lg-12">
      <br><br>
      <p></p>
    </div>
  </div>    

  <div class="row">
    <div class="title_heat">
      presence of issues since the <b>beginning</b> of measurements
    </div>
    <div class="col-lg-1" style="width: 10px">
      <div class="side_title">
        <img src="/assets/img/mapylegend.png" class="">
      </div>
    </div>
    <div class="col-lg-10" style="width: 83.7%">
      <div class="heat_container" style="background-image: url(/assets/img/chamber.png); background-repeat: no-repeat;">
        <canvas id="heat" width="775" height="505"></canvas>
      </div>
    </div>
    <div class="legend complete_serie"></div><div class="legend2">&nbsp;all serie</div>
    <div class="col-lg-1" style="padding-left: 0px;">
      <div class="side_title"></div>
      <div class="heat_bar">
        high
        <span class="glyphicon glyphicon-plus" aria-hidden="true"></span>
      </div>
      <div class="">
        &nbsp;<img src="/assets/img/heatlevel.png" class="heatlevel">
      </div>
      <div class="heat_bar">
        less
        <span class="glyphicon glyphicon-minus" aria-hidden="true"></span>
      </div>
    </div>
  </div>

  <div class="row">
    <div class="col-lg-12">
      <br><br>
      <p></p>
    </div>
  </div>

  <div class="row">
    <div class="title_heat">
      presence of issues since the <b>beginning</b> of measurements by issue type in percent
    </div>
    <div class="col-lg-1" style="width: 10px">
      <div class="side_title">
        <img src="/assets/img/mapylegend.png" class="">
      </div>
    </div>
    <div class="col-lg-10" style="width: 83.7%">
      <div class="heat_container" id="doughnut_container" style="background-image: url(/assets/img/chamber.png); background-repeat: no-repeat;">
      </div>
    </div>
    <div class="legend complete_serie"></div><div class="legend2">&nbsp;all serie</div>
    <div class="col-lg-1" style="padding-right: 0px; padding-left: 0px; padding-top: 4px; width: 140px;">
      <div class="side_title"></div>
      <div class="legend_intern">LEGEND</div>
      <div class="legend start"></div><div class="legend2">issue in start</div>
      <div class="legend load"></div><div class="legend2">issue in load</div>
      <div class="legend zombie"></div><div class="legend2">issue in shut off</div>
      <div class="legend noissue"></div><div class="legend2">no issues</div>
    </div>
  </div>

</div>
