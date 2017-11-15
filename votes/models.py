from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    SCORE_CHOICES = (
        (1, 'upvote'),
        (-1, 'downvote'),
    )
    score = models.SmallIntegerField(
        choices=SCORE_CHOICES,
    )
    comment = models.ForeignKey('comments.Comment',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    reply = models.ForeignKey('comments.Reply',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    faq = models.ForeignKey('faqs.FAQ',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
