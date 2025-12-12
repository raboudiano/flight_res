# reservations/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Hotel Template Pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('hotel-booking/', views.booking_page, name='booking_page'),

    # Contact
    path('contact/', views.contact_view, name='contact'),
    path('contact/success/', views.contact_success, name='contact_success'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
   
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('register/', views.register, name='register'),

    # Flight Booking System
    path('flights/', views.flight_list, name='flight_list'),
    path('flight/<int:pk>/', views.flight_detail, name='flight_detail'),  # Detail page (no login required)
    path('flight/<int:pk>/book/', views.flight_book_page, name='flight_book_page'),  # Booking page (login required)
    path('booking/<int:pk>/success/', views.booking_success, name='booking_success'),
    path('booking/<int:pk>/resend/', views.resend_booking_email, name='resend_booking_email'),

    
]