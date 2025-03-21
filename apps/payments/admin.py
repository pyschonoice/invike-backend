from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'amount', 'manually_confirmed', 'created_at')
    list_filter = ('status', 'manually_confirmed', 'created_at')
    search_fields = ('user__name', 'user__email', 'event__title', 'confirmation_notes')
    raw_id_fields = ('user', 'event', 'confirmed_by')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('event', 'user', 'status', 'amount', 'payment_link', 'description')
        }),
        ('Confirmation', {
            'fields': ('manually_confirmed', 'confirmed_by', 'confirmation_notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )