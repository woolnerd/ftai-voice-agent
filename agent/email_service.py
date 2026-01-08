"""Email service for sending appointment confirmations via Gmail SMTP."""

import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional


class EmailService:
    """Service for sending emails via Gmail SMTP."""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("GMAIL_USER")
        self.smtp_password = os.getenv("GMAIL_APP_PASSWORD")
        self.from_name = os.getenv("EMAIL_FROM_NAME", "Glow Medical Spa")

    @property
    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return bool(self.smtp_user and self.smtp_password)

    def send_confirmation_email(
        self,
        customer_name: str,
        customer_email: str,
        service_type: str,
        appointment_date: datetime,
        duration_minutes: int = 60,
        location: str = "2847 Riverside Drive, Suite 100",
        phone: str = "(555) 234-5678",
    ) -> bool:
        """
        Send an appointment confirmation email.

        Args:
            customer_name: Name of the customer
            customer_email: Customer's email address
            service_type: Type of service booked
            appointment_date: Date and time of appointment
            duration_minutes: Length of appointment
            location: Spa location address
            phone: Spa phone number

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.is_configured:
            print("[EMAIL] Email service not configured, skipping send")
            return False

        # Format the date/time nicely
        date_str = appointment_date.strftime("%A, %B %d, %Y")
        time_str = appointment_date.strftime("%-I:%M %p")
        end_time = appointment_date.replace(
            hour=appointment_date.hour + duration_minutes // 60,
            minute=appointment_date.minute + duration_minutes % 60,
        )
        end_time_str = end_time.strftime("%-I:%M %p")

        subject = f"Appointment Confirmed - {service_type} at {self.from_name}"

        # Create HTML email body
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .appointment-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .detail-row {{ display: flex; padding: 10px 0; border-bottom: 1px solid #eee; }}
        .detail-label {{ font-weight: bold; width: 120px; color: #666; }}
        .footer {{ text-align: center; padding: 20px; color: #888; font-size: 12px; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{self.from_name}</h1>
            <p>Appointment Confirmation</p>
        </div>
        <div class="content">
            <p>Hi {customer_name},</p>
            <p>Your appointment has been confirmed! Here are your booking details:</p>

            <div class="appointment-details">
                <div class="detail-row">
                    <span class="detail-label">Service:</span>
                    <span>{service_type}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Date:</span>
                    <span>{date_str}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Time:</span>
                    <span>{time_str} - {end_time_str}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Location:</span>
                    <span>{location}</span>
                </div>
            </div>

            <p><strong>What to expect:</strong></p>
            <ul>
                <li>Please arrive 10-15 minutes early to complete any paperwork</li>
                <li>Wear comfortable clothing</li>
                <li>Let us know if you have any questions beforehand</li>
            </ul>

            <p>Need to reschedule or cancel? Please call us at {phone} at least 24 hours in advance.</p>

            <p>We look forward to seeing you!</p>

            <p>Warm regards,<br>The {self.from_name} Team</p>
        </div>
        <div class="footer">
            <p>{self.from_name}<br>{location}<br>{phone}</p>
        </div>
    </div>
</body>
</html>
"""

        # Create plain text version
        text_body = f"""
Appointment Confirmation - {self.from_name}

Hi {customer_name},

Your appointment has been confirmed!

APPOINTMENT DETAILS:
- Service: {service_type}
- Date: {date_str}
- Time: {time_str} - {end_time_str}
- Location: {location}

WHAT TO EXPECT:
- Please arrive 10-15 minutes early to complete any paperwork
- Wear comfortable clothing
- Let us know if you have any questions beforehand

Need to reschedule or cancel? Please call us at {phone} at least 24 hours in advance.

We look forward to seeing you!

Warm regards,
The {self.from_name} Team

---
{self.from_name}
{location}
{phone}
"""

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.smtp_user}>"
            msg["To"] = customer_email

            # Attach both plain text and HTML versions
            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            print(f"[EMAIL] Confirmation sent to {customer_email}")
            return True

        except Exception as e:
            print(f"[EMAIL] Error sending email: {e}")
            return False


# Singleton instance
email_service = EmailService()
