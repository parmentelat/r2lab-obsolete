$(function() {

    var init_chat = function() {
	var username =
	    r2lab_user.email
	    .replace("@", "_at_")
	    .replace(".", "_");
	$("#chat-container").html(
	    '<span id="chat-hide-show" class="fa"></span>'
		+ '<iframe id="chat-body" src="https://webchat.freenode.net?nick='
		+ username
		+ '&channels=%23r2lab&uio=MTY9dHJ1ZSY5PXRydWUmMTE9MzA572"'
		+ ' width="100%" height="450"></iframe>');
	$("#chat-hide-show").click(function(){
	    $("#chat-body").toggle("slow", update_hide_show);
	})
	update_hide_show();
    }

    var end_chat = function() {
	$("#chat-container").html('');
    }

    var update_hide_show = function() {
	classes = [ 'fa-window-minimize', 'fa-window-restore'];
	var add = $("#chat-body").is(":visible") ? 0 : 1;
	var rem = 1 - add;
	$("#chat-hide-show")
	    .addClass(classes[add])
	    .removeClass(classes[rem]);
    }
    
    var update_button = function() {
	classes = [ 'fa-close', 'fa-user-circle-o'];
	messages = [ 'leave IRC', 'join IRC'];
	var add = $("#chat-container").html() ? 0 : 1;
	var rem = 1 - add;
	$("#chat-button-text").html(messages[add]);
	$("#chat-button-icon")
	    .addClass(classes[add])
	    .removeClass(classes[rem]);
    }


    var toggle_chat = function() {
	var contents = $("#chat-container").html();
	contents ? end_chat() : init_chat();
	update_button();
    };

    // at load-time we just create a button to enable it
    var r2labchat_loadtime = function() {
	$("#chat-button")
	    .click(toggle_chat)
	    .append(
		$("<span/>")
		    .attr("id", "chat-button-icon")
		    .addClass("fa")
		    .css("margin-right", "10px")
	    )
	    .append(
		$("<span/>")
		    .attr("id", "chat-button-text")
		    .addClass("btn").addClass("btn-primary").addClass("btn-large"))
	;
	update_button();
    }

    r2labchat_loadtime();
})
