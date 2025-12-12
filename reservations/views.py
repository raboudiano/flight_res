from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import login
from django.db.models import Sum
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login

from .models import Flight, Passenger, Booking, ContactSubmission
from .forms import BookingForm, CustomUserCreationForm, ContactForm

# Email services
from .services.emailing import send_booking_confirmation
from .services.contact_email import send_contact_email


def home(request):
    """Home page with the hotel template"""
    return render(request, "base_template/index.html")


def about(request):
    """About page"""
    return render(request, "base_template/about.html")


def booking_page(request):
    """Booking page (hotel template)"""
    return render(request, "base_template/booking.html")


def contact(request):
    """Contact page"""
    return render(request, "base_template/contact.html")


def flight_list(request):
    """Flight list page"""
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
    """
    Public flight detail page - ONLY shows flight information.
    No booking form here. Users must click "Book Now" button.
    """
    flight = get_object_or_404(Flight, pk=pk)
    
    # Calculate available seats
    booked_seats = Booking.objects.filter(flight=flight).aggregate(total=Sum("seats")).get("total") or 0
    available_seats = max(flight.seats - booked_seats, 0)
    
    return render(request, "reservations/flight_detail.html", {
        "flight": flight,
        "available_seats": available_seats
    })


def booking_success(request, pk):
    """Booking success page"""
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, "reservations/booking_success.html", {"booking": booking})


def register(request):
    """User registration"""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("flight_list")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})


def contact_view(request):
    """Contact submission view with optional email to support."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_submission = form.save()
            # Optional: send email to support with the message
            send_contact_email(
                form.cleaned_data['name'],
                form.cleaned_data['email'],
                form.cleaned_data['subject'],
                form.cleaned_data['message'],
            )
            messages.success(request, f"Thank you {form.cleaned_data['name']}! Your message has been sent successfully. We will get back to you within 2 hours.")
            return redirect('contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    return render(request, 'base_template/contact.html', {'form': form})


def contact_success(request):
    return render(request, 'contact_success.html')


@require_POST
@login_required(login_url='login')
def resend_booking_email(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.user and booking.user != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to resend this booking email.")
        return redirect('booking_success', pk=pk)
    send_booking_confirmation(booking)
    messages.success(request, f"Confirmation email resent to {booking.passenger.email}.")
    return redirect('booking_success', pk=pk)

@login_required(login_url='login')
def flight_book_page(request, pk):
    """
    Booking page - LOGIN REQUIRED.
    If not logged in → redirects automatically to /login/?next=...
    """
    flight = get_object_or_404(Flight, pk=pk)

    # Calculate available seats
    booked_seats = Booking.objects.filter(flight=flight).aggregate(total=Sum("seats")).get("total") or 0
    available_seats = max(flight.seats - booked_seats, 0)

    # Prefill user data
    initial = {
        "name": request.user.get_full_name() or request.user.username,
        "email": request.user.email or ""
    }

    form = BookingForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        name = form.cleaned_data.get("name") or initial["name"]
        email = form.cleaned_data.get("email") or initial["email"]
        seats = form.cleaned_data["seats"]

        # Recalculate seats (safety)
        booked_seats = Booking.objects.filter(flight=flight).aggregate(total=Sum("seats")).get("total") or 0
        remaining = max(flight.seats - booked_seats, 0)

        if seats <= remaining:
            with transaction.atomic():
                passenger, _ = Passenger.objects.get_or_create(
                    email=email, defaults={"name": name}
                )
                booking = Booking.objects.create(
                    flight=flight,
                    passenger=passenger,
                    user=request.user,
                    seats=seats
                )

                send_booking_confirmation(booking)

            messages.success(request, "Your booking has been confirmed!")
            return redirect(reverse("booking_success", args=[booking.id]))

        else:
            form.add_error("seats", f"Only {remaining} seat(s) remaining.")

    return render(request, "reservations/flight_book_page.html", {
        "flight": flight,
        "form": form,
        "available_seats": available_seats
    })