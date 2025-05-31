from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin
from django.contrib.auth.models import User

from user_register.models import UserProfile, PetUserProfile


class PetUserProfileInline(admin.StackedInline):
    model = PetUserProfile
    can_delete = False


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


class CustomUserAdmin(OriginalUserAdmin):
    inlines = (UserProfileInline, PetUserProfileInline)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
