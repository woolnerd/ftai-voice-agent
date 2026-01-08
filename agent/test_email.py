"""Quick test script for email service."""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_service import email_service

def test_email():
    print("=" * 50)
    print("Testing Gmail Email Service")
    print("=" * 50)

    print(f"\nGmail User: {email_service.smtp_user}")
    print(f"Configured: {'Yes' if email_service.is_configured else 'No'}")

    if not email_service.is_configured:
        print("\n❌ Email not configured. Set GMAIL_USER and GMAIL_APP_PASSWORD in .env")
        return

    # Test sending email
    print("\n--- Sending test confirmation email ---")

    test_email_to = input(f"Send test email to (default: {email_service.smtp_user}): ").strip()
    if not test_email_to:
        test_email_to = email_service.smtp_user

    tomorrow = datetime.now() + timedelta(days=1)
    test_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)

    success = email_service.send_confirmation_email(
        customer_name="Test Customer",
        customer_email=test_email_to,
        service_type="HydraFacial",
        appointment_date=test_time,
        duration_minutes=45,
    )

    if success:
        print(f"✅ Email sent to {test_email_to}")
    else:
        print("❌ Failed to send email")

    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_email()
