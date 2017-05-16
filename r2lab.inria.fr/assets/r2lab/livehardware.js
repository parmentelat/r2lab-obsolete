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
let LiveHardwareNode = function (id) {

    this.id = id;

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

LiveHardwareNode.prototype.__proto__ = LiveColumnsNode.prototype;

// nodes worth being followed when clicking on the hardware banner
LiveHardwareNode.prototype.is_worth = function() {
    return (   this.cmc_on_off == 'on'
	       || this.usrp_on_off == 'on' )
 	&& this.available != 'ko';
}

// after the internal properties are updated from the incoming JSON message
// we need to rewrite actual representation in cells_data
// that will contain a list of ( html_text, class )
// used by the d3 mechanism to update the <td> elements in the row
LiveHardwareNode.prototype.compute_cells_data = function() {
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

LiveHardwareNode.prototype.cell_duplexer = function() {
    let html = (! 'usrp_duplexer' in this) ? '-' : this.usrp_duplexer;
    return [ html, "" ];
}

LiveHardwareNode.prototype.image_link = function(img) {
    // xxx where to store those files exactly ?
    let icon = span_html('', 'fa fa-camera');
    // something like ${this.id:02d} 
    // let str_id = (this.id <= 9) ? `0${this.id}` : `${this.id}`;
    return `<a class='image-link' alt="click to see image" onclick='show_image("/raw/node-images/${img}")'>${icon}</a>`;
}

LiveHardwareNode.prototype.cell_usrp_antennas = function() {
    if ((!('images_usrp' in this)) || (this.images_usrp.length == 0)) {
	return '-';
    }
    let html = this.images_usrp.map( (name) => this.image_link(name)).join(" / ");
    return [html, "image-links"]
}

LiveHardwareNode.prototype.cell_wifi_antennas = function() {
    if ((!('images_wifi' in this)) || (this.images_wifi.length == 0)) {
	return '-';
    }
    let html = this.images_wifi.map( (name) => this.image_link(name)).join(" / ");
    return [html, "image-links"]
}

//////////////////////////////
function LiveHardware(domid) {

    this.nodes = [];
    this.domid = domid;
}

// inheritance
LiveHardware.prototype.__proto__ = LiveColumns.prototype;

LiveHardware.prototype.init_headers = function (header) {
    header.append('th').html('node');
    header.append('th').html('avail.');
    header.append('th').html('on/off');
    header.append('th').html('usrp');
    header.append('th').html('duplexer');
    header.append('th').html('usrp antenna');
    header.append('th').html('wifi antennas');
}

LiveHardware.prototype.init_nodes = function () {
    for (let i=0; i < livecolumns_options.nb_nodes; i++) {
	this.nodes[i] = new LiveHardwareNode(i+1);
    }
}

// autoload
$(function() {
    // name it for debugging from the console
    the_livehardware = new LiveHardware("livehardware_container");
    the_livehardware.init();
})

// helpers
function show_image(img) {
    $('#big_image_content').html('<img src="'+img+'" class="max-img" >');
    $('#big_photo').modal('toggle');
}

