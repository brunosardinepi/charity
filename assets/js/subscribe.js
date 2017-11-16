$(document).on("click", "#subscribe", function(event) {
    var action = $("#subscribe").attr("name");
    var url = "/" + model + "/subscribe/" + model_pk + "/" + action + "/";
    $.get(url, function (data) {
        subscribe_attr = JSON.parse(data);
        $("#subscribe").attr("name", subscribe_attr.name);
        $("#subscribe").css("background-color", subscribe_attr.color);
        $("#subscribe").text(subscribe_attr.value);
    });
});
