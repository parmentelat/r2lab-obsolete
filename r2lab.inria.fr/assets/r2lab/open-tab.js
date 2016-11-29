// include this in pages that feature tabs
function open_tab(name) {
    /* add initial sharp sign if not provided */
    if (name[0] != '#')
	name = '#' + name;
    $('.nav-tabs a[href=' + name + ']').tab('show');
}

$(function () {
    // upon load, go to the tab specified by hash like e.g. #A1
    var hash = document.location.hash;
    if (hash) open_tab(hash);
/* arm the tabs and pills */
    $(".nav-tabs a").click(function(e){
/* we DO NOT call this; this way when changing tabs the url location
   is updated with say #A2 when one clicks A2 */
/*	e.preventDefault(); */
        $(this).tab('show');
    });
    $(".nav-pills a:not(.default-click)").click(function(e){
/* we DO call this one, so the codeview elements do not cause a change in the url
   e.g. when clicking in 'plain' or 'diff' this does not reflect in url */
	e.preventDefault(); 
        $(this).tab('show');
    });
});
