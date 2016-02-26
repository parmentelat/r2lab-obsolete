{% load jsonify %}
<script type="text/javascript" src="/assets/r2lab/current-slice.js"></script>
<script type="text/javascript">
// globals that describe logged in user 
r2lab_user = {{r2lab_context.mfuser|jsonify|safe}};
// shortcuts
r2lab_email = {{r2lab_context.mfuser.email|jsonify|safe}};
r2lab_hrn = {{r2lab_context.mfuser.hrn|jsonify|safe}};
// slices
r2lab_slices = {{r2lab_context.slices|jsonify|safe}};
// initialize current_slice
// javascript code should use 'current_slice.name'
current_slice.init_from_storage(r2lab_slices);
</script>
