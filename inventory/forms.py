from django import forms
from .models import Reservation, InventoryItem
import constants

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()

class ChangeProductTypeForm(forms.Form):
    new_product_type = forms.ChoiceField(choices=constants.CATEGORY_CHOICES, required=True, label="New Product Type")

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['WO', 'client']  # Include the 'client' field in the form
        widgets = {
            'WO': forms.TextInput(attrs={'class': 'form-control'}),
            'client': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_WO(self):
        WO = self.cleaned_data.get('WO')
        if not WO:
            raise forms.ValidationError("Work Order is required.")
        return WO

from constants import CATEGORY_CHOICES
class InventoryItemForm(forms.ModelForm):
    PRODUCT_TYPE = forms.ChoiceField(choices=CATEGORY_CHOICES, required=True, label="Product Type")

    class Meta:
        model = InventoryItem
        fields = [
            'QTY',
            'MAKE',
            'PART_NUMBER',
            'PRODUCT_NAME',
            'SERIAL',
            'NOTE',
            'SHELF',
            'PRODUCT_TYPE',
            'DESCRIPTION',

        ]

        widgets = {
            'QTY': forms.NumberInput(attrs={'class': 'form-control'}),
            'MAKE': forms.TextInput(attrs={'class': 'form-control'}),
            'PART_NUMBER': forms.TextInput(attrs={'class': 'form-control'}),
            'PRODUCT_NAME': forms.TextInput(attrs={'class': 'form-control'}),
            'DESCRIPTION': forms.TextInput(attrs={'class': 'form-control'}),
            'SERIAL': forms.TextInput(attrs={'class': 'form-control'}),
            'NOTE': forms.TextInput(attrs={'class': 'form-control'}),
            'SHELF': forms.TextInput(attrs={'class': 'form-control'}),
            'PRODUCT_TYPE': forms.Select(attrs={'class':'regDropDown'})

        }
