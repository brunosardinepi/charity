function sort(event, column) {
    var parent_th = $(event.target).parent("th");
    if (parent_th.hasClass("desc")) {
        var sort_by = "asc";
    } else {
        var sort_by = "desc";
    };

    $.ajax({
        url : "/campaign/dashboard/ajax/donations/",
        type : "POST",
        traditional: true,
        data : {
            campaign_pk : campaign_pk,
            sort_by : sort_by,
            column : column,
        },
        success : function(result) {
            $("#donation-history-body").empty();
            parent_th.attr("class", sort_by);
            for (var key in result) {
                var date = result[key]["date"];
                if (result[key]["anonymous_amount"] == true) {
                    var amount = "Anonymous";
                } else if (result[key]["anonymous_amount"] == false) {
                    var amount = "$" + result[key]['amount'] / 100;
                };
                if (result[key]["anonymous_donor"] == true) {
                    var donor = "Anonymous";
                } else if (result[key]["anonymous_donor"] == false) {
                    var donor = result[key]["user"]["first_name"] + " " + result[key]["user"]["last_name"];
                };
                $("#donation-history-body").append("<tr><td>" + date + "</td><td>" + amount + "</td><td>" + donor + "</td></tr>");
            }
        }
    });
};

$(document).on("click", ".sort", function(event) {
    event.preventDefault();
    var column = $(event.target).attr("id");
    sort(event, column);
});

