import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Replace with your actual Canvas instance domain and API endpoint
canvas_url = "https://umich.instructure.com/api/v1"
access_token = os.getenv("CANVAS_ACCESS_TOKEN")

# Example: GET request to list courses
headers = {
    "Authorization": f"Bearer {access_token}"
}

course_id = "705948"

courses = requests.get(f"{canvas_url}/courses", headers=headers)
assignments = requests.get(f"{canvas_url}/courses/{course_id}/files", headers=headers) 


# Check if request was successful
if courses.status_code == 200:
    courses = courses.json()
    # Save response JSON to a file
    with open("courses.json", "w") as json_file:
        json.dump(courses, json_file, indent=4)
    print("Courses JSON data saved to courses.json")
else:
    print("Failed to retrieve courses:", courses.status_code)

if assignments.status_code == 200:
    assignments = assignments.json()
    # Save response JSON to a file
    with open("assignments.json", "w") as json_file:
        json.dump(assignments, json_file, indent=4)
    print("Assignments JSON data saved to assignments.json")
else:
    print("Failed to retrieve assignments:", assignments.status_code)
