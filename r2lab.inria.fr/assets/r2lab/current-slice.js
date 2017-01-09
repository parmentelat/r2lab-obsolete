/*
 * tools for managing current slice
 */

var current_slice = {
    debug : true,

    // the value of interest
    name : "",

    // the key for storing the value
    key : 'r2lab:current_slice',
    // the class for decorating html elements
    klass : 'current_slice',

    // retrieve current slice upon page load
    // avail_slices is the full list as retrieved at the registry
    // mostly for the r2lab-user.js template
    init_from_storage : function(r2lab_accounts_slices) {
	var slicenames = r2lab_accounts.map(
	    function(account){return account['name'];});
	current_slice.name = current_slice.get(slicenames);
	current_slice.store(current_slice.name);
    },

    get : function(avail_slices) {
	if (avail_slices.length == 0) {
	    console.log("WARNING: current_slice.get_last: no slices to chose from");
	    return "";
	}
	var default_slice = avail_slices[0];
	// non-html5 browsers
	if (typeof(Storage) === "undefined") {
	    console.log("WARNING: current_slice.get_last: no local storage");
	    return default_slice;
	} 
	stored = localStorage.getItem(current_slice.key);
	// check it's still current
	if (avail_slices.indexOf(stored) >= 0) {
	    if (current_slice.debug) console.log("Retrieved current_slice:"+stored);
	    return stored;
	}
	if (current_slice.debug) console.log("Returning default:"+default_slice);
	return default_slice;
    },

    store : function(slice) {
	if (typeof(Storage) === "undefined") {
	    console.log("WARNING: current_slice.store : no local storage");
	} else {
	    if (current_slice.debug) console.log("Storing current_slice:"+slice);
	    localStorage.setItem(current_slice.key, slice);
	}
    }
};
$(current_slice.init)
