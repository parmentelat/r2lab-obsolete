title: R2lab Statistics
tab: status
skip_header: yes

<script type="text/javascript" src="/assets/r2lab/omfrest.js"></script>
<script src="http://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
<script src="/assets/js/moment.min.js"></script>
<script src="/assets/js/underscore-min.js"></script>
<style type="text/css"> @import url("/assets/css/daterangepicker.css"); </style>
<script src="/assets/js/daterangepicker.js"></script>
<script type="text/javascript" src="/assets/r2lab/range-calendar.js"></script>
<script type="text/javascript" src="/assets/r2lab/statistics.js"></script>
<script src="/assets/js/chartlib/dist/Chart.bundle.js"></script>
<script src="/assets/js/simpleheat.js"></script>
<script src="/assets/js/data.js"></script>
<style type="text/css"> @import url("/assets/r2lab/statistics.css"); </style>



<ul id="myTabs" class="nav nav-tabs" role="tablist">
  <li role="presentation" class="active">
    <a href="#A1" id="A1-tab" role="tab" data-toggle="tab" aria-controls="A1" aria-expanded="true">Line Graph</a>
  </li>
  <li role="presentation" class="">
    <a href="#A2" role="tab" id="A2-tab" data-toggle="tab" aria-controls="A2" aria-expanded="false">Bar Graph</a>
  </li>
  <li role="presentation" class="">
    <a href="#A3" role="tab" id="A3-tab" data-toggle="tab" aria-controls="A3" aria-expanded="false">Heat Graph</a>
  </li>
</ul>

<div id="contents" class="tab-content">
  <!------------ G1 ------------>
  <div role="tabpanel" class="tab-pane fade active in" id="A1" aria-labelledby="home-tab">
    <br/>
    1 Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut officia deserunt mollit anim id est laborum.
    <br/><br/>

  </div>

  <!------------ G2 ------------>
  <div role="tabpanel" class="tab-pane fade" id="A2" aria-labelledby="profile-tab">
    <br/>
    2 Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
    <br/><br/>
  </div>

  <!------------ G3 ------------>
  <div role="tabpanel" class="tab-pane fade" id="A3" aria-labelledby="profile-tab">
    <br/>
    3  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut.
    <br/><br/>
  </div>
</div> <!-- end div contents -->

<script src="/assets/r2lab/open_tab.js"></script>



<div class="container">

  <div class="row">
    <div class="col-lg-12">
      <div style="width: 100%">
        <canvas id="line" height="250" width="700"></canvas>
      </div>
    </div>
  </div>

  <div class="row">
    <div class="col-lg-12">
      <br><br>
      <p></p>
      <br><br>
    </div>
  </div>  

  <div class="row">
    <div class="col-lg-12">
      <div style="width: 100%">
        <canvas id="bar" height="250" width="700"></canvas>
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
      <br><br>
    </div>
  </div>  

  <div class="row">
    <div class="col-lg-12">
      <div class="heat_container" style="background-image: url(/assets/img/chamber.png); background-repeat: no-repeat;">
        <canvas id="heat" width="775" height="505"></canvas>
      </div>
    </div>
  </div>

</div>
<script src="/assets/r2lab/statistics-heat.js"></script>
