from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Hotel Template Pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('apartments/', views.room, name='room'),
    path('amenities/', views.amenities, name='amenities'),
    path('hotel-booking/', views.booking_page, name='booking_page'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),

    # Flight Booking System
    path('flights/', views.flight_list, name='flight_list'),
    path('flight/<int:pk>/', views.flight_detail, name='flight_detail'),
    path('booking/<int:pk>/success/', views.booking_success, name='booking_success'),
]