# inventory/tables.py
from django_tables2 import tables, TemplateColumn, A
from django.urls import reverse
from .models import InventoryItem

class InventoryItemTable(tables.Table):
    table_options = {'clickable': True}

    # Define a custom column for the link
    link_column = TemplateColumn(
        template_name="link_column.html",  # Create a template for the link column
        verbose_name="LINK"  # Change this to whatever you want to display as the column header
    )

    class Meta:
        model = InventoryItem
        template_name = "django_tables2/bootstrap5.html"
        attrs = {"class": "table table-hover"}
        fields = ('QTY', 'MAKE', 'PART_NUMBER', 'PRODUCT_NAME', 'SERIAL', 'NOTE', 'SHELF')  # Include other fields as necessary.
        row_attrs = {
            'data-href': lambda record: record.get_absolute_url()
        }
