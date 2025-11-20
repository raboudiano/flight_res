from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Flight, Passenger, Booking
from django.db.models import Sum
from .forms import BookingForm


def flight_list(request):
    flights = Flight.objects.filter(departure_time__gte=timezone.now())

    origin = request.GET.get("origin")
    destination = request.GET.get("destination")
    date = request.GET.get("date")

    if origin:
        flights = flights.filter(origin__code__iexact=origin)
    if destination:
        flights = flights.filter(destination__code__iexact=destination)
    if date:
        flights = flights.filter(departure_time__date=date)

    flights = flights.order_by("departure_time")
    return render(request, "reservations/flight_list.html", {
        "flights": flights,
        "origin": origin or "",
        "destination": destination or "",
        "date": date or "",
    })


def flight_detail(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    initial = None
    if request.user.is_authenticated:
        initial = {"name": getattr(request.user, "get_full_name", lambda: request.user.username)(), "email": request.user.email or ""}
    form = BookingForm(request.POST or None, initial=initial)

    if request.method == "POST" and not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.path}")

    if request.method == "POST" and form.is_valid():
        name = form.cleaned_data["name"]
        email = form.cleaned_data["email"]
        if request.user.is_authenticated:
            name = name or (getattr(request.user, "get_full_name", lambda: request.user.username)())
            email = email or request.user.email
        seats = form.cleaned_data["seats"]

        booked_seats = Booking.objects.filter(flight=flight).aggregate(total=Sum("seats")).get("total") or 0
        available = max(flight.seats - booked_seats, 0)

        if seats <= available:
            passenger, _ = Passenger.objects.get_or_create(email=email, defaults={"name": name})
            booking = Booking.objects.create(flight=flight, passenger=passenger, user=request.user if request.user.is_authenticated else None, seats=seats)
            return redirect(reverse("booking_success", args=[booking.id]))
        else:
            form.add_error("seats", f"Only {available} seat(s) remaining.")

    return render(request, "reservations/flight_detail.html", {"flight": flight, "form": form})


def booking_success(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, "reservations/booking_success.html", {"booking": booking})

from .forms import CustomUserCreationForm

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("flight_list")
    else:
        form = CustomUserCreationForm()

    return render(request, "reservations/register.html", {"form": form})
