from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Flight, Passenger, Booking
from django.db.models import Sum
from .forms import BookingForm, CustomUserCreationForm
from .forms import ContactForm



def home(request):
    """Home page with the hotel template"""
    return render(request, "base_template/index.html")


def about(request):
    """About page"""
    return render(request, "base_template/about.html")


def room(request):
    """Apartments/Rooms page"""
    return render(request, "base_template/room.html")


def amenities(request):
    """Amenities page"""
    return render(request, "base_template/amenities.html")


def booking_page(request):
    """Booking page (hotel template)"""
    return render(request, "base_template/booking.html")


def contact(request):
    """Contact page"""
    return render(request, "base_template/contact.html")


def flight_list(request):
    """Flight list page - your existing functionality"""
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
    """Flight detail page - your existing functionality"""
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



from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm
from .models import ContactSubmission

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save to database
            contact_submission = form.save()
            
            # You can also send email here if needed
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Send email functionality (optional)
            # send_contact_email(name, email, subject, message)
            
            messages.success(request, f'Thank you {name}! Your message has been sent successfully. We will get back to you within 2 hours.')
            return redirect('contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    return render(request, 'base_template/contact.html', {'form': form})

def contact_success(request):
    return render(request, 'contact_success.html')