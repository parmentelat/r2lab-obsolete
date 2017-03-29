$(function() {
    var R2labChat = function(chat_username) {
	this.username = chat_username;
	this.init = function() {
	    console.log($("#chat-container"));
	    $("#chat-container").html(
		'<a class="chat-on-off btn btn-primary btn-large">Join chat room #r2lab at freenode (on and off)</a>'
		    + '<iframe style="display:none" class="chat-body" src="https://webchat.freenode.net?nick='
		    + this.username
		    + '&channels=%23r2lab&uio=MTY9dHJ1ZSY5PXRydWUmMTE9MzA572"'
		    + ' width="100%" height="400"></iframe>');
	    $("#chat-container .chat-on-off").click(function(){
		$("#chat-container .chat-body").toggle();
	    })
	};
    };

    new R2labChat(r2lab_user.email
		  .replace("@", "_at_")
		  .replace(".", "_"))
	.init();
})
