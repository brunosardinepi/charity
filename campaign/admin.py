from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from . import models


class CampaignAdmin(GuardedModelAdmin):
    list_display = ('id', 'name', 'campaign_slug', 'trending_score', 'page', 'type', 'deleted', 'is_active',)
    ordering = ('id', 'name', 'campaign_slug', 'trending_score', 'page', 'type',)
    list_filter = ('page', 'type', 'deleted', 'is_active',)
    filter_horizontal = ('campaign_admins', 'campaign_managers',)

class CampaignImageAdmin(admin.ModelAdmin):
    list_display = ('uploaded_by', 'campaign', 'caption', 'profile_picture', 'uploaded_at',)
    ordering = ('campaign', 'uploaded_at',)
    list_filter = ('campaign', 'profile_picture',)

class VoteParticipantAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'name',)
    ordering = list_display
    list_filter = ('campaign',)

admin.site.register(models.Campaign, CampaignAdmin)
admin.site.register(models.CampaignImage, CampaignImageAdmin)
admin.site.register(models.VoteParticipant, VoteParticipantAdmin)
