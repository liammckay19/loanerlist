from django.contrib import admin
from .models import InventoryItem, ReservationHistory

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('MAKE', 'PART_NUMBER', 'PRODUCT_NAME', 'SERIAL', 'NOTE', 'SHELF')
    
@admin.register(ReservationHistory)
class ReservationHistoryAdmin(admin.ModelAdmin):
    list_display = ("reservation", "start_time", "end_time", "work_order")

    def work_order(self, obj):
        return obj.reservation.WO if obj.reservation else ""
    work_order.short_description = "Work Order"