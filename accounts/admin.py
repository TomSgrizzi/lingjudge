# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, NativeLanguage

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # Extend the fieldsets to include your additional fields
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('date_of_birth', 'affiliation', 'native_languages'),
        }),
    )

    # Also add to list_display for easier admin view
    list_display = ('username', 'email', 'date_of_birth', 'affiliation')

@admin.register(NativeLanguage)
class NativeLanguageAdmin(admin.ModelAdmin):
    list_display = ('name',)
