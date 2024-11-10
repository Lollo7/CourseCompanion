import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Replace with your actual Canvas instance domain and API endpoint
canvas_url = "https://canvas.instructure.com/api/v1"
access_token = os.getenv("CANVAS_ACCESS_TOKEN")

# Headers for authorization
headers = {
    "Authorization": f"Bearer {access_token}"
}

# List of course IDs (replace with your actual list of course IDs)
course_ids = [
    17700000000698456,  # Example course ID, replace with actual ones
    # Add more course IDs as needed
]

def fetch_files(course_id):
    """Fetch all files for a given course ID."""
    url = f"{canvas_url}/courses/{course_id}/files"
    all_files = []
    
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            all_files.extend(data)  # Collect all files across pages
            
            # Check for 'next' link in the headers for pagination
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                url = None  # No more pages
        else:
            print(f"Failed to retrieve files for course {course_id}: {response.status_code}")
            break
    
    return all_files

def download_file(file_info, download_dir):
    """Download a file given its URL and save it locally."""
    file_url = file_info['url']
    file_name = file_info['filename']
    
    # Make sure the download directory exists
    os.makedirs(download_dir, exist_ok=True)
    
    # Full path where the file will be saved
    file_path = os.path.join(download_dir, file_name)
    
    # Download the file and save it locally
    response = requests.get(file_url)
    
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {file_name} to {file_path}")
        return file_path
    else:
        print(f"Failed to download {file_name}: {response.status_code}")
        return None

# Fetch and download files for each course in the list
downloaded_files = []

for course_id in course_ids:
    print(f"Fetching files for course ID: {course_id}")
    files = fetch_files(course_id)
    
    # Download each file and store its local path
    for file_info in files:
        downloaded_file_path = download_file(file_info, f"personal/course_{course_id}_files")
        if downloaded_file_path:
            downloaded_files.append(downloaded_file_path)

# Save metadata about downloaded files to a JSON file (optional)
with open("personal/downloaded_files.json", "w") as json_file:
    json.dump(downloaded_files, json_file, indent=4)

print("All files have been downloaded.")