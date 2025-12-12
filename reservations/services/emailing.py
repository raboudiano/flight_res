
# reservations/services/emailing.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal
import logging

from reservations.utils.invoices import generate_invoice_pdf

logger = logging.getLogger(__name__)

def send_booking_confirmation(booking):
    """
    Sends booking confirmation (HTML + text) with a PDF invoice attachment.
    Uses Booking, Flight, Passenger models.
    """
    passenger = booking.passenger
    flight = booking.flight

    # Compute totals
    unit_price = flight.price or Decimal("0.00")
    seats = booking.seats or 1
    total = unit_price * seats
    currency = getattr(settings, "COMPANY_CURRENCY", "TND")

    # Company meta
    company_name = getattr(settings, "COMPANY_NAME", "SkyTunisia")
    company_address = getattr(settings, "COMPANY_ADDRESS", "")
    support_email = getattr(settings, "COMPANY_SUPPORT_EMAIL", "")
    support_phone = getattr(settings, "COMPANY_SUPPORT_PHONE", "")

    ctx = {
        "booking_id": booking.id,
        "passenger_name": passenger.name,
        "passenger_email": passenger.email,
        "flight_number": flight.number,
        "origin_code": flight.origin.code,
        "destination_code": flight.destination.code,
        "departure_time": flight.departure_time,
        "arrival_time": flight.arrival_time,
        "seats": seats,
        "booked_at": booking.booked_at,

        "unit_price": unit_price,
        "total": total,
        "currency": currency,

        "company_name": company_name,
        "company_address": company_address,
        "support_email": support_email,
        "support_phone": support_phone,
    }

    subject = f"Booking Confirmation — #{booking.id}"
    from_email = settings.DEFAULT_FROM_EMAIL or support_email or "no-reply@yourdomain.com"
    to = [passenger.email]

    # Render email bodies
    html_body = render_to_string("emails/booking_confirmation.html", ctx)
    text_body = (
        f"Booking Confirmed — #{booking.id}\n"
        f"Passenger: {passenger.name} ({passenger.email})\n"
        f"Flight: {flight.number} — {flight.origin.code} -> {flight.destination.code}\n"
        f"Departure: {flight.departure_time} | Arrival: {flight.arrival_time}\n"
        f"Seats: {seats}\n"
        f"Total: {total} {currency}\n"
        "Your invoice (PDF) is attached.\n"
        f"Support: {support_email} | {support_phone}\n"
    )

    msg = EmailMultiAlternatives(subject, text_body, from_email, to)
    msg.attach_alternative(html_body, "text/html")

    # Attach PDF
    pdf_bytes = generate_invoice_pdf(ctx)
    msg.attach(f"Invoice_{booking.id}.pdf", pdf_bytes, "application/pdf")

    # Send with basic error logging
    try:
        msg.send()
    except Exception as e:
        logger.exception("Failed to send booking confirmation for booking #%s: %s", booking.id, e)
