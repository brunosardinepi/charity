$(document).on("click", "#form-submit", function(event) {
    event.preventDefault();
    if (!$("input:checked").length) {
        alert("Please choose at least one permission");
    } else {
        $("#invite-form").submit();
    };
});

