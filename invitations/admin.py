from django.contrib import admin

from . import models


class ManagerInvitationAdmin(admin.ModelAdmin):
    list_display = ('invite_to', 'invite_from', 'page', 'campaign', 'date_created', 'expired', 'accepted', 'declined',)
#    ordering = ('invite_to', 'invite_from', 'page', 'campaign', 'date_created', 'expired', 'accepted', 'declined',)
    ordering = list_display
    list_filter = ('expired', 'accepted', 'declined', 'page', 'campaign',)

class GeneralInvitationAdmin(admin.ModelAdmin):
    list_display = ('invite_to', 'invite_from', 'date_created', 'expired', 'accepted', 'declined',)
#    ordering = ('invite_to', 'invite_from', 'date_created', 'expired', 'accepted', 'declined',)
    ordering = list_display
    list_filter = ('expired', 'accepted', 'declined',)

admin.site.register(models.ManagerInvitation, ManagerInvitationAdmin)
admin.site.register(models.GeneralInvitation, GeneralInvitationAdmin)
