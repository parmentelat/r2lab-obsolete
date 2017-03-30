(function($) {

    // returns a random image from a given image list already placed in assets/img folder
    getOneImage = function(imagesList, path) {
	path = path || '/assets/img/';
  	idx  = Math.round(Math.random() * (imagesList.length - 1));
  	return path+imagesList[idx]
    }


    // set at background tag the image returned by getOneImage function
    placeImage = function() {
	var imagesList = ["banner-1.png", "banner-2.png",
			  "banner-3.png", "banner-4.png",
			  "banner-5.png", "banner-6.png",
			 ];

  	$('#background').css("background-image", "url("+getOneImage(imagesList)+")");
    }

})(jQuery);
