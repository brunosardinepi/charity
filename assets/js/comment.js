$(document).ready(function() {
    $('#newComment').on('shown.bs.modal', function () {
        $('#id_comment').trigger('focus');
    });
});

$(document).on("click", "#submit-comment", function(event) {
    $("#comment-form").submit();
});
