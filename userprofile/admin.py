from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from . import models


class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, )

class StripeCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'stripe_card_id',)
    ordering = ('user',)
    list_filter = ('user',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(models.StripeCard, StripeCardAdmin)
