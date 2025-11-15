from django.db import models

class Transaction(models.Model):
    """
    Model representing financial transactions from the Parquet dataset.
    Contains 11.5M+ transaction records with card, merchant, and transaction details.
    """
    
    # Transaction identifiers
    transaction_id = models.CharField(
        max_length=255, 
        unique=True, 
        db_index=True,
        help_text="Unique identifier for the transaction (UUID format)"
    )
    transaction_timestamp = models.DateTimeField(
        db_index=True,
        help_text="Timestamp when the transaction occurred"
    )
    
    # Card information
    card_id = models.BigIntegerField(
        db_index=True,
        help_text="Identifier for the card used in the transaction"
    )
    expiry_date = models.CharField(
        max_length=10,
        help_text="Card expiry date in MM/YY format"
    )
    issuer_bank_name = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Name of the bank that issued the card"
    )
    
    # Merchant information
    merchant_id = models.BigIntegerField(
        db_index=True,
        help_text="Unique identifier for the merchant"
    )
    merchant_mcc = models.IntegerField(
        db_index=True,
        help_text="Merchant Category Code (MCC)"
    )
    mcc_category = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Human-readable category of the merchant (e.g., 'Grocery & Food Markets')"
    )
    merchant_city = models.CharField(
        max_length=255,
        db_index=True,
        help_text="City where the merchant is located"
    )
    
    # Transaction details
    transaction_type = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Type of transaction (e.g., 'POS', 'Online', etc.)"
    )
    transaction_amount_kzt = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Transaction amount in Kazakhstani Tenge (KZT)"
    )
    original_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Original amount in original currency (if different from KZT)"
    )
    transaction_currency = models.CharField(
        max_length=3,
        help_text="Currency code of the transaction (ISO 4217)"
    )
    acquirer_country_iso = models.CharField(
        max_length=3,
        db_index=True,
        help_text="ISO country code of the acquirer"
    )
    
    # Payment method details
    pos_entry_mode = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Point of Sale entry mode (e.g., 'Contactless', 'Chip', etc.)"
    )
    wallet_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
        help_text="Digital wallet type (e.g., 'Apple Pay', 'Google Pay', etc.)"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this record was created in the database"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when this record was last updated"
    )
    
    class Meta:
        db_table = 'mcp_transactions'
        ordering = ['-transaction_timestamp']
        indexes = [
            models.Index(fields=['transaction_timestamp', 'card_id']),
            models.Index(fields=['merchant_id', 'transaction_timestamp']),
            models.Index(fields=['issuer_bank_name', 'transaction_timestamp']),
            models.Index(fields=['mcc_category', 'transaction_timestamp']),
        ]
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.transaction_amount_kzt} KZT"
    
    @property
    def formatted_amount(self):
        """Returns formatted transaction amount with currency."""
        return f"{self.transaction_amount_kzt:,.2f} KZT"
