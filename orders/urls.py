from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('waiting/<int:order_id>/', views.waiting, name='waiting'),
    path('kaspi-qr/<int:order_id>/', views.kaspi_qr, name='kaspi_qr'),
    path('success/<str:order_number>/', views.success, name='success'),
    path('check-status/<int:order_id>/', views.check_status, name='check_status'),
    path('check-kaspi-status/<int:order_id>/', views.check_kaspi_status, name='check_kaspi_status'),
    path('saved-cards/', views.get_saved_cards, name='saved_cards'),
] 