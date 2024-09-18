from django.db import models
from django.urls import reverse
from accounts.models import Profile
from django.utils import timezone

class InventoryItem(models.Model):

    # Define the category choices:

    from constants import UNCATEGORIZED, CATEGORY_CHOICES
    QTY = models.IntegerField()
    MAKE = models.CharField(max_length=255)
    PART_NUMBER = models.CharField(max_length=255, blank=True)
    PRODUCT_NAME = models.CharField(max_length=255, blank=True)
    DESCRIPTION = models.CharField(max_length=1000, blank=True)
    SERIAL = models.CharField(max_length=255, blank=True)
    NOTE = models.CharField(max_length=255, blank=True)
    SHELF = models.CharField(max_length=255, blank=True)
    PRODUCT_TYPE = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default=UNCATEGORIZED)  # Add the category field

    PRINTED = models.BooleanField(default=False)  # Indicates if the item has been printed, default is False
    DATE_CREATED = models.DateTimeField(auto_now_add=True)  # Automatically set to the current date when the item is first created

    def __str__(self):
        s = f"{self.MAKE} {self.PART_NUMBER} {self.PRODUCT_NAME}"
        return s[:20]  # Display the MAKE field as the string representation


    def get_absolute_url(self):
        return reverse('inventory_item_detail', args=[str(self.id)])

    def get_reservation_status(self):
        # Check if there is at least one active reservation for this inventory item
        has_active_reservation = self.reservation_set.filter(active=True).exists()
        return has_active_reservation


class Reservation(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    reserved_on = models.DateTimeField(auto_now_add=True)
    WO = models.CharField(max_length=255, verbose_name="Work Order", blank=True)  # Work Order field
    active = models.BooleanField(default=True)
    client = models.CharField(max_length=255, verbose_name="Client", default='Not specified')  # Add the Client field
    notes = models.CharField(max_length=3000, verbose_name="Notes", default='Notes')  # Add the Client field

    def __str__(self):
        return f"Reservation of {self.inventory_item} for {self.client}"  # Include the client in the __str__ representation

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.active:
            # Reservation is ending, create a reservation history entry
            ReservationHistory.objects.create(
                reservation=self,
                start_time=self.reserved_on,
                end_time=timezone.now()  # Import timezone from django.utils
            )

class ReservationHistory(models.Model):
    reservation = models.ForeignKey('Reservation', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"Reservation History for {self.reservation}"

