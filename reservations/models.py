from django.db import models
from django.db.models import Sum, F, Q
from django.conf import settings
from django.utils import timezone

class Airport(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.city}"


class Flight(models.Model):
    number = models.CharField(max_length=10)
    origin = models.ForeignKey(Airport, related_name='departures', on_delete=models.CASCADE)
    destination = models.ForeignKey(Airport, related_name='arrivals', on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seats = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.number}: {self.origin.code} → {self.destination.code}"

    @property
    def available_seats(self):
        booked = self.booking_set.aggregate(total=Sum("seats")).get("total") or 0
        return max(self.seats - booked, 0)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(arrival_time__gt=F("departure_time")),
                name="arrival_after_departure",
            ),
            models.CheckConstraint(
                check=Q(price__gte=0) & Q(seats__gte=0),
                name="non_negative_price_seats",
            ),
        ]

class Passenger(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Booking(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    seats = models.PositiveIntegerField(default=1)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking #{self.id} for {self.flight.number}"


# ADD THIS CONTACT MODEL
class ContactSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(default=timezone.now)
    is_resolved = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.submitted_at.date()})"