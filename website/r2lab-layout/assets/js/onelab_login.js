
(function($) {

  // remove the OneLab login form in function of the current page 
  present_onelab_login_form = function(imagesList, path) {

    // pages where the login form will appear
    present_login_only_at_page = ['overview', 'index']

    var file = getBaseName($(location).attr('href'));
    
    if ($.inArray(file, present_login_only_at_page) < 0) {
      $( "#onelab_login" ).remove();
    }

  }


  // from the whole URL path get only page name
  getBaseName = function(url) {
  
    if(!url || (url && url.length === 0)) {
      return "";
    }
    var index = url.lastIndexOf("/") + 1;
    var filenameWithExtension = url.substr(index);
    var basename = filenameWithExtension.split(/[.?&#]+/)[0];

    // Handle '/mypage/' type paths
    if(basename.length === 0) {
      url = url.substr(0,index-1);
      basename = getBaseName(url);
    }
    return basename ? basename : ""; 
  }

})(jQuery);
