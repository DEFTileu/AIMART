from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('auth/', views.auth_view, name='auth'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    # path('profile/edit/', views.edit_profile, name='edit_profile'),
]