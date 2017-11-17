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

class UserImageAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_picture',)
    ordering = list_display
    list_filter = list_display

class StripeCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'stripe_card_id', 'default',)
    ordering = ('user', 'name',)
    list_filter = ('user', 'default', )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(models.UserImage, UserImageAdmin)
admin.site.register(models.StripeCard, StripeCardAdmin)
