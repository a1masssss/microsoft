from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin interface for Transaction model."""
    
    list_display = [
        'transaction_id',
        'transaction_timestamp',
        'card_id',
        'issuer_bank_name',
        'merchant_id',
        'mcc_category',
        'merchant_city',
        'transaction_type',
        'transaction_amount_kzt',
        'transaction_currency',
        'pos_entry_mode',
        'wallet_type',
    ]
    
    list_filter = [
        'transaction_type',
        'issuer_bank_name',
        'mcc_category',
        'merchant_city',
        'transaction_currency',
        'pos_entry_mode',
        'wallet_type',
        'acquirer_country_iso',
        'transaction_timestamp',
    ]
    
    search_fields = [
        'transaction_id',
        'card_id',
        'merchant_id',
        'issuer_bank_name',
        'merchant_city',
        'mcc_category',
    ]
    
    readonly_fields = [
        'transaction_id',
        'created_at',
        'updated_at',
    ]
    
    date_hierarchy = 'transaction_timestamp'
    
    list_per_page = 50
    
    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'transaction_id',
                'transaction_timestamp',
                'transaction_type',
            )
        }),
        ('Card Information', {
            'fields': (
                'card_id',
                'expiry_date',
                'issuer_bank_name',
            )
        }),
        ('Merchant Information', {
            'fields': (
                'merchant_id',
                'merchant_mcc',
                'mcc_category',
                'merchant_city',
            )
        }),
        ('Transaction Details', {
            'fields': (
                'transaction_amount_kzt',
                'original_amount',
                'transaction_currency',
                'acquirer_country_iso',
            )
        }),
        ('Payment Method', {
            'fields': (
                'pos_entry_mode',
                'wallet_type',
            )
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def has_add_permission(self, request):
        """Allow manual addition of transactions via admin."""
        return True