from django.contrib import admin

from . import models


class StripePlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'interval',)
    ordering = ('user', 'amount',)
    list_filter = ('user',)

admin.site.register(models.StripePlan, StripePlanAdmin)
