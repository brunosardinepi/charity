$(document).on("change", "#id_type", function() {
    if($(this).val() === "nonprofit"){
        $("#ein-row").show()
    } else {
        $("#ein-row").hide()
    }
});
