from django.contrib import admin
from .models import ParametreApp, UserProfile


@admin.register(ParametreApp)
class ParametreAppAdmin(admin.ModelAdmin):
    list_display = ('nom_entreprise', 'email_contact', 'telephone', 'updated_at')
    search_fields = ('nom_entreprise', 'email_contact')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'fonction', 'telephone', 'updated_at')
    search_fields = ('user__username', 'user__email', 'fonction')
