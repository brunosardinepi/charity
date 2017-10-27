from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from . import models


class CampaignAdmin(GuardedModelAdmin):
    list_display = ('id', 'name', 'campaign_slug', 'page', 'deleted',)
    ordering = ('id', 'name', 'campaign_slug', 'page',)
    list_filter = ('page', 'deleted',)
    filter_horizontal = ('campaign_admins', 'campaign_managers',)

class CampaignImageAdmin(admin.ModelAdmin):
    list_display = ('uploaded_by', 'campaign', 'caption', 'profile_picture', 'uploaded_at',)
    ordering = ('campaign', 'uploaded_at',)
    list_filter = ('campaign', 'profile_picture',)


admin.site.register(models.Campaign, CampaignAdmin)
admin.site.register(models.CampaignImage, CampaignImageAdmin)
