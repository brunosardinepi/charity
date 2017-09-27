from django.contrib import admin

from . import models


class DonationAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'amount', 'page', 'campaign',)
    ordering = ('user', 'date', 'amount',)
    list_filter = ('user',)

admin.site.register(models.Donation, DonationAdmin)
