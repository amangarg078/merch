import os
import json
import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db.models import Sum # Import Sum for aggregation
from skus.models import SKU, Note, SKUDailyMetric


class Command(BaseCommand):
    """
    Django management command to load mock SKU, SKUDailyMetric data,
    and create user groups and sample users into the database.
    SKU data is loaded from a JSON file.
    """
    help = 'Loads mock SKU, SKUDailyMetric data, and creates user groups and sample users into the database from a JSON file.'
    json_file_path = 'dummy_sku.json'  # Name of the JSON file containing SKU data
    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.SUCCESS('Creating user groups...'))
        brand_user_group, created = Group.objects.get_or_create(name='brand_user')
        if created:
            self.stdout.write(self.style.SUCCESS('Created group: brand_user'))
        merch_ops_group, created = Group.objects.get_or_create(name='merch_ops')
        if created:
            self.stdout.write(self.style.SUCCESS('Created group: merch_ops'))

        self.stdout.write(self.style.SUCCESS('Creating sample users...'))
        brand_user, created = User.objects.get_or_create(username='branduser1', email='brand1@example.com')
        if created:
            brand_user.set_password('password123')
            brand_user.save()
            brand_user_group.user_set.add(brand_user)
            self.stdout.write(self.style.SUCCESS('Created brand_user1 and added to brand_user group.'))
        else:
            self.stdout.write(self.style.WARNING('branduser1 already exists.'))

        merch_ops_user, created = User.objects.get_or_create(username='merchops1', email='merch1@example.com')
        if created:
            merch_ops_user.set_password('password123')
            merch_ops_user.save()
            merch_ops_group.user_set.add(merch_ops_user)
            self.stdout.write(self.style.SUCCESS('Created merchops1 and added to merch_ops group.'))
        else:
            self.stdout.write(self.style.WARNING('merchops1 already exists.'))

        self.stdout.write(self.style.SUCCESS('Loading SKU data from JSON file...'))

        if not os.path.exists(self.json_file_path):
            self.stdout.write(self.style.ERROR(f"Error: JSON file not found at {self.json_file_path}"))
            return

        try:
            with open(self.json_file_path, 'r') as f:
                skus_data_from_json = json.load(f)
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f"Error: Could not decode JSON from {self.json_file_path}. Check file format."))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An unexpected error occurred while reading the JSON file: {e}"))
            return

        # --- Bulk Create SKUs ---
        skus_to_create = []
        for data in skus_data_from_json:
            skus_to_create.append(
                SKU(
                    sku_id=data['sku_id'],
                    name=data.get('name', 'N/A'),
                    sales=data.get('sales', 0), # Initial sales, will be updated by daily metrics sum
                    return_percentage=data.get('return_percentage', 0.0),
                    content_score=data.get('content_score', 0.0)
                )
            )
        SKU.objects.bulk_create(skus_to_create)
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(skus_to_create)} SKUs in bulk.'))

        # Fetch created SKUs to get their IDs for related objects
        sku_map = {sku.sku_id: sku for sku in SKU.objects.all()}

        # --- Bulk Create SKUDailyMetrics ---
        daily_metrics_to_create = []
        today = date.today()
        for sku_data_item in skus_data_from_json:
            sku_obj = sku_map.get(sku_data_item['sku_id'])
            if sku_obj:
                sku_total_sales = sku_data_item.get('sales', 0)
                if sku_total_sales > 0:
                    average_daily_sales = sku_total_sales / 365
                    for i in range(365):
                        current_date = today - timedelta(days=i)
                        daily_sales_units = max(0, round(average_daily_sales + random.uniform(-average_daily_sales * 0.5, average_daily_sales * 0.5)))
                        daily_metrics_to_create.append(
                            SKUDailyMetric(sku=sku_obj, date=current_date, sales_units=daily_sales_units)
                        )
                else:
                    self.stdout.write(self.style.WARNING(f'  - SKU {sku_obj.name} has 0 total sales, no daily metrics generated.'))
            else:
                self.stdout.write(self.style.ERROR(f"  - Could not find SKU object for sku_id: {sku_data_item['sku_id']}"))

        SKUDailyMetric.objects.bulk_create(daily_metrics_to_create)
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(daily_metrics_to_create)} daily metrics in bulk.'))

        # --- Bulk Create Notes ---
        notes_to_create = []
        for sku_obj in sku_map.values():
            num_notes = random.randint(0, 3)
            for _ in range(num_notes):
                note_text = random.choice([
                    "Customer feedback indicates strong satisfaction.",
                    "Consider reviewing product images for better conversion.",
                    "High return rate, investigate common issues.",
                    "Marketing campaign for this SKU is performing well.",
                    "Competitor analysis suggests price adjustment might be needed.",
                    "Content score is low, needs optimization.",
                    "Positive reviews are increasing, good sign.",
                    "Check inventory levels, sales are spiking."
                ])
                notes_to_create.append(Note(sku=sku_obj, text=note_text))

        Note.objects.bulk_create(notes_to_create)
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(notes_to_create)} notes in bulk.'))

        self.stdout.write(self.style.SUCCESS('Mock data loading complete.'))