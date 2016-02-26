(function($) {
    // Functions for float menu in the tutorials pages

    float_menu = function() {
        // Config
        var $float_speed            = 1000;
        var $float_easing           = "easeOutQuint";
        var $menu_fade_speed        = 500;
        var $closed_menu_opacity    = 0.75;
         
        // Cache vars
        var $float_menu        = $("#float_menu");
        var $float_menu_menu   = $("#float_menu .menu");
        var $float_menu_label  = $("#float_menu .label");

        // Called in page load
        $(window).load( function() {
            menuPosition = $('#float_menu').position().top;
            
            adjust_menu();
            
            $float_menu_menu.fadeIn($menu_fade_speed);
        });
         
	var adjust_menu = function() {
	    
            var scrollAmount = $(document).scrollTop();
            var newPosition  = menuPosition + scrollAmount;
        
            if($(window).height() < $float_menu.height() + $float_menu_menu.height()){
		$float_menu.css("top", menuPosition);
            } else {
		$float_menu.stop().animate({top: newPosition}, $float_speed, $float_easing);
            }
	}

        // Called when page is scrolled
        $(window).scroll( function () {
            adjust_menu();
        });
    }
})(jQuery);
