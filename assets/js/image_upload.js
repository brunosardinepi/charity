$(function () {
    $("#upload-button").click(function () {
        $("#upload-input").click();
    });

    $("#upload-input").fileupload({
        dataType: 'json',
        done: function (event, data) {
            if (data.result.is_valid == 't') {
                $("#image-list").prepend("<li id='image-" + data.result.pk + "'><a href='" + data.result.url + "'>" + data.result.name + "</a> - <a id='delete-" + data.result.pk + "' class='delete-image' href=''>Delete</a></li>");
            } else {
                if (data.result.redirect == "error_size") {
                    var url = "/error/image/size/";
                } else if (data.result.redirect == "error_type") {
                    var url = "/error/image/type/";
                }
                window.location.href = url;
            }
        }
    });
});
