from django.contrib import admin

from . import models


class ManagerInvitationAdmin(admin.ModelAdmin):
    list_display = ('invite_to', 'invite_from', 'page', 'campaign', 'date_created', 'expired', 'accepted', 'declined',)
    ordering = list_display
    list_filter = ('expired', 'accepted', 'declined', 'page', 'campaign',)

class ForgotPasswordRequestAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_created', 'expired', 'completed',)
    ordering = ('email', 'date_created',)
    list_filter = ('expired', 'completed',)

admin.site.register(models.ManagerInvitation, ManagerInvitationAdmin)
admin.site.register(models.ForgotPasswordRequest, ForgotPasswordRequestAdmin)
