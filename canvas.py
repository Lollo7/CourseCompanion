import requests
import os
import json
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta, timezone

# Load environment variables from a .env file
load_dotenv()

# Replace with your actual Canvas instance domain and API endpoint
canvas_url = "https://umich.instructure.com/api/v1"
access_token = os.getenv("CANVAS_ACCESS_TOKEN")

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Headers for authorization
headers = {
    "Authorization": f"Bearer {access_token}"
}

def authenticate_google_calendar():
    """Authenticate with Google Calendar API using OAuth 2.0."""
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future runs
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def get_today_events(service):
    """Retrieve events from today's calendar."""
    # Get current time in UTC using timezone-aware datetime
    now = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat()  # 'Z' indicates UTC time

    # Get the end of today at 23:59:59 UTC
    end_of_day = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59).isoformat()

    # print(f"Getting events from {now} to {end_of_day}")

    try:
        events_result = service.events().list(
            calendarId='primary', 
            timeMin=now, 
            timeMax=end_of_day,
            maxResults=10, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
    
        events = events_result.get('items', [])

        if not events:
            # print('No upcoming events found.')
            return []

        # print("Today's Events:")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            # print(f"{event['summary']} at {start}")
        
        return events
    
    except HttpError as error:
        # print(f"An error occurred: {error}")
        return []


def get_all_pages(url):
    all_data = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            all_data.extend(response.json())
            links = requests.utils.parse_header_links(response.headers.get('Link', ''))
            next_link = next((link['url'] for link in links if link['rel'] == 'next'), None)
            url = next_link
        else:
            # print(f"Failed to retrieve data: {response.status_code}")
            break
    return all_data

# Get all courses
courses_url = f"{canvas_url}/courses"
all_courses = get_all_pages(courses_url)

# Filter courses with "FA 2024" in the name
fa_2024_courses = [course for course in all_courses if 'name' in course and "FA 2024" in course['name']]

course_ids = [course['id'] for course in fa_2024_courses]
# print(f"Course IDs: {course_ids}")

# Save filtered courses to JSON file
os.makedirs("personal", exist_ok=True)
with open("personal/fa_2024_courses.json", "w") as json_file:
    json.dump(fa_2024_courses, json_file, indent=4)

# print(f"FA 2024 courses saved to personal/fa_2024_courses.json")

# Print the filtered courses
# print("\nCourses for Fall 2024:")
# for course in fa_2024_courses:
    # print(f"- {course['name']} (ID: {course['id']})")



creds = authenticate_google_calendar()
try:
    # Build the service object for interacting with Google Calendar API
    service = build('calendar', 'v3', credentials=creds)

    # Get today's events from Google Calendar
    today_events = get_today_events(service)

    # Print out retrieved events (or process them as needed)
    for event in today_events:
        print(json.dumps(event, indent=4))

except Exception as error:
    print(f"An error occurred: {error}")