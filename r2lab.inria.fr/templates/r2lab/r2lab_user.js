{% load jsonify %}
<script type="text/javascript">
/* globals that describe logged in user */
r2lab_user = {{r2lab_context.mfuser|jsonify|safe}};
r2lab_hrn = {{r2lab_context.mfuser.hrn|jsonify|safe}};
r2lab_slices = {{r2lab_context.slices|jsonify|safe}};
</script>
