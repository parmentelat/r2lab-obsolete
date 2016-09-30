$(document).ready(function() {

  hide_all();

  $("#img_left").click(function(){
    hide_all();
    $("#left_tour").show();
  });
  $("#img_center").click(function(){
    hide_all();
    $("#center_tour").show();
  });
  $("#img_right").click(function(){
    hide_all();
    $("#right_tour").show();
  });

  function hide_all() {
    $("#left_tour"  ).hide();
    $("#center_tour").hide();
    $("#right_tour" ).hide();
  }

})
