
(function($) {

	// returns a random images from a given list 
  getOneImage = function(imagesList, path) {
  	path = path || 'assets/img/';	
  	idx  = Math.round(Math.random() * (imagesList.length - 1));
  	return path+imagesList[idx]
  }


  // set at background tag the image returned by getOneImage function
	placeImage = function() {
		var imagesList = ["back.jpg", "back_1.jpg", "back_2.jpg"];

  	$('#background').css("background-image", "url("+getOneImage(imagesList)+")"); 
	}

})(jQuery);
