from django.contrib import admin
from django.urls import path,include

from .views import  news_list, news_detail, add_news, edit_news


urlpatterns = [
        path('', news_list, name='news_list'),
        path('add/', add_news, name='add_news'),
        path('edit/<slug:slug>/', edit_news, name='edit_news'),
        path('<slug:slug>/', news_detail, name='news_detail'),
        ]