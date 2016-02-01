/*
 * tools for managing current slice
 */

// xxx todo - group all this inside a 'current_slice' global variable

var current_slice_key = 'r2lab:current_slice';
// for styling selected slice
var current_slice_class = 'current_slice';

// expose this function to r2lab_user.js for retrieving current slice upon page load
// avail_slices is the full list as retrieved at the registry
function current_slice_get_last(avail_slices) {
    if (avail_slices.length == 0) {
	console.log("WARNING: current_slice_get_last: no slices to chose from");
	return "";
    } else {
	default_slice = avail_slices[0];
    }
    // non-html5 browsers
    if (typeof(Storage) === "undefined") {
	console.log("WARNING: current_slice_get_last: no local storage");
	return default_slice;
    } 
    stored = localStorage.getItem(current_slice_key);
    if (avail_slices.indexOf(stored) >= 0) {
	return stored;
    }
    current_slice_store(default_slice);
    return default_slice;
}

function current_slice_store(slice) {
    if (typeof(Storage) === "undefined") {
	console.log("WARNING: current_slice_store : no local storage");
    } else {
	localStorage.setItem(current_slice_key, slice);
    }
}

// highlight the item corresponding to current slice
function current_slice_update_selectors() {
    $('.set_current_slice').each(function(index){
        if ($(this).attr('slicename') == r2lab_current_slice){
	    $(this).addClass(current_slice_class);
	} else {
	    $(this).removeClass(current_slice_class);
	}
    });
}
// all elements of type 'set_current_slice' will have a click function
// defined on them that will change the current slice name
(function($){
    var arm_selectors = function() {
	$('.set_current_slice').on("click", function(){
	    var new_slice = $(this).attr("slicename");
	    current_slice_store(new_slice);
	    r2lab_current_slice = new_slice;
	    current_slice_update_selectors();
	});
    };
    $(arm_selectors);
    $(current_slice_update_selectors);
})(jQuery);
