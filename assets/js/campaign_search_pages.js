function search() {
    var q = $('#q').val();
    console.log(q);
//    q = q.split(/[ ]+/).join(',');

    $.ajax({
        url : "/create/campaign/search/",
        type : "POST",
        traditional: true,
        data : {
            q : q,
        },
        success : function(result) {
            $("#results-list").empty();
            for (var key in result) {
                if (result[key]["city"]) {
                    var location = result[key]["city"] + ", " + result[key]["state"];
                } else if (result[key]["state"]) {
                    var location = result[key]["state"];
                } else {
                    var location = "";
                }
                $("#results-list").append("<li><input type='radio' name='page' value='" + result[key]['pk'] + "' />" + result[key]['name'] + " - " + location + "</li>");
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
