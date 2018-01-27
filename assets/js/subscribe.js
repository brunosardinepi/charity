$(document).on("click", "#subscribe", function(event) {
    event.preventDefault();
    var action = $("#subscribe").attr("name");
    var url = "/" + model + "/subscribe/" + model_pk + "/" + action + "/";
    $.get(url, function (data) {
        subscribe_attr = JSON.parse(data);
        $("#subscribe").attr("name", subscribe_attr.name);
        $("#subscribe").text(subscribe_attr.value);
    });
});
