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
    if(moment().diff(date, 'minutes') > 0){
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
  	  $(body).html('');
  	  for (i = 0; i < responses.length; i++) {
        var response = responses[i];
        var slicename = response['name'];
        var expiration = response['valid_until'];

        var s_class = 'in_green';
        var s_message = 'valid';
        var s_icon = "";
        if (isPastDate(expiration)){
          s_class = 'in_red';
          s_message = 'expired';
          s_icon = "<a href='#' rel='tooltip' title='renew'><span class='glyphicon glyphicon-refresh' onClick=renew_slice('"+i+"','"+slicename+"');></span></a>";
        }
        $(body).append("<div class='row'><div class='col-md-6'>"+slicename+"</div><div class='col-md-4' id='datetime_"+i+"'><span class="+s_class+">"+moment(expiration).format("YYYY-MM-DD HH:mm")+"<span></div><div class='col-md-2' id='icon_"+i+"'>"+s_icon+"</div></div>");
        $('a').tooltip();
       }
     }
   });
  }


  function main(){
    partial();
    get_slices("list-slices", r2lab_slices);

    // sendMessage('One or more of your slices had expired. Click <a href="#" data-toggle="modal" data-target="#slice_modal">here</a> to manage it and renew it!', 'warning');
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
      $('#datetime_'+element).removeClass('in_red');
      $('#datetime_'+element).addClass('in_green');
      $('#datetime_'+element).html(moment(answer['valid_until']).format("YYYY-MM-DD HH:mm"));
      $('#icon_'+element).html('');
    } else {
      alert('Ops! Request failed.');
    }
  });
}
