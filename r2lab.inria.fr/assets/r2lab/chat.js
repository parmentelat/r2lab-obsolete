$(function() {

    var init_chat = function() {
	var username =
	    r2lab_user.email
	    .replace("@", "_at_")
	    .replace(".", "_");
	$("#chat-container")
	    .append($("<span />")
		    .attr("id", "chat-hide-show")
		    .addClass("fa")
		    .click(hide_show))
	    .append($("<span />")
		    .attr("id", "chat-hide-legend")
		    .addClass("chat-legend")
		    .html("Click to hide (but stay connected)")
		    .click(hide_show))
	    .append($("<span />")
		    .attr("id", "chat-show-legend")
		    .addClass("chat-legend")
		    .html("Click to show IRC chatroom")
		    .click(hide_show))
	    .append($("<iframe />")
		    .attr("id", "chat-body")
		    .attr("src",
			  "https://webchat.freenode.net?nick="
			  + username
			  + "&channels=%23r2lab&uio=MTY9dHJ1ZSY5PXRydWUmMTE9MzA572")
		    .attr("width", "100%")
		    .attr("height", "450"));
	update_hide_show();
    }

    var end_chat = function() {
	$("#chat-container").html('');
    }

    var hide_show = function() {
	$("#chat-body").toggle(200, update_hide_show);
    }
			  
    var update_hide_show = function() {
	var classes = [ 'fa-caret-down', 'fa-caret-right'];
	var visible = $("#chat-body").is(":visible");
	var add = visible ? 0 : 1;
	var rem = 1 - add;
	$("#chat-hide-show")
	    .addClass(classes[add])
	    .removeClass(classes[rem]);
	$("#chat-hide-legend").toggle(visible);
	$("#chat-show-legend").toggle(!visible);
    }
    
    var update_button = function() {
	classes = [ 'fa-close', 'fa-user-o'];
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
