<!--  CALENDAR -->
<div><hr></div>
<div id='messages' style="display: none" class="alert alert-danger" role="alert">
  <strong>Ooops!</strong> This is a past date!
  <a class="close" onclick="$('.alert').hide()">×</a>
</div>
<br />
<div id='calendar'></div>
<script src="https://cdn.socket.io/socket.io-1.4.4.js"></script>
<script src='../plugins/slices/js/moment.min.js'></script>
<script src='../plugins/slices/js/jquery.min.js'></script>
<script src='../plugins/slices/js/fullcalendar.min.js'></script>
<script src="../plugins/slices/js/calendar.js"></script>
<script src="../plugins/slices/js/update_calendar.js"></script>
<link href='../plugins/slices/css/fullcalendar.css' rel='stylesheet' />
<link href='../plugins/slices/css/fullcalendar.print.css' rel='stylesheet' media='print' />
<link href='../plugins/slices/css/calendar.css' rel='stylesheet'/>

<!--  MAP -->
<div id="livemap_container"></div>
<script type="text/javascript" src="/plugins/livemap.js"></script>
<script>livemap_show_rxtx_rates = true;</script>
<style type="text/css"> @import url("/plugins/livemap.css"); </style>
