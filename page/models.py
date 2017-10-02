from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from userprofile.models import UserProfile


class Page(models.Model):
    admins = models.ManyToManyField(UserProfile, related_name='page_admins', blank=True)
    city = models.CharField(max_length=255, blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    deleted_on = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    donation_count = models.IntegerField(default=0)
    donation_money = models.IntegerField(default=0)
    is_sponsored = models.BooleanField(default=False)
    managers = models.ManyToManyField(UserProfile, related_name='page_managers', blank=True)
    name = models.CharField(max_length=255, db_index=True)
    page_slug = models.SlugField(max_length=100, unique=True)
    subscribers = models.ManyToManyField(UserProfile, related_name='subscribers', blank=True)

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

    STATE_CHOICES = (
        ('AL', 'Alabama'),
        ('AK', 'Alaska'),
        ('AZ', 'Arizona'),
        ('AR', 'Arkansas'),
        ('CA', 'California'),
        ('CO', 'Colorado'),
        ('CT', 'Connecticut'),
        ('DE', 'Delaware'),
        ('FL', 'Florida'),
        ('GA', 'Georgia'),
        ('HI', 'Hawaii'),
        ('ID', 'Idaho'),
        ('IL', 'Illinois'),
        ('IN', 'Indiana'),
        ('IA', 'Iowa'),
        ('KS', 'Kansas'),
        ('KY', 'Kentucky'),
        ('LA', 'Louisiana'),
        ('ME', 'Maine'),
        ('MD', 'Maryland'),
        ('MA', 'Massachusetts'),
        ('MI', 'Michigan'),
        ('MN', 'Minnesota'),
        ('MS', 'Mississippi'),
        ('MO', 'Missouri'),
        ('MT', 'Montana'),
        ('NE', 'Nebraska'),
        ('NV', 'Nevada'),
        ('NH', 'New Hampshire'),
        ('NJ', 'New Jersey'),
        ('NM', 'New Mexico'),
        ('NY', 'New York'),
        ('NC', 'North Carolina'),
        ('ND', 'North Dakota'),
        ('OH', 'Ohio'),
        ('OK', 'Oklahoma'),
        ('OR', 'Oregon'),
        ('PA', 'Pennsylvania'),
        ('RI', 'Rhode Island'),
        ('SC', 'South Carolina'),
        ('SD', 'South Dakota'),
        ('TN', 'Tennessee'),
        ('TX', 'Texas'),
        ('UT', 'Utah'),
        ('VT', 'Vermont'),
        ('VA', 'Virginia'),
        ('WA', 'Washington'),
        ('WV', 'West Virginia'),
        ('WI', 'Wisconsin'),
        ('WY', 'Wyoming'),
    )
    state = models.CharField(
        max_length=100,
        choices=STATE_CHOICES,
        default='',
    )

    TYPE_CHOICES = (
        ('organization', 'Organization'),
        ('personal', 'Personal'),
    )
    type = models.CharField(
        max_length=255,
        choices=TYPE_CHOICES,
        default='',
    )

    class Meta:
        permissions = (
            ('manager_edit', 'Manager -- edit Page'),
            ('manager_delete', 'Manager -- delete Page'),
            ('manager_invite', 'Manager -- invite users to manage Page'),
            ('manager_upload', 'Manager -- upload media to Page'),
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

class PageImages(models.Model):
    page = models.ForeignKey('page.Page', on_delete=models.CASCADE)
    image = models.FileField(upload_to='media/pages/images/', blank=True, null=True)
    caption = models.CharField(max_length=255, blank=True)
    page_profile = models.BooleanField(default=False)
