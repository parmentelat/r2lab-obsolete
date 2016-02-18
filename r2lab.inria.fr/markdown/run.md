title: R2lab Experimenter Page
tab: run
skip_header: yes
float_menu_template: r2lab/float_menu-slices.html

# Warning : this page is work in progress !

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
</script>
<style type="text/css"> @import url("/plugins/livemap.css"); </style>

---
<table class="table table-condensed" id='livetable_container'> </table>
<script type="text/javascript" src="/plugins/livetable.js"></script>
<script>livetable_show_rxtx_rates = true;</script>
<style type="text/css"> @import url("/plugins/livetable.css"); </style>
