function vote(event) {
    var obj = $(event.target).parent().attr("id");
    var vote = $(event.target).attr("class");

    $.ajax({
        url : "/votes/vote/",
        type : "POST",
        traditional: true,
        data : {
            obj : obj,
            vote : vote,
        },
        success : function(result) {
            $("#upvotes-" + result.type + "-" + result.pk).text(result.upvotes);
            $("#downvotes-" + result.type + "-" + result.pk).text(result.downvotes);
        }
    });
};

$(document).on("click", "button[class^=vote]", function(event) {
   event.preventDefault();
   vote(event);
});
