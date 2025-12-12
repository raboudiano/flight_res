
# reservations/utils/invoices.py
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

def generate_invoice_pdf(ctx: dict) -> bytes:
    """
    ctx keys:
      booking_id, passenger_name, passenger_email,
      flight_number, origin_code, destination_code,
      departure_time, arrival_time,
      unit_price, seats, total, currency,
      company_name, company_address, support_email
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    x = 20 * mm
    y = height - 25 * mm

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, f"{ctx.get('company_name', 'Company')} — Invoice")
    y -= 10 * mm

    c.setFont("Helvetica", 10)
    c.drawString(x, y, f"Invoice #: {ctx.get('booking_id')}")
    y -= 6 * mm
    c.drawString(x, y, f"Passenger: {ctx.get('passenger_name')} ({ctx.get('passenger_email')})")
    y -= 10 * mm

    # Flight
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Flight Details")
    y -= 7 * mm

    c.setFont("Helvetica", 10)
    c.drawString(x, y, f"Flight: {ctx.get('flight_number')}")
    y -= 6 * mm
    c.drawString(x, y, f"{ctx.get('origin_code')} → {ctx.get('destination_code')}")
    y -= 6 * mm
    c.drawString(x, y, f"Departure: {ctx.get('departure_time')}")
    y -= 6 * mm
    c.drawString(x, y, f"Arrival: {ctx.get('arrival_time')}")
    y -= 10 * mm

    # Billing
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Billing")
    y -= 7 * mm

    currency = ctx.get("currency")
    unit_price = ctx.get("unit_price")
    seats = ctx.get("seats")
    total = ctx.get("total")

    c.setFont("Helvetica", 10)
    if unit_price is not None and currency:
        c.drawString(x, y, f"Unit price: {unit_price} {currency}"); y -= 6 * mm
    if seats is not None:
        c.drawString(x, y, f"Seats: {seats}"); y -= 6 * mm
    if total is not None and currency:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, f"Total: {total} {currency}"); y -= 10 * mm

    # Footer
    c.setFont("Helvetica", 9)
    c.drawString(x, 20 * mm, f"{ctx.get('company_name', '')} · {ctx.get('company_address', '')} · {ctx.get('support_email', '')}")

    c.showPage()
    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
