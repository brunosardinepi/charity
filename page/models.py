from collections import OrderedDict

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from campaign.models import Campaign
from comments.models import Comment
from donation.models import Donation


class Page(models.Model):
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    admins = models.ManyToManyField('userprofile.UserProfile', related_name='page_admins', blank=True)
    city = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(max_length=128, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    deleted_on = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    donation_count = models.IntegerField(default=0)
    donation_money = models.IntegerField(default=0)
    ein = models.CharField(max_length=255)
    is_sponsored = models.BooleanField(default=False)
    managers = models.ManyToManyField('userprofile.UserProfile', related_name='page_managers', blank=True)
    name = models.CharField(max_length=255, db_index=True)
    nonprofit_number = models.CharField(max_length=255, blank=True)
    page_slug = models.SlugField(max_length=100, unique=True)
    subscribers = models.ManyToManyField('userprofile.UserProfile', related_name='subscribers', blank=True)
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_bank_account_id = models.CharField(max_length=255, blank=True, null=True)
    trending_score = models.DecimalField(default=0, max_digits=10, decimal_places=1)
    website = models.CharField(max_length=128, blank=True)
    zipcode = models.CharField(max_length=5)

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
        ('nonprofit', 'Nonprofit'),
        ('personal', 'Personal'),
        ('religious', 'Religious'),
        ('other', 'Other'),
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
            ('manager_image_edit', 'Manager -- upload and edit media on Page'),
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

    def top_donors(self):
        donors = Donation.objects.filter(page=self).values_list('user', flat=True).distinct()
        top_donors = {}
        for d in donors:
            user = get_object_or_404(User, pk=d)
            total_amount = Donation.objects.filter(user=user, page=self, anonymous_donor=False).aggregate(Sum('amount')).get('amount__sum')
            if total_amount is not None:
                top_donors[d] = {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'amount': total_amount
                }
        top_donors = OrderedDict(sorted(top_donors.items(), key=lambda t: t[1]['amount'], reverse=True))
        top_donors = list(top_donors.items())[:10]
        return top_donors

    def managers_list(self):
        return self.managers.all()

    def images(self):
        return PageImages.objects.filter(page=self)

    def profile_image(self):
        try:
            return PageImages.objects.filter(page=self, page_profile=True)
        except PageImages.MultipleObjectsReturned:
            # create an exception for future use
            print("multiple profile images returned")

    def active_campaigns(self):
        return Campaign.objects.filter(page=self, is_active=True, deleted=False)

    def inactive_campaigns(self):
        return Campaign.objects.filter(page=self, is_active=False, deleted=False)

    def comments(self):
        return Comment.objects.filter(page=self, deleted=False).order_by('-date')

    def donations(self):
        return Donation.objects.filter(page=self).order_by('-date')


class PageImages(models.Model):
    page = models.ForeignKey('page.Page', on_delete=models.CASCADE)
    image = models.FileField(upload_to='media/pages/images/', blank=True, null=True)
    caption = models.CharField(max_length=255, blank=True)
    page_profile = models.BooleanField(default=False)
