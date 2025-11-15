"""
Django management command to load transaction data from Parquet file into the database.

Usage:
    python manage.py load_transactions [--batch-size 10000] [--clear]
"""

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from mcp.models import Transaction
import os
from pathlib import Path
import pytz


class Command(BaseCommand):
    help = 'Load transaction data from Parquet file into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10000,
            help='Number of records to insert per batch (default: 10000)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing transactions before loading'
        )
        parser.add_argument(
            '--file',
            type=str,
            default='backend/mcp/dataset/example_dataset.parquet',
            help='Path to the Parquet file (relative to project root)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of records to load (for testing purposes)'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        clear = options['clear']
        file_path = options['file']
        limit = options['limit']

        # Resolve file path
        project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        parquet_file = project_root / file_path

        if not parquet_file.exists():
            raise CommandError(f'Parquet file not found: {parquet_file}')

        self.stdout.write(self.style.SUCCESS(f'Loading data from: {parquet_file}'))

        # Clear existing data if requested
        if clear:
            self.stdout.write(self.style.WARNING('Clearing existing transactions...'))
            count = Transaction.objects.count()
            Transaction.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {count} existing transactions'))

        # Load Parquet file
        self.stdout.write('Reading Parquet file...')
        try:
            df = pd.read_parquet(parquet_file)
            
            if limit:
                df = df.head(limit)
                self.stdout.write(self.style.WARNING(f'Limited to {limit} records for testing'))
            
            total_records = len(df)
            self.stdout.write(self.style.SUCCESS(f'Loaded {total_records:,} records from Parquet file'))
        except Exception as e:
            raise CommandError(f'Error reading Parquet file: {e}')

        # Process and insert data in batches
        self.stdout.write(f'Inserting records in batches of {batch_size:,}...')
        
        inserted_count = 0
        skipped_count = 0
        batch = []

        for idx, row in df.iterrows():
            try:
                # Convert timestamp to timezone-aware datetime
                ts = row['transaction_timestamp']
                if pd.notna(ts):
                    # Make timezone-aware using UTC
                    ts = timezone.make_aware(ts.to_pydatetime(), timezone=pytz.UTC) if ts.tzinfo is None else ts
                
                # Create Transaction object
                transaction_obj = Transaction(
                    transaction_id=str(row['transaction_id']),
                    transaction_timestamp=ts,
                    card_id=int(row['card_id']) if pd.notna(row['card_id']) else 0,
                    expiry_date=str(row['expiry_date']) if pd.notna(row['expiry_date']) else '',
                    issuer_bank_name=str(row['issuer_bank_name']) if pd.notna(row['issuer_bank_name']) else '',
                    merchant_id=int(row['merchant_id']) if pd.notna(row['merchant_id']) else 0,
                    merchant_mcc=int(row['merchant_mcc']) if pd.notna(row['merchant_mcc']) else 0,
                    mcc_category=str(row['mcc_category']) if pd.notna(row['mcc_category']) else '',
                    merchant_city=str(row['merchant_city']) if pd.notna(row['merchant_city']) else '',
                    transaction_type=str(row['transaction_type']) if pd.notna(row['transaction_type']) else '',
                    transaction_amount_kzt=float(row['transaction_amount_kzt']) if pd.notna(row['transaction_amount_kzt']) else 0.0,
                    original_amount=float(row['original_amount']) if pd.notna(row['original_amount']) else None,
                    transaction_currency=str(row['transaction_currency']) if pd.notna(row['transaction_currency']) else '',
                    acquirer_country_iso=str(row['acquirer_country_iso']) if pd.notna(row['acquirer_country_iso']) else '',
                    pos_entry_mode=str(row['pos_entry_mode']) if pd.notna(row['pos_entry_mode']) else '',
                    wallet_type=str(row['wallet_type']) if pd.notna(row['wallet_type']) else None,
                )
                batch.append(transaction_obj)
                
                # Insert batch when it reaches batch_size
                if len(batch) >= batch_size:
                    with transaction.atomic():
                        Transaction.objects.bulk_create(batch, ignore_conflicts=True)
                    inserted_count += len(batch)
                    batch = []
                    
                    # Progress indicator
                    progress = (inserted_count / total_records) * 100
                    self.stdout.write(
                        f'Progress: {inserted_count:,}/{total_records:,} ({progress:.1f}%)',
                        ending='\r'
                    )
                    self.stdout.flush()
                    
            except Exception as e:
                skipped_count += 1
                if skipped_count <= 10:  # Only show first 10 errors
                    self.stdout.write(self.style.ERROR(f'Error processing row {idx}: {e}'))

        # Insert remaining batch
        if batch:
            try:
                with transaction.atomic():
                    Transaction.objects.bulk_create(batch, ignore_conflicts=True)
                inserted_count += len(batch)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error inserting final batch: {e}'))

        # Final summary
        self.stdout.write('')  # New line after progress indicator
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'Data loading completed!'))
        self.stdout.write(self.style.SUCCESS(f'Total records in Parquet: {total_records:,}'))
        self.stdout.write(self.style.SUCCESS(f'Successfully inserted: {inserted_count:,}'))
        
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'Skipped (errors): {skipped_count:,}'))
        
        # Verify database count
        db_count = Transaction.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Total records in database: {db_count:,}'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

