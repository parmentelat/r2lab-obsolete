// -*- js-indent-level:4 -*-

/* for eslint */
/*global $*/

"use strict";

// set a random image as the background for #background
$(function() {
    var imagesList = [
	"banner-1.png", "banner-2.png",
	"banner-3.png", "banner-4.png",
	"banner-5.png", "banner-6.png",
    ];
    
    // returns a random image from a given image list already placed in assets/img folder
    function getOneImage(imagesList) {
	let path = '/assets/img/';
	let idx  = Math.round(Math.random() * (imagesList.length - 1));
	return path+imagesList[idx]
    }
    
    $('#background').css("background-image", "url("+getOneImage(imagesList)+")");
})


