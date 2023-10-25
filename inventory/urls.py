from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory_item_list, name='inventory_item_list'),
    path('<int:item_id>/', views.inventory_item_detail, name='inventory_item_detail'),
    path('edit/<int:item_id>/', views.edit_inventory_item, name='edit_inventory_item'),
    path('reserved_inventory/', views.reserved_inventory_items, name='reserved_inventory'),
    path('all_reserved_inventory/', views.all_reserved_inventory_items, name='all_reserved_inventory'),
    path('end_reservation/<int:reservation_id>/', views.end_reservation, name='end_reservation'),

]
