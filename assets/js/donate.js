$(document).ready(function() {
    $('#donateModal').on('shown.bs.modal', function () {
        $('#id_amount').trigger('focus');
    });
});

$(document).on('change', "input.preset-amount", function() {
    console.log("input.preset-amount changed");
    $("input.preset-amount").not(this).prop("checked", false);
});

$(document).on('click', "#new-card", function(event) {
    event.preventDefault();
    $("#new-card-info").show();
    $("#new-card").text("Cancel new card");
    $("#new-card").attr("id", "hide-new-card");
});

$(document).on('click', "#hide-new-card", function(event) {
    event.preventDefault();
    $("#new-card-info").hide();
    $("#hide-new-card").text("New card");
    $("#hide-new-card").attr("id", "new-card");
});

//var stripe = Stripe('{{ api_pk }}');
var elements = stripe.elements();
var card = elements.create('card');
console.log("stripe = " + JSON.stringify(stripe));
console.log("elements = " + elements);
console.log("card = " + card);

$(document).on('click', "[id^='show-donate']", function(event) {
    event.preventDefault();

    var arr = $(this).attr('id');
    var arr = arr.split("-");
    var model = arr[2];
    var pk = arr[3];

    var url = "/profile/card/list/";

    $.get(url, function (data) {
        var cards = "";
        $.each(data, function(key, value) {
            console.log("default = " + value.default);
            var checked = ((value.default == true) ? 'checked' : '');
            console.log("checked = " + checked);
            cards += "<input type='radio' name='saved_card' class='saved-card' value='" + value.id + "' " + checked + "/> " + value.name + " (" + value.last4 + ")<br />";
        });
        console.log("cards = " + cards);
        var url = "/page/" + pk + "/donate/";

       $('#donateModal .modal-body').append("<form action=" + url + " method='POST' id='payment-form'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrftoken + "' /><input type='checkbox' name='amount' class='preset-amount' value=5 />$5<br /><input type='checkbox' name='amount' class='preset-amount' value=10 />$10<br /><input type='checkbox' name='amount' class='preset-amount' value=25 />$25<br /><input type='checkbox' name='amount' class='preset-amount' value=50 />$50<br /><input type='checkbox' name='amount' class='preset-amount' value=100 />$100<br /><div class='input-group'><div class='input-group-prepend'><span class='input-group-text'>$</span></div><input type='number' class='form-control' name='amount' id='id_amount' min='0' max='999999' aria-label='Amount' placeholder='Custom amount'></div><div class='form-check'><input type='checkbox' name='anonymous_amount' class='form-check-input' id='id_anonymous_amount'><label class='form-check-label' for='id_anonymous_amount'>Anonymous amount</label></div><div id='amount-errors'></div><div class='form-check'><input type='checkbox' name='anonymous_donor' class='form-check-input' id='id_anonymous_donor'><label class='form-check-label' for='id_anonymous_donor'>Anonymous donor</label></div><div class='form-group'><textarea class='form-control' name='comment' id='id_comment' rows='3' placeholder='Type your comment here (optional)'></textarea></div><div class='form-check'><input type='checkbox' name='monthly' class='form-check-input' id='id_monthly'><label class='form-check-label' for='id_monthly'>Monthly</label></div>" + cards + "<p><a id='new-card' href=''>New card</a></p><div id='new-card-info' style='display:none;'><p><label for='id_save_card'>Save card:</label> <input type='checkbox' name='save_card' id='id_save_card' /></p><div id='card-element'></div><div id='card-errors' role='alert'></div></div></form>");

//        var stripe = Stripe('{{ api_pk }}');
//        var elements = stripe.elements();
//        var card = elements.create('card');
        card.mount("#card-element");

        card.addEventListener('change', function(event) {
            var displayError = document.getElementById('card-errors');
            if (event.error) {
                displayError.textContent = event.error.message;
            } else {
                displayError.textContent = '';
            }
        });

        $('#donateModal .modal-footer').html("<button type='button' class='btn btn-secondary' data-dismiss='modal'>Close</button><button type='button' class='btn btn-primary submit-donate' data-dismiss='modal'>Donate</button>");
    });
});

$(document).on("click", ".submit-donate", function(event) {
    donate();
});

function donate() {
console.log("stripe = " + stripe);
console.log("elements = " + elements);
console.log("card = " + card);

            if (document.getElementById("id_anonymous_donor").checked) {
                var extraDetails = {};
            } else {
                var extraDetails = {
                    name: "{{ request.user.first_name }} {{ request.user.last_name }}",
                };
            };

            if ($("#hide-new-card").length > 0) {
                console.log("hide-new-card length");
                console.log($("#hide-new-card").length);
                $("input.saved-card").prop("checked", false);
                stripe.createToken(card, extraDetails).then(function(result) {
                    if (result.error) {
                        var errorElement = document.getElementById('card-errors');
                        errorElement.textContent = result.error.message;
                    } else {
                        stripeTokenHandler(result.token);
                    }
                });
            } else if ($("#new-card").length > 0) {
                console.log("new-card length");

                if (($("input.preset-amount:checked").length == 0) && ($("#id_amount").val().length == 0)) {
                    console.log("bad, nothing is checked and amount is empty");
                    $("#amount-errors").html("Please select an amount to donate.");
                } else {
                    console.log("good, something is either checked or the amount is not empty");
                    $("#amount-errors").html("");
                    var form = document.getElementById("payment-form");
                    form.submit();
                };
            };
};

function stripeTokenHandler(token) {
    var form = document.getElementById("payment-form");
    var hiddenInput = document.createElement("input");
    hiddenInput.setAttribute("type", "hidden");
    hiddenInput.setAttribute("name", "stripeToken");
    hiddenInput.setAttribute("value", token.id);
    form.appendChild(hiddenInput);
    form.submit();
}
