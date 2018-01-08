$(document).ready(function() {
    $('#newComment').on('shown.bs.modal', function () {
        $('#id_comment').trigger('focus');
    });
});

$(document).on("click", "#submit-comment", function(event) {
    console.log("clicked #submit-comment");
    $("#comment-form").submit();
});

$(document).on('click', ".delete-cr", function(event) {
    event.preventDefault();
    var arr = $(this).attr('id');
    var arr = arr.split('-');
    var url = "/comments/delete/" + arr[1] + "/" + arr[2] + "/";
    $.get(url, function () {
        $("#" + arr[1] + "-" + arr[2]).remove();
    });
});
