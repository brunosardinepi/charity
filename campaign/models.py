from django.db import models
from django.utils.text import slugify


class Campaign(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    campaign_slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    donation_count = models.IntegerField(default=0)
    donation_money = models.IntegerField(default=0)
    TYPE_CHOICES = (
        ('event', 'Event'),
    )
    type = models.CharField(
        max_length=255,
        choices=TYPE_CHOICES,
        default='Event',
    )
    page = models.ForeignKey(
        'page.Page',
        on_delete=models.CASCADE,
        related_name='campaigns',
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.id:
            self.campaign_slug = slugify(self.campaign_slug)
            super(Campaign, self).save(*args, **kwargs)
        elif not self.id:
            self.campaign_slug = slugify(self.name)
            super(Campaign, self).save(*args, **kwargs)