from django.db import models
#from django.core.urlresolvers import reverse
from django.urls import reverse
from django.utils.text import slugify
from userprofile.models import UserProfile


class Page(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    page_slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    donation_count = models.IntegerField(default=0)
    donation_money = models.IntegerField(default=0)
    admins = models.ManyToManyField(UserProfile, related_name='page_admins', blank=True)
    managers = models.ManyToManyField(UserProfile, related_name='page_managers', blank=True)
    subscribers = models.ManyToManyField(UserProfile, related_name='subscribers', blank=True)
    is_sponsored = models.BooleanField(default=False)
    CATEGORY_CHOICES = (
        ('animal', 'Animal'),
        ('environment', 'Environment'),
        ('education', 'Education'),
        ('religious', 'Religious'),
    )
    category = models.CharField(
        max_length=255,
        choices=CATEGORY_CHOICES,
        default='',
    )

    class Meta:
        permissions = (
            ('manager_edit', 'Manager -- edit Page'),
            ('manager_delete', 'Manager -- delete Page'),
            ('manager_invite', 'Manager -- invite users to manage Page'),
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('page', kwargs={
            'page_slug': self.page_slug
            })

    def save(self, *args, **kwargs):
        if self.id:
            self.page_slug = slugify(self.page_slug).replace('-', '')
            super(Page, self).save(*args, **kwargs)
        elif not self.id:
            self.page_slug = slugify(self.name).replace('-', '')
            super(Page, self).save(*args, **kwargs)

class PageImage(models.Model):
    icon = models.ImageField(upload_to='media/pages/', blank=True, null=True)
    page_id = models.ForeignKey(Page)

