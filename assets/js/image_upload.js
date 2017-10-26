$(function () {
    $("#upload-button").click(function () {
        $("#upload-input").click();
    });

    $("#upload-input").fileupload({
        dataType: 'json',
        done: function (event, data) {
            if (data.result.is_valid) {
                $("#image-list").prepend(
                    "<li><a href='" + data.result.url + "'>" + data.result.name + "</a></li>"
                )
            }
        }
    });
});
