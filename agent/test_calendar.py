"""Quick test script for calendar integration."""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calendar_service import calendar_service

def test_calendar():
    print("=" * 50)
    print("Testing Google Calendar Integration")
    print("=" * 50)

    # Check config
    print(f"\nCalendar ID: {calendar_service.calendar_id}")
    print(f"Delegate User: {calendar_service.delegate_user}")
    print(f"Credentials File: {calendar_service.credentials_file}")

    if not calendar_service.calendar_id:
        print("\n❌ GOOGLE_CALENDAR_ID not set in .env")
        return

    # Test 1: Check availability for tomorrow
    print("\n--- Test 1: Checking availability for tomorrow ---")
    tomorrow = datetime.now() + timedelta(days=1)

    # Skip to next open day if tomorrow is Sunday or Monday
    while tomorrow.weekday() in [6, 0]:
        tomorrow += timedelta(days=1)

    print(f"Checking: {tomorrow.strftime('%A, %B %d')}")

    try:
        slots = calendar_service.get_available_slots(tomorrow)
        if slots:
            print(f"✅ Available slots: {', '.join(slots[:5])}")
        else:
            print("⚠️  No available slots (calendar may be fully booked)")
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # Test 2: Create a test appointment (optional)
    print("\n--- Test 2: Create test appointment? ---")
    response = input("Create a test appointment? (y/n): ").strip().lower()

    if response == 'y':
        test_time = tomorrow.replace(hour=15, minute=0, second=0, microsecond=0)
        print(f"Creating appointment for {test_time.strftime('%A, %B %d at %-I:%M %p')}")

        result = calendar_service.create_appointment(
            customer_name="Test Customer",
            customer_email=calendar_service.calendar_id,  # Send to yourself
            service_type="Test Appointment",
            start_time=test_time,
            duration_minutes=30,
        )

        if result:
            print(f"✅ Appointment created!")
            print(f"   Link: {result.get('link')}")
        else:
            print("❌ Failed to create appointment")

    print("\n" + "=" * 50)
    print("Test complete!")

if __name__ == "__main__":
    test_calendar()
