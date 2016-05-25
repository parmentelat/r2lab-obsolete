$(document).ready(function() {

  function partial(){
    $('#partial_slices').load('slices.md');
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


  //STOLEN FROM THIERRY EXAMPLES
  var get_slices = function(id, names) {
    var body = "#"+id;
    var request = {};
    if (names) request['names'] = names;
    post_omfrest_request('/slices/get', request, function(xhttp) {
      if (xhttp.readyState == 4 && xhttp.status == 200) {

      var responses = JSON.parse(xhttp.responseText);
    	  $(body).html("<div class='row'>\
                        <div class='col-md-4'><b>name</b></div>\
                        <div class='col-md-3'><b>slice expiration date</b></div>\
                        <div class='col-md-3'><b>account expiration date</b></div>\
                        <div class='col-md-2'>&nbsp;</div>\
                      </div>");
    	  for (i = 0; i < responses.length; i++) {
          var response   = responses[i];
          var slicename  = response['name'];
          var expiration = response['valid_until'];
          var closed     = response['closed_at'];
          //var expiration = '2016-01-22T09:25:31Z';

          var s_class   = ['in_green','in_green'];
          var s_message = ['valid', 'valid'];
          var s_icon    = '';
          if (isPastDate(expiration) || isPastDate(closed)){
            sendMessage('One or more of your slices had expired. Click \
                        <a href="#" data-toggle="modal" data-target="#slice_modal">here</a>\
                        to manage it and renew it!', 'attention');

            if (isPastDate(expiration)){
              s_class[0]   = 'in_red';
              s_message[0] = 'expired';
            }
            if (isPastDate(closed)){
              s_class[1]   = 'in_red';
              s_message[1] = 'expired';
            }

            s_icon = "<a href='#' rel='tooltip' title='renew'>\
                       <span class='glyphicon glyphicon-refresh' onClick=renew_slice('"+i+"','"+slicename+"');></span>\
                     </a>";
          }
          $(body).append("<div class='row'>\
                            <div class='col-md-4'>"+slicename+"</div>\
                            <div class='col-md-3' id='datetime_expiration"+i+"'>\
                              <span class="+s_class[0]+">"+moment(expiration).format("YY-MM-DD HH:mm")+"<span>\
                            </div>\
                            <div class='col-md-3' id='datetime_closed"+i+"'>\
                              <span class="+s_class[1]+">"+moment(closed).format("YY-MM-DD HH:mm")+"<span>\
                            </div>\
                            <div class='col-md-2' id='icon_"+i+"'>"+s_icon+"</div>\
                          </div>");
          $('a').tooltip();
        }
     }
   });
  }


  function main(){
    partial();
    get_slices("list-slices", r2lab_slices);
  }


  main();
});

//STOLEN FROM THIERRY EXAMPLES
// an example of how to renew a slice
var renew_slice = function(element, slicename) {
  var request = {
    "name" : slicename,
	};
  post_omfrest_request('/slices/renew', request, function(xhttp) {
    if (xhttp.readyState == 4 && xhttp.status == 200) {
      var answer = JSON.parse(xhttp.responseText);
      console.log(answer);

      get_slices("list-slices", r2lab_slices);
      // $('#datetime_expiration'+element).removeClass('in_red');
      // $('#datetime_expiration'+element).addClass('in_green');
      // $('#datetime_expiration'+element).html(moment(answer['valid_until']).format("YY-MM-DD HH:mm"));
      //
      // $('#datetime_closed'+element).removeClass('in_red');
      // $('#datetime_closed'+element).addClass('in_green');
      // $('#datetime_closed'+element).html(moment(answer['closed_at']).format("YY-MM-DD HH:mm"));
      // $('#icon_'+element).html('');
    }
  });
}
