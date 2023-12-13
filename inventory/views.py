
# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator
from django.shortcuts import render
# inventory/views.py
from .tables import InventoryItemTable
from django_tables2 import RequestConfig
from django.db.models import Q

from django.shortcuts import render, get_object_or_404, redirect
from .forms import ReservationForm, InventoryItemForm
from .models import InventoryItem, Reservation

from constants import CATEGORY_CHOICES
from .models import Reservation

def all_reserved_inventory_items(request):

    # Query the Reservation model to get active reservations for the current user
    active_reservations = Reservation.objects.filter(active=True)

    # Pass the active reservations to the template
    return render(request, 'all_reserved_items.html', {'active_reservations': active_reservations})


def reserved_inventory_items(request):
    # Get the currently logged-in user
    current_user = request.user

    # Query the Reservation model to get active reservations for the current user
    active_reservations = Reservation.objects.filter(profile__user=current_user, active=True)

    # Pass the active reservations to the template
    return render(request, 'reserved_items.html', {'active_reservations': active_reservations})

def end_reservation_redirect_all(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Check if the reservation belongs to the currently logged-in user (security check)
    if reservation.profile.user == request.user:
        reservation.profile = None  # Remove the user from the reservation
        reservation.active = False
        reservation.save()

    return redirect('all_reserved_inventory')


def end_reservation_of_item(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)
    active_reservation = Reservation.objects.filter(inventory_item=item, active=True).first()

    if active_reservation and active_reservation.profile.user == request.user:
        # Check if the reservation belongs to the currently logged-in user (security check)
        active_reservation.active = False
        active_reservation.save()

    return redirect('inventory_item_detail', item_id=item.id)

def end_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Check if the reservation belongs to the currently logged-in user (security check)
    if reservation.profile.user == request.user:
        reservation.profile = None  # Remove the user from the reservation
        reservation.active = False
        reservation.save()

    return redirect('reserved_inventory')

def inventory_item_detail(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)
    active_reservation = Reservation.objects.filter(inventory_item=item, active=True).first()

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.profile = request.user.profile
            reservation.inventory_item = item
            reservation.save()
            return redirect('inventory_item_list')  # Redirect as needed
    else:
        form = ReservationForm()
    context = {
        'item': item,
        'active_reservation': active_reservation,
        'form': form
    }
    return render(request, 'inventory_item_detail.html', context)

def edit_inventory_item(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)

    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            # Redirect to the details page (or wherever you'd like) after saving
            return redirect('inventory_item_detail', item_id=item.id)
    else:
        form = InventoryItemForm(instance=item)

    context = {
        'item': item,
        'edit_form': form
    }
    return render(request, 'inventory_item_edit.html', context)

def inventory_item_list(request):
    queries = {
        'QTY': request.GET.get('qty_search', ''),
        'MAKE': request.GET.get('make_search', ''),
        'PART_NUMBER': request.GET.get('part_number_search', ''),
        'PRODUCT_NAME': request.GET.get('product_name_search', ''),
        'SERIAL': request.GET.get('serial_search', ''),
        'DESCRIPTION': request.GET.get('description_search', ''),
        'SHELF': request.GET.get('shelf_search', ''),
        'PRODUCT_TYPE': request.GET.get('product_type_search', ''),

    }

    query_filter = Q()

    if queries['QTY']:
        query_filter &= Q(QTY=queries['QTY'])  # Assumes exact match for integer field
    if queries['MAKE']:
        query_filter &= Q(MAKE__icontains=queries['MAKE'])
    if queries['PART_NUMBER']:
        query_filter &= Q(PART_NUMBER__icontains=queries['PART_NUMBER'])
    if queries['PRODUCT_NAME']:
        query_filter &= Q(PRODUCT_NAME__icontains=queries['PRODUCT_NAME'])
    if queries['SERIAL']:
        query_filter &= Q(SERIAL__icontains=queries['SERIAL'])
    if queries['DESCRIPTION']:
        query_filter &= Q(DESCRIPTION__icontains=queries['DESCRIPTION'])
    if queries['SHELF']:
        query_filter &= Q(SHELF__icontains=queries['SHELF'])
    if queries['PRODUCT_TYPE']:
        query_filter &= Q(PRODUCT_TYPE__icontains=queries['PRODUCT_TYPE'])

    items = InventoryItem.objects.filter(query_filter)

    table = InventoryItemTable(items)
    RequestConfig(request, paginate={"per_page": 10}).configure(table)

    return render(request, 'inventory_item_list.html', {'table': table, 'CATEGORY_CHOICES': CATEGORY_CHOICES,**queries})
