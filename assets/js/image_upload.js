$(function () {
    $("#upload-button").click(function () {
        $("#upload-input").click();
    });

    $("#upload-input").fileupload({
        dataType: 'json',
        done: function (event, data) {
            if (data.result.is_valid == 't') {
                if (!$("#image-list").length) {
                    $("<ul id='image-list'></ul>").insertAfter("#images-header");
                    $("p:contains('No images!')").remove();
                };
                $("#image-list").prepend("<li id='image-" + data.result.pk + "'><span class='profile' id='profile-" + data.result.pk + "'><a class='set-profile-picture' href=''>Make profile picture</a> - </span><a href='" + data.result.url + "'>" + data.result.name + "</a> - <a id='delete-" + data.result.pk + "' class='delete-image' href=''>Delete</a></li>");
            } else {
                if (data.result.redirect == "error_size") {
                    var url = "/error/image/size/";
                } else if (data.result.redirect == "error_type") {
                    var url = "/error/image/type/";
                };
                window.location.href = url;
            };
        }
    });
});
