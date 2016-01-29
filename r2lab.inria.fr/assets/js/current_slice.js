// all elements of type 'set_current_slice' will have a click function
// defined on them that will change the current slice name
(function($){
  var init = function() {
    $('.set_current_slice').on("click", function(){
       console.log("current_slice should now become: " + $(this).attr("slicename"));
    });
    };
    $(init);
})(jQuery);
