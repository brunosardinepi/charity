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

//    $('#donateModal .modal-body').html("<form action=" + url + " method='POST' id='payment-form'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrftoken + "' /><div class='form-check'><input type='checkbox' name='anonymous_donor' class='form-control' id='id_anonymous_donor'><label for='id_anonymous_donor'>Anonymous donor</label></div><div class='form-check'><input type='checkbox' name='amount' class='preset-amount form-check-input' value=5 />$5<br /><input type='checkbox' name='amount' class='preset-amount form-check-input' value=10 />$10<br /><input type='checkbox' name='amount' class='preset-amount form-check-input' value=25 />$25<br /><input type='checkbox' name='amount' class='preset-amount form-check-input' value=50 />$50<br /><input type='checkbox' name='amount' class='preset-amount form-check-input' value=100 />$100<br /></div><div class='form-check'><input type='checkbox' name='anonymous_amount' class='form-control' id='id_anonymous_amount'><label for='id_anonymous_amount'>Anonymous amount</label></div><div class='form-group'><label for='id_amount'>Amount</label><input type='number' class='form-control' id='id_amount' placeholder='$15' min='0' max='999999'></div><div id='amount-errors'></div><div class='form-group'><label for='id_comment'>Comment</label><textarea class='form-control' name='comment' id='id_comment' rows='3'></textarea></div><div class='form-check'><input type='checkbox' name='monthly' class='form-control' id='id_monthly'><label for='id_monthly'>Monthly</label></div><p><a id='new-card' href=''>New card</a></p><div id='new-card-info' style='display:none;'><p><label for='id_save_card'>Save card:</label> <input type='checkbox' name='save_card' id='id_save_card' /></p><div id='card-element'></div><div id='card-errors' role='alert'></div></div></div><button>Donate</button></form>");

    $('#donateModal .modal-body').append("<form action=" + url + " method='POST' id='payment-form'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrftoken + "' />");
    $('#donateModal .modal-body').append("<div class='btn-group btn-group-toggle' data-toggle='buttons'><label class='btn btn-purple'><input type='checkbox' name='amount' class='preset-amount' value=5 />$5</label><label class='btn btn-purple'><input type='checkbox' name='amount' class='preset-amount' value=10 />$10</label><label class='btn btn-purple'><input type='checkbox' name='amount' class='preset-amount' value=25 />$25</label><label class='btn btn-purple'><input type='checkbox' name='amount' class='preset-amount' value=50 />$50</label><label class='btn btn-purple'><input type='checkbox' name='amount' class='preset-amount' value=100 />$100</label></div>");
    $('#donateModal .modal-body').append("<div class='input-group'><div class='input-group-prepend'><span class='input-group-text'>$</span></div><input type='number' class='form-control' id='id_amount' min='0' max='999999' aria-label='Amount' placeholder='Custom amount'></div>");
    $('#donateModal .modal-body').append("<div class='form-check'><input type='checkbox' name='anonymous_amount' class='form-check-input' id='id_anonymous_amount'><label class='form-check-label' for='id_anonymous_amount'>Anonymous amount</label></div>");
    $('#donateModal .modal-body').append("<div id='amount-errors'></div>");
    $('#donateModal .modal-body').append("<div class='form-check'><input type='checkbox' name='anonymous_donor' class='form-check-input' id='id_anonymous_donor'><label class='form-check-label' for='id_anonymous_donor'>Anonymous donor</label></div>");
    $('#donateModal .modal-body').append("<div class='form-group'><textarea class='form-control' name='comment' id='id_comment' rows='3' placeholder='Type your comment here (optional)'></textarea></div>");
    $('#donateModal .modal-body').append("<div class='form-check'><input type='checkbox' name='monthly' class='form-check-input' id='id_monthly'><label class='form-check-label' for='id_monthly'>Monthly</label></div>");
    $('#donateModal .modal-body').append("<p><a id='new-card' href=''>New card</a></p><div id='new-card-info' style='display:none;'><p><label for='id_save_card'>Save card:</label> <input type='checkbox' name='save_card' id='id_save_card' /></p><div id='card-element'></div><div id='card-errors' role='alert'></div></div>");
//    $('#donateModal .modal-body').append("");
//    $('#donateModal .modal-body').append("");
//    $('#donateModal .modal-body').append("");
//    $('#donateModal .modal-body').append("");

    $.get(url, function (data) {
        $.each(data, function(key, value) {
            console.log("default = " + value.default);
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

