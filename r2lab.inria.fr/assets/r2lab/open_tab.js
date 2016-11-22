// include this in pages that feature tabs
function open_tab(name) {
    if (name[0] != '#')
	name = '#' + name;
    $('.nav-tabs a[href=' + name + ']').tab('show');
}

$(function () {
    // upon load, go to the tab specified by hash like e.g. #A1
    var hash = document.location.hash;
    if (hash) open_tab(hash);
    $(".nav-tabs a").click(function(){
        $(this).tab('show');
    });
});
