$(document).ready(function() {
    var version = '1.36';

    function partial(){
	$('#partial_slices').load('slices.md');
    }


    function idFormat(name){
	var new_name = name;
	new_name = name.replace(/[_\s]/g, '-').replace(/[^a-z0-9-\s]/gi, '');
	return new_name
    }

    function sendMessage(msg, type){
	var cls   = 'danger';
	var title = 'Ooops!'
	if(type == 'info'){
	    cls   = 'info';
	    title = 'Info:'
	}
	if(type == 'attention'){
	    cls   = 'warning';
	    title = 'Attention:'
	}
	if(type == 'success'){
	    cls   = 'success';
	    title = 'Yep!'
	}
	$('html,body').animate({'scrollTop' : 0},400);
	$('#messages').removeClass().addClass('alert alert-'+cls);
	$('#messages').html("<strong>"+title+"</strong> "+msg);
	$('#messages').fadeOut(200).fadeIn(200).fadeOut(200).fadeIn(200);
    }


    function isPastDate(date){
	var past = false;
	if(moment().diff(date, 'minutes') > 0 && date != null){
	    past = true;
	}
	return past;
    }


    var get_slices = function(id, names) {
	var body = "#"+id;
	$(body).html("<div class='row slice-header'>\
                    <div class='col-md-6'>Name</div>\
                    <div class='col-md-4'>Expiration Date</div>\
                    <div class='col-md-2'>&nbsp;</div>\
                  </div>");
	$.each(names, function(index, value){

	    var request = {};
	    request['names'] = [value];

	    post_xhttp_django('/slices/get', request, function(xhttp) {

		if (xhttp.readyState == 4 && xhttp.status == 200) {
		    var responses = JSON.parse(xhttp.responseText);

		    var slice_manage_invitation = '\
One or more of your slices has expired. \
<a href="#" data-toggle="modal" data-target="#slices_keys_modal">\
Click here to renew it!</a>';
		    if (responses.length > 0) {
        		for (i = 0; i < responses.length; i++) {

			    var response   = responses[i];
			    var slicename  = response['name'];
			    var expiration = response['valid_until'];
			    var closed     = response['closed_at'];
			    //var expiration = '2016-01-22T09:25:31Z';

			    var s_class   = 'in-green';
			    var s_message = 'valid';
			    var s_icon = "<a href='#' rel='tooltip' title='renew'>\
                         <span class='glyphicon glyphicon-refresh' onClick=renew_slice('"+idFormat(slicename)+"','"+slicename+"');></span>\
                       </a>";
			    var the_date  = moment(expiration).format("YYYY-MM-DD HH:mm");
			    if (isPastDate(expiration) || isPastDate(closed)){
				sendMessage(slice_manage_invitation, 'attention');

				if (isPastDate(closed)){
				    the_date  = moment(closed).format("YYYY-MM-DD HH:mm");
				}

				s_class   = 'in-red';
				s_message = 'expired';
			    }

			    $(body).append("<div class='row'>\
                                <div class='col-md-6'>"+slicename+"</div>\
                                <div class='col-md-4' id='datetime_expiration"+idFormat(slicename)+"'>\
                                  <span class="+s_class+">"+the_date+"<span>\
                                </div>\
                                <div class='col-md-2' id='icon_"+idFormat(slicename)+"'>"+s_icon+"</div>\
                              </div>");
			    $('a').tooltip();
			}
		    }
		}

	    });
	});
    }

    function main(){
	console.log("liveslices version " + version);
	partial();
	var slicenames = r2lab_accounts.map(
	    function(account){return account['name'];});
	get_slices("list-slices", slicenames);
    }

    main();
});

//STOLEN FROM THIERRY EXAMPLES
// an example of how to renew a slice
var renew_slice = function(element, slicename) {
    var request = {
	"name" : slicename,
    };
    post_xhttp_django('/slices/renew', request, function(xhttp) {
	if (xhttp.readyState == 4 && xhttp.status == 200) {
	    var answer = JSON.parse(xhttp.responseText);
	    console.log(answer);

	    $('#datetime_expiration'+element).removeClass('in-red');
	    $('#datetime_expiration'+element).addClass('in-green');
	    $('#datetime_expiration'+element).toggle("pulsate").toggle("highlight");
	    $('#datetime_expiration'+element).html(moment(answer['valid_until']).format("YYYY-MM-DD HH:mm"));
	    // $('#icon_'+element).html('');
	}
    });
}
