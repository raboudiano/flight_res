from django.urls import path

from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.flight_list, name='flight_list'),
    path('flight/<int:pk>/', views.flight_detail, name='flight_detail'),
    path('booking/<int:pk>/success/', views.booking_success, name='booking_success'),
    
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='flight_list'), name='logout'),
]