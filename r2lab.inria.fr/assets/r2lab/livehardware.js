"use strict";

// sidecar_url global variable is defined in template sidecar-url.js
// from sidecar_url as defined in settings.py

//global - mostly for debugging and convenience
let the_livehardware;

////////// configurable
let livehardware_options = {

}

//////////////////////////////
// nodes are dynamic
// their hardware row and cells get created through d3 enter mechanism
class LiveHardwareNode extends LiveColumnsNode{

    constructor(id) {
	super(id);
	this.cells_data = [
	    [ span_html(id, 'badge pointer'), '' ],	// id
	    undefined,				// avail
	    undefined,				// on/off
	    undefined,				// usrp-on-off
	    undefined,				// duplexer
	    undefined,				// usrp-antenna
	    undefined,				// wifi antennas
	];
    }

    // nodes worth being followed when clicking on the hardware banner
    is_worth() {
	return (   (this.usrp_type || 'none') != 'none');
    }

    // after the internal properties are updated from the incoming JSON message
    // we need to rewrite actual representation in cells_data
    // that will contain a list of ( html_text, class )
    // used by the d3 mechanism to update the <td> elements in the row
    compute_cells_data() {
	let col = 1
	// avail
	this.cells_data[col++] = this.cell_available();
	// on-off
	this.cells_data[col++] = this.cell_on_off();
	// usrp-on-off
	this.cells_data[col++] = this.cell_usrp();
	// duplexer details
	this.cells_data[col++] = this.cell_duplexer();
	// usrp antenna(s) images
	this.cells_data[col++] = this.cell_usrp_antennas();
	// wifi antenna(s) images
	this.cells_data[col++] = this.cell_wifi_antennas();
    }

    cell_duplexer() {
	let html = (! 'usrp_duplexer' in this) ? '-' : this.usrp_duplexer;
	return [ html, "" ];
    }

    image_link(img) {
	// xxx where to store those files exactly ?
	let icon = span_html('', 'fa fa-camera');
	// something like ${this.id:02d} 
	// let str_id = (this.id <= 9) ? `0${this.id}` : `${this.id}`;
	return `<a class='image-link' alt="click to see image" onclick='show_image("/raw/node-images/${img}")'>${icon}</a>`;
    }

    cell_usrp_antennas() {
	if ((!('images_usrp' in this)) || (this.images_usrp.length == 0)) {
	    return '-';
	}
	let html = this.images_usrp.map( (name) => this.image_link(name)).join(" / ");
	return [html, "image-links"]
    }

    cell_wifi_antennas() {
	if ((!('images_wifi' in this)) || (this.images_wifi.length == 0)) {
	    return '-';
	}
	let html = this.images_wifi.map( (name) => this.image_link(name)).join(" / ");
	return [html, "image-links"]
    }
    
}


//////////////////////////////
class LiveHardware extends LiveColumns {

    constructor(domid) {
	super();
	this.domid = domid;
    }

    init_headers(header) {
	header.append('th').html('node');
	header.append('th').html('avail.');
	header.append('th').html('on/off');
	header.append('th').html('usrp');
	header.append('th').html('duplexer');
	header.append('th').html('usrp antenna');
	header.append('th').html('wifi antennas');
    }

    init_nodes() {
	for (let i=0; i < livecolumns_options.nb_nodes; i++) {
	    this.nodes[i] = new LiveHardwareNode(i+1);
	}
    }
}

// autoload
$(function() {
    // name it for debugging from the console
    the_livehardware = new LiveHardware("livehardware_container");
    the_livehardware.init();
})

//////////////////// helpers
function show_image(img) {
    $('#big_image_content').html('<img src="'+img+'" class="max-img" >');
    $('#big_photo').modal('toggle');
}

