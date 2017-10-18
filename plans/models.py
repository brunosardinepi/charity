from django.db import models
from django.contrib.auth.models import User


class StripePlan(models.Model):
    amount = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    INTERVAL_CHOICES = (
        ('monthly', 'Monthly'),
    )
    interval = models.CharField(
        max_length=20,
        choices=INTERVAL_CHOICES,
        default='monthly',
    )

    def __str__(self):
        return "%s%s-%s" % (self.user.first_name, self.user.last_name, self.pk)
