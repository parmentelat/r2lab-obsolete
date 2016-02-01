{% load staticfiles %}
{% load jsonify %}
<script type="text/javascript" src="{% static 'js/current_slice.js' %}"></script>
<script type="text/javascript">
/* globals that describe logged in user */
r2lab_user = {{r2lab_context.mfuser|jsonify|safe}};
r2lab_hrn = {{r2lab_context.mfuser.hrn|jsonify|safe}};
r2lab_slices = {{r2lab_context.slices|jsonify|safe}};
// initialize current_slice - set of slices is needed there
console.log("before -> "+ current_slice.name);
current_slice.init_from_storage(r2lab_slices);
console.log("after -> "+ current_slice.name);
// javascript code should use  'current_slice.name'
</script>
