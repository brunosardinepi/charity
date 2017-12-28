function vote(event) {
    var obj = $(event.target).parent('a').attr("id");
    var vote = $(event.target).parent('a').attr("class");

    $.ajax({
        url : "/votes/vote/",
        type : "POST",
        traditional: true,
        data : {
            obj : obj,
            vote : vote,
        },
        success : function(result) {
            $("#upvote-count-" + result.type + "-" + result.pk).text(result.upvotes);
            $("#downvote-count-" + result.type + "-" + result.pk).text(result.downvotes);
            if (result.vote == "upvote") {
                $("#upvotes-" + result.type + "-" + result.pk).attr("class", "vote upvote user-vote");
                $("#downvotes-" + result.type + "-" + result.pk).attr("class", "vote downvote");
            } else if (result.vote == "downvote") {
                $("#downvotes-" + result.type + "-" + result.pk).attr("class", "vote downvote user-vote");
                $("#upvotes-" + result.type + "-" + result.pk).attr("class", "vote upvote");
            }
        }
    });
};

$(document).on("click", "a[class^=vote]", function(event) {
   event.preventDefault();
   vote(event);
});
