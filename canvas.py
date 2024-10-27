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

course_id = os.getenv("COURSE_ID")

# Define different API endpoints and filenames
endpoints = {
    "courses": f"{canvas_url}/courses",
    "assignments": f"{canvas_url}/courses/{course_id}/assignments",
    "files": f"{canvas_url}/courses/{course_id}/files"
}

# Headers for authorization
headers = {
    "Authorization": f"Bearer {access_token}"
}

# Loop over each endpoint, request data, and save to JSON
for name, url in endpoints.items():
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        # Save response JSON to a file named after the endpoint
        os.makedirs("personal", exist_ok=True)  # Create the directory if it doesn't exist
        with open(f"personal/{name}.json", "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"{name.capitalize()} JSON data saved to personal/{name}.json")
    else:
        print(f"Failed to retrieve {name} data:", response.status_code)
