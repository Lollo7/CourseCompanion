import requests
import os
import json
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from a .env file
load_dotenv()

def courses_to_csv(course_json):
    # Convert to DataFrame and write to CSV
    course_df = pd.DataFrame(course_json)
    course_df.to_csv("personal/courses.csv", index=False)
    print("Courses data saved to courses.csv")
    return True

# Replace with your actual Canvas instance domain and API endpoint
canvas_url = "https://umich.instructure.com/api/v1"
access_token = os.getenv("CANVAS_ACCESS_TOKEN")

# Headers for authorization
headers = {
    "Authorization": f"Bearer {access_token}"
}

name = "courses"
url = f"{canvas_url}/courses"

# Loop over each page of results, using pagination
all_courses = []
while url:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        all_courses.extend(data)  # Collect all courses across pages
        # Check for 'next' link in the headers for pagination
        if 'next' in response.links:
            url = response.links['next']['url']
        else:
            url = None  # No more pages
    else:
        print(f"Failed to retrieve {name} data:", response.status_code)
        break

# Save the accumulated data to JSON and CSV
os.makedirs("personal", exist_ok=True)  # Create the directory if it doesn't exist
with open(f"personal/{name}.json", "w") as json_file:
    json.dump(all_courses, json_file, indent=4)
print(f"{name.capitalize()} JSON data saved to personal/{name}.json")

if name == "courses":
    courses_to_csv(all_courses)
