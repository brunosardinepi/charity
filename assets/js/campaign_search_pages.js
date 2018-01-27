function search() {
    var q = $('#q').val();

    $.ajax({
        url : "/create/campaign/search/",
        type : "POST",
        traditional: true,
        data : {
            q : q,
        },
        success : function(json) {
            $("#results").empty();
            for (var key in json) {
                $("#results").append(json[key]);
            }
        }
    });
};

$(document).on('keyup', '#q', function() {
    search();
});

$(document).on('keypress', '#q', function(event) {
    if (event.keyCode == 13) {
        event.preventDefault();
        return false;
    }
});
