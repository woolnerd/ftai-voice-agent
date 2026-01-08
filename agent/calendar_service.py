"""Google Calendar integration for appointment booking."""

import os
from datetime import datetime, timedelta
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Google Calendar API scopes
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar",
]


class CalendarService:
    """Service for interacting with Google Calendar API."""

    def __init__(self):
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID")
        self.credentials_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials.json")
        # For domain-wide delegation, impersonate this user
        self.delegate_user = os.getenv("GOOGLE_DELEGATE_USER", self.calendar_id)
        self._service = None

    @property
    def service(self):
        """Lazy-load the Google Calendar service with domain-wide delegation."""
        if self._service is None:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file, scopes=SCOPES
            )
            # Use domain-wide delegation to impersonate the user
            if self.delegate_user:
                credentials = credentials.with_subject(self.delegate_user)
                print(f"[CALENDAR] Using domain-wide delegation as: {self.delegate_user}")
            self._service = build("calendar", "v3", credentials=credentials)
        return self._service

    def get_available_slots(
        self,
        date: datetime,
        slot_duration_minutes: int = 60,
        start_hour: int = 9,
        end_hour: int = 18,
    ) -> list[str]:
        """
        Get available appointment slots for a given date.

        Args:
            date: The date to check availability for
            slot_duration_minutes: Length of each appointment slot
            start_hour: Business hours start (24h format)
            end_hour: Business hours end (24h format)

        Returns:
            List of available time slots as formatted strings (e.g., "10:00 AM")
        """
        # Set up time range for the day
        time_min = date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        time_max = date.replace(hour=end_hour, minute=0, second=0, microsecond=0)

        try:
            # Query free/busy information
            body = {
                "timeMin": time_min.isoformat() + "Z",
                "timeMax": time_max.isoformat() + "Z",
                "items": [{"id": self.calendar_id}],
            }
            result = self.service.freebusy().query(body=body).execute()
            busy_periods = result.get("calendars", {}).get(self.calendar_id, {}).get("busy", [])

            # Convert busy periods to datetime objects
            busy_times = []
            for period in busy_periods:
                start = datetime.fromisoformat(period["start"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(period["end"].replace("Z", "+00:00"))
                busy_times.append((start.replace(tzinfo=None), end.replace(tzinfo=None)))

            # Generate all possible slots
            available_slots = []
            current_slot = time_min
            while current_slot + timedelta(minutes=slot_duration_minutes) <= time_max:
                slot_end = current_slot + timedelta(minutes=slot_duration_minutes)

                # Check if this slot overlaps with any busy period
                is_available = True
                for busy_start, busy_end in busy_times:
                    if not (slot_end <= busy_start or current_slot >= busy_end):
                        is_available = False
                        break

                if is_available:
                    available_slots.append(current_slot.strftime("%-I:%M %p"))

                # Move to next slot (30-minute increments for flexibility)
                current_slot += timedelta(minutes=30)

            return available_slots

        except HttpError as e:
            print(f"[CALENDAR] Error querying availability: {e}")
            return []

    def create_appointment(
        self,
        customer_name: str,
        customer_email: str,
        service_type: str,
        start_time: datetime,
        duration_minutes: int = 60,
        notes: Optional[str] = None,
    ) -> Optional[dict]:
        """
        Create a calendar event for an appointment.

        Args:
            customer_name: Name of the customer
            customer_email: Customer's email (will receive calendar invite)
            service_type: Type of service being booked
            start_time: Appointment start time
            duration_minutes: Length of appointment
            notes: Optional notes for the appointment

        Returns:
            Created event details or None if failed
        """
        end_time = start_time + timedelta(minutes=duration_minutes)

        event = {
            "summary": f"{service_type} - {customer_name}",
            "description": f"Service: {service_type}\nClient: {customer_name}\nEmail: {customer_email}"
            + (f"\nNotes: {notes}" if notes else ""),
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "America/Los_Angeles",
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "America/Los_Angeles",
            },
            "attendees": [
                {"email": customer_email},
            ],
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},  # 1 day before
                    {"method": "email", "minutes": 60},  # 1 hour before
                ],
            },
        }

        try:
            created_event = (
                self.service.events()
                .insert(calendarId=self.calendar_id, body=event, sendUpdates="all")
                .execute()
            )
            print(f"[CALENDAR] Event created: {created_event.get('htmlLink')}")
            return {
                "id": created_event.get("id"),
                "link": created_event.get("htmlLink"),
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
            }
        except HttpError as e:
            print(f"[CALENDAR] Error creating event: {e}")
            return None


# Singleton instance
calendar_service = CalendarService()
