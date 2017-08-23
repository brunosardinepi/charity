from django.contrib import admin

from . import models


class ManagerInvitationAdmin(admin.ModelAdmin):
    list_display = ('invite_to', 'invite_from', 'date_created', 'accepted', 'expired',)
    ordering = ('invite_to', 'invite_from', 'date_created', 'accepted', 'expired',)
    list_filter = ('accepted', 'expired',)

admin.site.register(models.ManagerInvitation, ManagerInvitationAdmin)
