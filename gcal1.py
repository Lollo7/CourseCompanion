import os
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

class GoogleCalendarManager:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.creds = None
        self.service = None

    def authenticate(self):
        """Handles authentication with Google Calendar API."""
        # Check if token.pickle exists
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        # If credentials are invalid or don't exist, get new ones
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('calendar', 'v3', credentials=self.creds)

    def create_calendar(self, calendar_name):
        """Creates a new calendar if it doesn't exist."""
        try:
            # Check if calendar already exists
            calendar_list = self.service.calendarList().list().execute()
            for calendar in calendar_list.get('items', []):
                if calendar['summary'] == calendar_name:
                    return calendar['id']

            # Create new calendar
            calendar_body = {
                'summary': calendar_name,
                'timeZone': 'UTC'
            }
            created_calendar = self.service.calendars().insert(body=calendar_body).execute()
            return created_calendar['id']

        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def create_event(self, calendar_id, event_name, start_time, end_time):
        """Creates a new event in the specified calendar."""
        try:
            event = {
                'summary': event_name,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }

            event = self.service.events().insert(calendarId=calendar_id, body=event).execute()
            return event

        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

def main():
    # Initialize the calendar manager
    calendar_manager = GoogleCalendarManager()
    calendar_manager.authenticate()

    # Create a new calendar (or get existing one)
    calendar_name = "My New Calendar"
    calendar_id = calendar_manager.create_calendar(calendar_name)

    if calendar_id:
        # Create event from 1:30 PM to 3:00 PM today
        today = datetime.now()
        start_time = today.replace(hour=13, minute=30, second=0, microsecond=0)
        end_time = today.replace(hour=15, minute=0, second=0, microsecond=0)

        event = calendar_manager.create_event(
            calendar_id,
            "Hello World",
            start_time,
            end_time
        )

        if event:
            print(f"Event created successfully: {event.get('htmlLink')}")
        else:
            print("Failed to create event")
    else:
        print("Failed to create/find calendar")

if __name__ == '__main__':
    main()