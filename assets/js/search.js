function search(a) {
    var checked = document.getElementsByName('filters[]');
    var filters = [];
    for (c = 0; c < checked.length; c++) {
        if (checked[c].checked) {
            filters.push(checked[c].value);
        }
    }
    var q = $('#q').val();
    q = q.split(/[ ]+/).join(',');

    var url = "/search/results/";
    filters = JSON.stringify(filters);

    $.ajax({
        url : url,
        type : "POST",
        traditional: true,
        data : {
            q : q,
            f : filters,
            a : a
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
    search("false");
});

$(document).on('keypress', '#q', function(event) {
    if (event.keyCode == 13) {
        event.preventDefault();
        return false;
    }
});

$(document).ready(function() {
    $(":checkbox").change(function() {
        search("false");
    });
});

$(document).ready(function() {
    $("#checkall").click(function(event) {
        event.preventDefault();
        var checkboxes = $(document.getElementsByName('filters[]'));
        checkboxes.prop('checked', !checkboxes.prop('checked')).change();
    });

    $("#allPages").click(function(event) {
        event.preventDefault();
        search("pages");
    });

    $("#allCampaigns").click(function(event) {
        event.preventDefault();
        search("campaigns");
    });
});

