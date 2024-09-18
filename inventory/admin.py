from django.contrib import admin
from django.http import HttpResponse
from .models import InventoryItem, ReservationHistory
from .utils import create_pdf_equally_spaced
import pandas as pd
import io
from django.db.models import Q
from django.contrib.admin import DateFieldListFilter
from django.shortcuts import render, redirect
from django.urls import path
from .forms import ChangeProductTypeForm
from django.contrib import messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
import csv
from constants import UNCATEGORIZED, CATEGORY_CHOICES
from django.contrib.admin.views.decorators import staff_member_required
from .forms import CSVUploadForm
import csv
from constants import CHOICE_FIELDS

from django.utils import timezone
from .models import Reservation, Profile

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('MAKE', 'PART_NUMBER', 'PRODUCT_NAME', 'SERIAL', 'PRODUCT_TYPE', 'NOTE', 'SHELF', 'PRINTED', 'DATE_CREATED')
    search_fields = ('MAKE', 'PART_NUMBER', 'PRODUCT_NAME', 'DESCRIPTION', 'SERIAL', 'NOTE', 'SHELF', 'PRODUCT_TYPE')
    list_filter = (
        ('DATE_CREATED', DateFieldListFilter),  # Date range filter
        'PRINTED',
        'PRODUCT_TYPE',
        # You can add more specific field filters here
    )

    actions = ['generate_pdf_for_selected_items', 'change_product_type', 'download_selected_as_csv', 'mark_as_printed', 'mark_as_not_printed']

    def mark_as_printed(self, request, queryset):
        count = queryset.update(PRINTED=True)
        if count == 1:
            message_bit = "1 inventory item was"
        else:
            message_bit = f"{count} inventory items were"
        self.message_user(request, f"{message_bit} marked as printed.")

    mark_as_printed.short_description = "Mark selected items as Printed"

    def mark_as_not_printed(self, request, queryset):
        count = queryset.update(PRINTED=False)
        if count == 1:
            message_bit = "1 inventory item was"
        else:
            message_bit = f"{count} inventory items were"
        self.message_user(request, f"{message_bit} marked as not printed.")

    mark_as_not_printed.short_description = "Mark selected items as not Printed"

    def download_selected_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}_selected_records.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    download_selected_as_csv.short_description = "Download selected items as CSV"

    def generate_pdf_for_selected_items(self, request, queryset):
        # Convert queryset to pandas DataFrame
        data = pd.DataFrame.from_records(queryset.values('id', 'MAKE', 'PART_NUMBER', 'PRODUCT_NAME', "DESCRIPTION", 'SERIAL', 'NOTE', 'SHELF'))

        # Call your utility function to generate the PDF
        pdf_buffer = create_pdf_equally_spaced(data)

        # Set up the HTTP response with the PDF file
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="selected_avidex_loaner_inventory_labels.pdf"'
        queryset.update(PRINTED=True)
        self.message_user(request, f"Generated PDF successfully. Check your browsers Downloads for the PDF file.")

        return response

    generate_pdf_for_selected_items.short_description = "Generate PDF for selected items (will mark these as printed)"


    def change_product_type(self, request, queryset):
        """Custom action to change the PRODUCT_TYPE of selected InventoryItem instances."""
        if 'apply' in request.POST:
            form = ChangeProductTypeForm(request.POST)
            if form.is_valid():
                new_product_type = form.cleaned_data['new_product_type']
                count = queryset.count()
                queryset.update(PRODUCT_TYPE=new_product_type)
                self.message_user(request, f"Successfully changed product type for {count} items.")
                return redirect(request.get_full_path())
        else:
            form = ChangeProductTypeForm(initial={'_selected_action': request.POST.getlist(ACTION_CHECKBOX_NAME)})

        return render(request, 'admin/change_product_type.html', {'items': queryset, 'form': form, 'action_checkbox_name': ACTION_CHECKBOX_NAME})

    change_product_type.short_description = "Change PRODUCT TYPE for selected items"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('change-product-type/', self.admin_site.admin_view(self.change_product_type), name='change-product-type'),
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv), name='upload-csv'),

        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            form = CSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES['csv_file']
                self.import_csv(file)
                self.message_user(request, "CSV file has been imported successfully")
                return redirect("..")
        else:
            form = CSVUploadForm()
        return render(request, "admin/csv_form.html", {'form': form})

    def import_csv(self, file):
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        for row in reader:
            # Check if 'QTY' is missing or blank in the row, or if the entire row is blank
            if not row.get('QTY') or all(value.strip() == '' for value in row.values()):
                continue  # Skip this row and move to the next one

            # Assuming 'QTY' needs to be an integer. This tries to convert 'QTY' to int and skips the row if it fails
            try:
                qty = int(row.get('QTY', 0))
            except ValueError:
                continue  # Skip rows where 'QTY' cannot be converted to an integer

            # Now, proceed to create or update the item only if the row passed the checks
            InventoryItem.objects.get_or_create(
                QTY=qty,
                MAKE=row.get('MAKE', '').strip(),
                PART_NUMBER=row.get('PART NUMBER', '').strip(),
                PRODUCT_NAME=row.get('PRODUCT NAME', '').strip(),
                DESCRIPTION=row.get('DESCRIPTION', '').strip(),
                SERIAL=row.get('SERIAL', '').strip(),
                NOTE=row.get('NOTE', '').strip(),
                SHELF=row.get('SHELF', '').strip(),
                PRODUCT_TYPE=row.get('PRODUCT TYPE', '').strip(),
                # Ensure to strip() all string fields to remove leading/trailing whitespaces
            )

    def get_search_results(self, request, queryset, search_term):
        """
        This method is overridden to add custom search logic that could combine search terms with OR logic across multiple fields.
        It's recommended to use this for more complex searches that `search_fields` can't handle.
        """
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            custom_query = Q(MAKE__icontains=search_term) | \
                           Q(PART_NUMBER__icontains=search_term) | \
                           Q(PRODUCT_NAME__icontains=search_term) | \
                           Q(DESCRIPTION__icontains=search_term) | \
                           Q(SERIAL__icontains=search_term) | \
                           Q(NOTE__icontains=search_term) | \
                           Q(SHELF__icontains=search_term) | \
                           Q(PRODUCT_TYPE__icontains=search_term)
            queryset |= self.model.objects.filter(custom_query)
        return queryset, use_distinct


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('client', 'inventory_item', 'profile', 'reserved_on', 'WO', 'active')
    list_filter = ('active', 'reserved_on', 'client')
    search_fields = ('client', 'WO', 'profile__user__username', 'inventory_item__name')
    date_hierarchy = 'reserved_on'
    actions = ['make_inactive', 'make_active']

    @admin.action(description='Mark selected reservations as inactive')
    def make_inactive(self, request, queryset):
        queryset.update(active=False)

    @admin.action(description='Mark selected reservations as active')
    def make_active(self, request, queryset):
        queryset.update(active=True)


@admin.register(ReservationHistory)
class ReservationHistoryAdmin(admin.ModelAdmin):
    list_display = ("reservation", "start_time", "end_time", "work_order")

    def work_order(self, obj):
        return obj.reservation.WO if obj.reservation else ""
    work_order.short_description = "Work Order"