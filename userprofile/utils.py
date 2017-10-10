from django.shortcuts import get_object_or_404

import stripe

from . import models
from pagefund import settings


def get_user_credit_cards(userprofile):
    cards = {}
    if not settings.TESTING:
        try:
            sc = stripe.Customer.retrieve(userprofile.stripe_customer_id).sources.all(object='card')
            print(sc)
            for c in sc:
                card = get_object_or_404(models.StripeCard, stripe_card_id=c.id)
                cards[card.id] = {
                    'exp_month': c.exp_month,
                    'exp_year': c.exp_year,
                    'name': card.name,
                    'id': card.id
                }
        except stripe.error.InvalidRequestError:
            metadata = {'user_pk': userprofile.user.pk}
            customer = stripe.Customer.create(
                email=userprofile.user.email,
                metadata=metadata
            )

            userprofile.stripe_customer_id = customer.id
            userprofile.save()
    return cards

