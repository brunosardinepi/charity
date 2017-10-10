import stripe


def get_card_source(request):
    customer = stripe.Customer.retrieve("%s" % request.user.userprofile.stripe_customer_id)
    customer_cards = request.user.userprofile.stripecard_set.all()
    card_check = stripe.Token.retrieve(request.POST.get('stripeToken'))
    customer_card_dict = {}
    if customer_cards:
        for c in customer_cards:
            if c.stripe_card_fingerprint == card_check['card']['fingerprint']:
                card_source = c.stripe_card_id
                break
            else:
                card_source = None
    else:
        card_source = None
    return customer, card_source

