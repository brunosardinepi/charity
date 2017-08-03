from django.db import models
from django.utils.text import slugify


class Page(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    donation_count = models.IntegerField(default=0)
    donation_money = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.id:
            self.slug = slugify(self.slug).replace('-', '')
            super(Page, self).save(*args, **kwargs)
        elif not self.id:
            self.slug = slugify(self.name).replace('-', '')
            super(Page, self).save(*args, **kwargs)

