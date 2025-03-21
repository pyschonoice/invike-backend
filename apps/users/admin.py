from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'name', 'role', 'is_staff', 'date_joined')
    search_fields = ('email', 'name')
    readonly_fields = ('date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('name', 'avatar', 'phone_number')}),
        ('Social Auth', {'fields': ('google_id', 'apple_id')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'name', 'role'),
        }),
    )

admin.site.register(User, CustomUserAdmin)