function comment() {
    console.log($("#comment-text").val());
    $.ajax({
        url : "/comments/" +  model + "/" + model_pk + "/comment/",
        type : "POST",
        data : {
            comment_text : $("#comment-text").val(),
        },
        success : function(json) {
            $("#comment-text").val('');
            if (!$("#comment-list").length) {
                $("#no-comments").remove();
                $("#comment").after("<div id='comment-list'></div>");
            }
            $("#comment-list").prepend("<div class='row comment' id='comment-" + json.id + "'><div class='col-md-auto'><img class='comment-profile-picture' src='" + json.user_image_url + "' /></div><div class='col'><div class='row'><div class='col'><span class='comment-user-name'>" + json.user + "</span><span class='comment-date'><i class='fal fa-clock'></i> " + json.date + "</span></div><div class='col text-right'><button id='upvotes-c-" + json.id + "' class='vote upvote user-vote'>1</button> <button id='downvotes-c-" + json.id + "' class='vote downvote'>0</button> - <a class='show-reply' id='" + json.id + "' href=''>Reply</a> - <a id='delete-comment-" + json.id + "' class='delete-cr' href=''>Delete</a></div></div><hr>" + json.content + "</div>");
        }
    });
};

$(document).on("submit", "#comment", function(event) {
    event.preventDefault();
    comment();
});

function show_reply_textarea(event) {
    var url = "/comments/" + event.target.id + "/reply/";
    $(event.target).parent().after("<form id='reply' action=" + url + " method='POST'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrftoken + "' /><textarea id='reply-text' autofocus></textarea><input type='submit' value='Reply' /></form>");
};

function reply(id) {
    $.ajax({
        url : "/comments/" + id + "/reply/",
        type : "POST",
        data : { reply_text : $("#reply-text").val() },
        success : function(json) {
            $("#reply").remove();
            if (!$("#comment-" + id + "-replies").length) {
                $("#comment-" + id).after("<div id='comment-" + id + "-replies' class='reply-list'></div>");
            }
            $("#comment-" + id + "-replies").append("<div class='row reply' id='reply-" + json.id + "'><div class='col-md-auto'><img class='comment-profile-picture' src='" + json.user_image_url + "' /></div><div class='col'><div class='row'><div class='col'><span class='comment-user-name'>" + json.user + "</span><span class='comment-date'><i class='fal fa-clock'></i> " + json.date + "</span></div><div class='col text-right'><button id='upvotes-r-" + json.id + "' class='vote upvote user-vote'>1</button> <button id='downvotes-r-" + json.id + "' class='vote downvote'>0</button> - <a id='delete-reply-" + json.id + "' class='delete-cr' href=''>Delete</a></div></div><hr>" + json.content + "</div>");
        }
    });
};

$(document).on('click', ".show-reply", function(event) {
    event.preventDefault();
    show_reply_textarea(event);
});

$(document).on('submit', "#reply", function(event) {
    event.preventDefault();
    var id = $("#reply").prev().find(".show-reply").attr("id");
    reply(id);
});

function delete_obj(event) {
    var arr = event.target.id.split('-');
    var url = "/comments/delete/" + arr[1] + "/" + arr[2] + "/";
    $.get(url, function () {
        $("#" + arr[1] + "-" + arr[2]).remove();
    });
};

$(document).on('click', ".delete-cr", function(event) {
    event.preventDefault();
    delete_obj(event);
});
