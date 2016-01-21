(function($) {
    // Functions for float menu in tutorias pages

    FloatMenu = function() {

        var scrollAmount =$(document).scrollTop();
        var newPosition  = menuPosition + scrollAmount;
        
        if($(window).height() < $float_menu.height() + $float_menu_menu.height()){
            $float_menu.css("top",menuPosition);
        }
        else {
            $float_menu.stop().animate({top: newPosition}, $float_speed, $float_easing);
        }
    }

    loadMenu = function() {
        // Config
        $float_speed            = 1000;
        $float_easing           = "easeOutQuint";
        $menu_fade_speed        = 500;
        $closed_menu_opacity    = 0.75;
         
        // Cache vars
        $float_menu        = $("#float_menu");
        $float_menu_menu   = $("#float_menu .menu");
        $float_menu_label  = $("#float_menu .label");

        // Called in page load
        $(window).load( function() {
            menuPosition = $('#float_menu').position().top;
            
            FloatMenu();
            
            $float_menu_menu.fadeIn($menu_fade_speed);
        });
         
        // Called when page is scrolled
        $(window).scroll( function () {
            FloatMenu();
        });
    }


})(jQuery);