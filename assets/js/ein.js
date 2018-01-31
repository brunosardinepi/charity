$(document).on("change", "#id_type", function() {
    if($(this).val() === "nonprofit"){
        $("#ein-row").show()
    } else {
        $("#ein-row").hide()
    }
});

$(document).on("click", "#form-input", function(event) {
    event.preventDefault();
    var type = $("#id_type");
    var ein = $("#id_ein");
    if (type.val() == "nonprofit") {
        if (ein.val().length) {
            $("#create-form").submit();
        } else {
            alert("Please add your EIN, or change the Page type to 'Personal'.");
        };
    } else {
        $("#create-form").submit();
    };
});

