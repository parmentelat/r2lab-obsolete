title: R2lab live status page
tab: run
skip_header: yes
require_login: true

<div id="livemap_container"></div>
<script type="text/javascript" src="/assets/r2lab/livemap.js"></script>
<style type="text/css"> @import url("/assets/r2lab/livemap.css"); </style>
<script>
    // override livemap default settings 
    Object.assign(livemap_options, {
      space_x : 72,
      space_y : 87,
      radius_unavailable : 21,
      radius_ok : 16,
      radius_pinging : 10,
      radius_warming : 4,
      radius_ko : 0,
      margin_x : 5,
      margin_y : 20,
      padding_x : 35,
      padding_y : 35,
//    debug : true,
   });
</script>
