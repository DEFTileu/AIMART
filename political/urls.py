# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_question, name='search_question'),
    path('ajax_search/', views.ajax_search, name='ajax_search'),
    path('add_question/', views.add_question, name='add_question'),
]
