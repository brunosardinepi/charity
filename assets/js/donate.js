$(document).ready(function() {
    $('#donateModal').on('shown.bs.modal', function () {
        $('#id_amount').trigger('focus');
    });
});

$(document).on('click', "[id^='show-donate']", function(event) {
    event.preventDefault();

    var arr = $(this).attr('id');
    var arr = arr.split("-");
    var model = arr[2];
    var pk = arr[3];

    var url = "/profile/card/list/";

    $.get(url, function (data) {
        $.each(data, function(key, value) {
            console.log("default = " + value.default);
//            if (value.default == "true") {
//                var checked = "checked";
//            } else {
//                var checked = "";
//            };
            var checked = ((value.default == true) ? 'checked' : '');
            console.log("checked = " + checked);
            $('#donateModal .modal-body').append("<input type='radio' name='saved_card' class='saved-card' value='" + value.id + "' " + checked + "/> " + value.name + " (" + value.last4 + ")<br />");
        });
    });


//    var url = "/comments/" + model + "/" + pk + "/comment/";

//    $('#newComment .modal-body').html("<form id='comment' action=" + url + " method='POST'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrftoken + "' /><div class='form-group'><textarea class='form-control' placeholder='Type your comment here.' id='comment-text' required></textarea></div></form>");
//    $('#newComment .modal-footer').html("<button type='button' class='btn btn-secondary' data-dismiss='modal'>Close</button><button id='comment-" + model + "-" + pk + "' type='button' class='btn btn-primary submit-comment' data-dismiss='modal'>Comment</button>");
});

$(document).on("click", ".submit-comment", function(event) {
    var arr = $(this).attr("id");
    comment(arr);
});

function comment(arr) {
    var arr = arr.split("-");
    var model = arr[1];
    var model_pk = arr[2];

    $.ajax({
        url : "/comments/" +  model + "/" + model_pk + "/comment/",
        type : "POST",
        data : { comment_text : $("#comment-text").val() },
        success : function(json) {
            $("#comment-text").val('');
            if (!$("#comment-list").length) {
                $("#no-comments").remove();
                $("#comment").after("<div id='comment-list'></div>");
            }
            $("#comment-list").prepend("<div class='row comment' id='comment-" + json.id + "'><div class='col-md-auto'><img class='comment-profile-picture' src='" + json.user_image_url + "' /></div><div class='col comment-main'><div class='row comment-info'><div class='col'><span class='comment-user-name'>" + json.user + "</span><span class='comment-date'><i class='fal fa-clock'></i> " + json.date + "</span></div><div class='col text-right'><span class='votes'><a id='upvotes-r-" + json.id + "' class='vote upvote user-vote' href=''><i class='fal fa-chevron-circle-up'></i></a> <label id='upvote-count-r-" + json.id + "'>1</label> <a id='downvotes-r-" + json.id + "' class='vote downvote' href=''><i class='fal fa-chevron-circle-down'></i></a> <label id='downvote-count-r-" + json.id + "'>0</label></span> <a class='show-reply' id='" + json.id + "' href='' data-toggle='modal' data-target='#replyModal'><i class='fal fa-reply'></i></a> <a id='delete-reply-" + json.id + "' class='delete-cr' href=''><i class='fal fa-trash-alt'></i></a> <a href='/notes/abuse/comment/reply/" + json.id + "' class='report-comment'><i class='fal fa-flag'></i></a></div></div><hr>" + json.content + "</div>");
        }
    });
};

