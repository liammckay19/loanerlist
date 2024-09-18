import csv
from django.core.management.base import BaseCommand
from ...models import InventoryItem  # Make sure to correct the import path
import constants

class Command(BaseCommand):
    help = 'Export data to a CSV file from the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='Path to the CSV file to export')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file_path']

        fieldnames = ['QTY', 'MAKE', 'PART NUMBER', 'PRODUCT NAME', 'DESCRIPTION', 'SERIAL', 'NOTE', 'SHELF', 'URL']

        with open(csv_file_path, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for item in InventoryItem.objects.all():
                writer.writerow({
                    'QTY': item.QTY,
                    'MAKE': item.MAKE,
                    'PART NUMBER': item.PART_NUMBER,
                    'PRODUCT NAME': item.PRODUCT_NAME,
                    'DESCRIPTION': item.DESCRIPTION,
                    'SERIAL': item.SERIAL,
                    'NOTE': item.NOTE,
                    'SHELF': item.SHELF,
                    'URL': constants.CURRENT_DOMAIN_NAME+f"/{item.id}/",
                })

        self.stdout.write(self.style.SUCCESS(f"Data exported successfully to {csv_file_path}"))
