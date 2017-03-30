$(document).ready(function() {

    function normalize_id(name){
	var new_name = name;
	new_name = name.replace(/[_\s]/g, '-').replace(/[^a-z0-9-\s]/gi, '');
	return new_name
    }


    function send_message(msg, type){
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
	$('html,body').animate({'scrollTop' : 0}, 400);
	$('#messages').removeClass().addClass('alert alert-'+cls);
	$('#messages').html("<strong>" + title + "</strong> " + msg);
	$('#messages').fadeOut(200).fadeIn(200).fadeOut(200).fadeIn(200);
    }


    function is_past_date(date){
	var past = false;
	if(moment().diff(date, 'minutes') > 0 && date != null){
	    past = true;
	}
	return past;
    }


    var get_slices = function(id, names) {
	var body = $("#"+id);
	body.html("<div class='row slice-header'>"
		  + "<div class='col-md-6'>Name</div>"
		  + "<div class='col-md-4'>Expiration Date</div>"
		  + "<div class='col-md-2'>&nbsp;</div>"
		  + "</div>");
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
			    var normal_id  = normalize_id(slicename);
			    var expiration = response['valid_until'];
			    var closed     = response['closed_at'];
			    //var expiration = '2016-01-22T09:25:31Z';

			    var s_class   = 'in-green';
			    var s_message = 'valid';
			    var s_id = "renew-slice-" + normal_id;
			    var s_icon = "<span class='fa fa-refresh in-blue' data-toggle='tooltip' title='renew'"
				+ " id='" + s_id + "'>";
			    var the_date  = moment(expiration).format("YYYY-MM-DD HH:mm");
			    if (is_past_date(expiration) || is_past_date(closed)){
				send_message(slice_manage_invitation, 'attention');

				if (is_past_date(closed)){
				    the_date  = moment(closed).format("YYYY-MM-DD HH:mm");
				}

				s_class   = 'in-red';
				s_message = 'expired';
			    }

			    $(body).append("<div class='row'>"
					   + "<div class='col-md-6'>" + slicename + "</div>"
					   + "<div class='col-md-4' id='timestamp-expire" + normal_id + "'>"
					   + "<span class=" + s_class + ">" + the_date + "</span>"
					   + "</div>"
					   + "<div class='col-md-2'>" + s_icon + "</div>");
			    $("#"+s_id).click(function() {renew_slice(normalize_id(slicename), slicename)});
			}
		    }
		}
		$('[data-toggle="tooltip"]').tooltip();   
	    });
	});
    }


    var renew_slice = function(element, slicename) {
	var request = {
	    "name" : slicename,
	};
	post_xhttp_django('/slices/renew', request, function(xhttp) {
	    if (xhttp.readyState == 4 && xhttp.status == 200) {
		var answer = JSON.parse(xhttp.responseText);
		console.log("answer from /slices/renew");
		console.log(answer);
		
		$('#timestamp-expire'+element).removeClass('in-red');
		$('#timestamp-expire'+element).addClass('in-green');
		$('#timestamp-expire'+element).toggle("pulsate").toggle("highlight");
		$('#timestamp-expire'+element).html(moment(answer['valid_until']).format("YYYY-MM-DD HH:mm"));
	    }
	});
    };


    function main(){
	var slicenames = r2lab_accounts.map(
	    function(account){return account['name'];});
	get_slices("liveslices-container", slicenames);
    }


    main();
});

