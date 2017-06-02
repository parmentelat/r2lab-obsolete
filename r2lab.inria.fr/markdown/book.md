title: R2lab Scheduler
tab: book
skip_header: yes
require_login: true

<div class="container" markdown="1">

<div class="alert alert-danger" role="alert" markdown="1">
<strong>Important notes!</strong>

* R2lab platform is reset every time a <strong>nightly</strong> slice is found in the calendar,
which occurs a couple times a week on average.
As part of this verification routine, the testbed will be thoroughly reset and <strong>all data will be lost</strong>.
* In any case, please make sure to **save your experiment's data** once you are done,
as the next user will probably reload an image on your nodes.
* All times on this website are expressed wrt the <strong>CET timezone</strong>,
which is UTC+1 in winter, and UTC+2 in summer.
</div>

 <div class="row">
  <div class="col-md-12">
   <div id='messages' style="display: none" class="" role="alert">
    <a class="close" onclick="$('.alert').hide()">×</a>
   </div>
  </div>
 </div>
 <br />
 <div class="row" id="all">
 <!-- the left pane with the slices & keys button, and the slices list, on 2 columns -->
 << include r2lab/slices-left-pane.html >>
 <div class="col-md-10">
  <div id="liveleases_container" class="book"></div>
   <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.18.1/moment.min.js"></script>
   <script type="text/javascript" src="/assets/js/moment-round.js"></script>
   <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js"></script>
   <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/fullcalendar/3.4.0/fullcalendar.min.js"></script>
   <style type="text/css"> @import url("https://cdnjs.cloudflare.com/ajax/libs/fullcalendar/3.4.0/fullcalendar.min.css"); </style>

   <style type="text/css"> @import url("/assets/r2lab/liveleases.css"); </style>
   <script type="text/javascript" src="/assets/r2lab/xhttp-django.js"></script>
   <script type="text/javascript" src="/assets/r2lab/liveleases.js"></script>
   <script>
    // override liveleases default settings 
    Object.assign(liveleases_options, {
      mode : 'book',
    });
   </script>
   <div id="current-slice" data-current-slice-color="#000"></div>
  </div>
 </div>

<!-- defines slices_keys_modal -->
<< include r2lab/slices-keys-modal.html >>

</div>
