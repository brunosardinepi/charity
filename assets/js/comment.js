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

$(document).on('click', ".show-reply", function(event) {
    event.preventDefault();

    var id = $(this).attr('id');
    console.log("id = " + id);
    var url = "/comments/" + id + "/reply/";
    console.log("url = " + url);

    $('.modal-body').html("<form id='replyForm' action=" + url + " method='POST'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrftoken + "' /><div class='form-group'><textarea class='form-control' id='reply-text' autofocus></textarea></div></form>");
    $('.modal-footer').html("<button type='button' class='btn btn-secondary' data-dismiss='modal'>Close</button><button id=" + id + " type='button' class='btn btn-primary submit-reply' data-dismiss='modal'>Reply</button>");
});

$(document).on("click", ".submit-reply", function(event) {
//    event.preventDefault();
    var id = $(this).attr("id");
    console.log("id to pass to reply() = " + id);
    reply(id);
//    $('form#replyForm').submit();
});

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

function delete_obj(event) {
    var arr = $(event.target).parent('a').attr('id');
    console.log("arr = " + arr);
    var arr = arr.split('-');
    var url = "/comments/delete/" + arr[1] + "/" + arr[2] + "/";
    $.get(url, function () {
        $("#" + arr[1] + "-" + arr[2]).remove();
    });
};

$(document).on('click', ".delete-cr", function(event) {
    event.preventDefault();
    delete_obj(event);
});
