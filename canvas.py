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

# Load environment variables from a .env file
load_dotenv()

# Replace with your actual Canvas instance domain and API endpoint
canvas_url = "https://umich.instructure.com/api/v1"
access_token = os.getenv("CANVAS_ACCESS_TOKEN")

# SCOPES = ['https://www.googleapis.com/auth/calendar']
# creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# service = build('calendar', 'v3', credentials=creds)

# Headers for authorization
headers = {
    "Authorization": f"Bearer {access_token}"
}

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
            print(f"Failed to retrieve data: {response.status_code}")
            break
    return all_data

# Get all courses
courses_url = f"{canvas_url}/courses"
all_courses = get_all_pages(courses_url)

# Filter courses with "FA 2024" in the name
fa_2024_courses = [course for course in all_courses if 'name' in course and "FA 2024" in course['name']]


def create_calendar(calendar_name):
    calendar = {
        'summary': calendar_name,
        'timeZone': 'America/New_York'
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    return created_calendar['id']

def add_ics_to_calendar(ics_url, calendar_id):
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    event = {
        'source': {
            'url': ics_url,
        }
    }
    
    try:
        event = service.events().import_(calendarId=calendar_id, body=event).execute()
        print(f'Event created: {event.get("htmlLink")}')
    except HttpError as error:
        print(f'An error occurred: {error}')

# new_calendar_name = "Canvas Courses"
# new_calendar_id = create_calendar(new_calendar_name)
# print(f"Created new calendar: {new_calendar_name} (ID: {new_calendar_id})")

course_ids = [course['id'] for course in fa_2024_courses]
print(f"Course IDs: {course_ids}")
# for course in fa_2024_courses:
#     if 'calendar' in course and 'ics' in course['calendar']:
#         ics_url = course['calendar']['ics']
#         course_name = course.get('name', 'Unknown Course')
#         print(f"Adding events for course: {course_name}")
#         add_ics_to_calendar(ics_url, new_calendar_id)

# Save filtered courses to JSON file
os.makedirs("personal", exist_ok=True)
with open("personal/fa_2024_courses.json", "w") as json_file:
    json.dump(fa_2024_courses, json_file, indent=4)

print(f"FA 2024 courses saved to personal/fa_2024_courses.json")

# Print the filtered courses
print("\nCourses for Fall 2024:")
for course in fa_2024_courses:
    print(f"- {course['name']} (ID: {course['id']})")