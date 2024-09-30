import csv
import argparse
from django.core.management.base import BaseCommand
from ...models import InventoryItem  # Import your model

class Command(BaseCommand):
    help = 'Import data from a CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='Path to the CSV file to import')
        parser.add_argument('--overwrite', action='store_true', help='Overwrite existing data')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file_path']
        overwrite = kwargs['overwrite']

        if overwrite:
            InventoryItem.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Deleted existing inventory items."))

        with open(csv_file_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                item, created = InventoryItem.objects.get_or_create(
                    QTY=row['QTY'],
                    MAKE=row['MAKE'],
                    PART_NUMBER=row['PART NUMBER'],
                    PRODUCT_NAME=row['PRODUCT NAME'],
                    DESCRIPTION=row['DESCRIPTION'],
                    SERIAL=row['SERIAL'],
                    NOTE=row['NOTE'],
                    SHELF=row['SHELF'],
                    PRODUCT_TYPE=row['PRODUCT TYPE']
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Imported new item: {item}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Skipped existing item: {item}"))
