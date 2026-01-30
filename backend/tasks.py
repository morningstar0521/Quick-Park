from __future__ import absolute_import
from datetime import datetime, timedelta
from pytz import timezone
from sqlalchemy import func
from flask_mail import Message
from jinja2 import Template
from models import User, Booking, ParkingLot
from celery import shared_task
from extensions import db, mail
from flask import Flask, current_app
import os
import io
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
except ImportError:
    pass

@shared_task
def notify_new_parking_lot(lot_id):
    with current_app.app_context():
        try:
            lot = ParkingLot.query.get(lot_id)
            if not lot:
                print(f"Parking lot {lot_id} not found")
                return f"Parking lot {lot_id} not found"
            
            users = User.query.all()

            template_path = os.path.join(os.path.dirname(__file__), 'templates', 'new_parking_lot.html')
            with open(template_path, 'r') as f:
                template_content = f.read()
            template = Template(template_content)

            for user in users:
                msg = Message(
                    subject=f"New Parking Lot Available - {lot.name}",
                    recipients=[user.email],
                    sender="noreply@quickpark.com"
                )
                msg.html = template.render(
                    user_name=user.full_name,
                    lot_name=lot.name,
                    lot_location=f"{lot.address}, {lot.city}",
                    total_spots=lot.total_spots,
                    rate_per_hour=lot.rate_per_hour,
                    description=f"Parking Type: {lot.parking_type}"
                )
                mail.send(msg)
                print(f"New parking lot notification sent to {user.email}")

            return f"Sent notifications to {len(users)} users about new parking lot {lot.name}"
        except Exception as e:
            print(f"Error sending new parking lot notifications: {e}")
            return f"Error: {e}"

@shared_task
def send_evening_reminders():
    with current_app.app_context():
        try:
            ist = timezone('Asia/Kolkata')
            tomorrow = (datetime.now(ist) + timedelta(days=1)).date()

            users_with_bookings = db.session.query(User.id).join(Booking).filter(
                func.date(Booking.start_time) == tomorrow
            ).distinct()

            users_without_bookings = User.query.filter(
                User.id.notin_(users_with_bookings)
            ).all()

            template_path = os.path.join(os.path.dirname(__file__), 'templates', 'reminder_email.html')
            with open(template_path, 'r') as f:
                template_content = f.read()
            template = Template(template_content)

            for user in users_without_bookings:
                msg = Message(
                    subject="Don't Get Left Behind! Book Your Parking Spot!",
                    recipients=[user.email],
                    sender="noreply@quickpark.com"
                )
                msg.html = template.render(user_name=user.full_name)
                mail.send(msg)
                print(f"Sent reminder to {user.email}")

            return f"Sent reminders to {len(users_without_bookings)} users."
        except Exception as e:
            print(f"Error sending evening reminders: {e}")
            return f"Error: {e}"
@shared_task
def send_receipt_email_task(booking_id):

    booking = Booking.query.get(booking_id)
    if not booking:
        print(f"Booking {booking_id} not found")
        return f"Booking {booking_id} not found"
    
    user = User.query.get(booking.user_id)
    lot = ParkingLot.query.get(booking.lot_id)
    
    if not user or not lot:
        print(f"User or lot not found for booking {booking_id}")
        return f"User or lot not found for booking {booking_id}"
        
    if booking.end_time is None:
        print(f"Booking {booking_id} has not ended yet, cannot send receipt")
        return f"Booking {booking_id} has not ended yet, cannot send receipt"
    
    ist = timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    
    start_time = booking.start_time
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone('Asia/Kolkata'))
    end_time = booking.end_time
    if end_time is not None and end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone('Asia/Kolkata'))
    duration_seconds = (end_time - start_time).total_seconds()
    duration_hours = duration_seconds / 3600
    duration_minutes = duration_seconds / 60
    hours_charged = max(1, round(duration_hours))
    
    pdf_data = generate_pdf_receipt(booking, user, lot, duration_hours, duration_minutes, hours_charged)
    
    msg = Message(
        subject=f"Your Parking Receipt - {lot.name}",
        recipients=[user.email],
        sender="noreply@quickpark.com"
    )
    
    msg.attach(
        filename=f"parking_receipt_{booking.id}.pdf",
        content_type="application/pdf",
        data=pdf_data
    )
    
    msg.html = render_receipt_template(booking, user, lot, duration_hours, duration_minutes, hours_charged)
    
    try:
        from flask import current_app
        with current_app.app_context():
            mail.send(msg)
            print(f"Receipt email sent to {user.email} for booking {booking_id}")
            return f"Receipt email sent to {user.email} for booking {booking_id}"
    except Exception as e:
        print(f"Failed to send receipt email: {str(e)}")
        return f"Failed to send receipt email: {str(e)}"

def generate_pdf_receipt(booking, user, lot, duration_hours, duration_minutes, hours_charged):
    buffer = io.BytesIO()
    
    try:
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        title = Paragraph(f"<b>Parking Receipt - {lot.name}</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph(f"<b>Booking ID:</b> {booking.id}", styles['Normal']))
        elements.append(Paragraph(f"<b>Vehicle Number:</b> {booking.vehicle_number}", styles['Normal']))
        elements.append(Paragraph(f"<b>Start Time:</b> {booking.start_time.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Paragraph(f"<b>End Time:</b> {booking.end_time.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Duration:</b> {round(duration_hours, 2)} hours ({round(duration_minutes, 2)} minutes)", styles['Normal']))
        elements.append(Paragraph(f"<b>Hours Charged:</b> {hours_charged}", styles['Normal']))
        elements.append(Paragraph(f"<b>Rate per Hour:</b> ₹{lot.rate_per_hour:.2f}", styles['Normal']))
        elements.append(Paragraph(f"<b>Amount Paid:</b> ₹{booking.amount_paid:.2f}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph("<i>Thank you for using our parking service!</i>", styles['Normal']))
        
        doc.build(elements)
        
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    except Exception as e:
        print(f"Failed to generate PDF: {str(e)}")
        buffer.close()
        return None

def render_receipt_template(booking, user, lot, duration_hours, duration_minutes, hours_charged):
    try:
        with open(os.path.join('templates', 'receipt_email.html'), 'r') as f:
            template_content = f.read()
            
        template = Template(template_content)
        return template.render(
            booking=booking,
            user=user,
            lot=lot,
            duration_hours=round(duration_hours, 2),
            duration_minutes=round(duration_minutes, 2),
            hours_charged=hours_charged
        )
    except Exception as e:
        print(f"Failed to render email template: {str(e)}")
        
        return f"""
        <html>
            <body>
                <h1>Parking Receipt - {lot.name}</h1>
                <p><b>Booking ID:</b> {booking.id}</p>
                <p><b>Vehicle Number:</b> {booking.vehicle_number}</p>
                <p><b>Start Time:</b> {booking.start_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><b>End Time:</b> {booking.end_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><b>Duration:</b> {round(duration_hours, 2)} hours ({round(duration_minutes, 2)} minutes)</p>
                <p><b>Hours Charged:</b> {hours_charged}</p>
                <p><b>Rate per Hour:</b> ₹{lot.rate_per_hour:.2f}</p>
        <p><b>Amount Paid:</b> ₹{booking.amount_paid:.2f}</p>
                <p><i>Thank you for using our parking service!</i></p>
            </body>
        </html>
        """

def generate_html_report(data):
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'monthly_report.html')
    
    with open(template_path, 'r') as file:
        template_content = file.read()

    template = Template(template_content)
    return template.render(**data)


@shared_task
def send_monthly_reports():
    with current_app.app_context():
        try:
            
            ist = timezone('Asia/Kolkata')
            current_time = datetime.now(ist)
            
            users = User.query.all()
            
            print(f"Found {len(users)} users to send reports to")
            
            for user in users:
                send_monthly_report.delay(user.id)
            
            return f"Started sending monthly reports to {len(users)} users"
        except Exception as e:
            print(f"Error in send_monthly_reports: {str(e)}")
            return f"Error in send_monthly_reports: {str(e)}"

@shared_task
def send_monthly_report(user_id):
    with current_app.app_context():
        try:
            user = User.query.get(user_id)
            if not user:
                print(f"User {user_id} not found")
                return f"User {user_id} not found"

            ist = timezone('Asia/Kolkata')
            current_time = datetime.now(ist)
            
            # Get the date range for the last month
            # end_date = current_time.replace(day=1) - timedelta(days=1)
            # start_date = end_date.replace(day=1)
            start_date = current_time.replace(day=1)
            end_date = current_time

            bookings = Booking.query.filter(
                Booking.user_id == user_id,
                Booking.end_time.between(start_date, end_date)
            ).all()

            if not bookings:
                print(f"No bookings found for user {user_id} in the last month")
                return f"No bookings found for user {user_id} in the last month"

            total_bookings = len(bookings)
            total_spent = sum(booking.amount_paid or 0 for booking in bookings)
            total_hours = sum(
                ((booking.end_time - booking.start_time).total_seconds() / 3600)
                for booking in bookings if booking.end_time
            )
            unique_spots = set()
            unique_lots = set()
            for booking in bookings:
                if booking.spot_id:
                    unique_spots.add(booking.spot_id)
                if booking.lot_id:
                    unique_lots.add(booking.lot_id)
            
            total_spots = len(unique_spots) if unique_spots else len(unique_lots)
            if total_spots == 0:
                total_spots = total_bookings

            lot_usage = {}
            for booking in bookings:
                try:
                    if booking.parking_lot:
                        lot_name = booking.parking_lot.name
                    else:
                        lot_name = "Unknown"
                    lot_usage[lot_name] = lot_usage.get(lot_name, 0) + 1
                except Exception as e:
                    print(f"Error getting lot name for booking {booking.id}: {str(e)}")
                    lot_usage["Unknown"] = lot_usage.get("Unknown", 0) + 1
            
            if lot_usage:
                most_used_lot = sorted(lot_usage.items(), key=lambda x: x[1], reverse=True)[0][0]
            else:
                most_used_lot = "N/A"

            report_data = {
                "user_name": user.full_name,
                "month": start_date.strftime("%B %Y"),
                "total_bookings": total_bookings,
                "total_spots": total_spots,
                "most_used_lot": most_used_lot,
                "total_spent": total_spent,
                "total_hours": round(total_hours, 2),
                "bookings": bookings
            }

            html_report = generate_html_report(report_data)

            msg = Message(
                subject=f"Your Monthly Parking Report - {start_date.strftime('%B %Y')}",
                recipients=[user.email],
                sender="noreply@quickpark.com"
            )
            msg.html = html_report

            mail.send(msg)
            print(f"Monthly report sent to {user.email}")
            return f"Monthly report sent to {user.email}"

        except Exception as e:
            print(f"Error sending monthly report to user {user_id}: {str(e)}")
            return f"Error sending monthly report to user {user_id}: {str(e)}"