from django.contrib import admin
from .models import Airport, Flight, Passenger, Booking


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("code", "city", "country")
    search_fields = ("code", "city", "country")


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("number", "origin", "destination", "departure_time", "arrival_time", "price", "seats")
    list_filter = ("origin", "destination")
    search_fields = ("number",)


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ("name", "email")
    search_fields = ("name", "email")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "flight", "passenger", "user", "seats", "booked_at")
    list_filter = ("flight", "user")
