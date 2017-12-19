$(document).on("change", "#id_type", function() {
    if($(this).val() === "personal"){
        $("#id_ein").hide()
    } else {
        $("#id_ein").show()
    }
});
