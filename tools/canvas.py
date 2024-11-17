import requests
import os
import json
from dotenv import load_dotenv
import tools.current_term as ct

load_dotenv()

# Replace with your actual Canvas instance domain and API endpoint
canvas_url = "https://umich.instructure.com/api/v1"
access_token = os.getenv("CANVAS_ACCESS_TOKEN")

# Example: GET request to list courses
headers = {
    "Authorization": f"Bearer {access_token}"
}

course_id = os.getenv("COURSE_ID")

def main():
    get_current_courses()
    with open("personal/current_courses.json", "r") as file:
        cc = json.load(file)
    for course in cc:
        print(course["name"].replace(" ", "_")) 
        get_assignments(course["id"], course["name"].replace(" ", "_"))
        get_files(course["id"], course["name"].replace(" ", "_"))
        print("finished downloading files for", course["name"])

def get_courses(): 
    all_courses = []
    url = f"{canvas_url}/courses"
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
            print(f"Failed to retrieve courses data:", response.status_code)
    return save_to_json("all_courses", all_courses)

def get_current_courses():
    # get courses and open the .json file
    courses = get_courses()
    with open(courses, "r") as file:
        courses = json.load(file)
    # filter out the current courses if course name contains ct.get_current_courses()
    current_courses = [course for course in courses if "name" in course and ct.return_current_term() in course["name"]]
    return save_to_json("current_courses", current_courses)

def get_assignments(course_id, course_name):
    url = f"{canvas_url}/courses/{course_id}/assignments"
    response = requests.get(url, headers=headers)
    return save_to_json("assignments", response.json(), course_name)

def get_folders(course_id, course_name):
    url = f"{canvas_url}/courses/{course_id}/folders"
    response = requests.get(url, headers=headers)
    save_to_json(f"folders", response.json(), course_name)
    return response.json()

def get_files(course_id, course_name):
    course_files = []
    list_folders = get_folders(course_id, course_name)
    url = f"{canvas_url}/courses/{course_id}/files"
    for folder in list_folders:
        folder_id = folder["id"]
        url = f"{canvas_url}/folders/{folder_id}/files"
        response = requests.get(url, headers=headers)
        course_files.extend(response.json())
    file = save_to_json(f"files", course_files, course_name)
    folder = "/".join(file.split("/")[:-1])

    # remove .json from folder name
    download_files(folder, file)
    return folder

def save_to_json(name, data, tree = None):
    if tree:
        tree = f"personal/{tree}"
    else:
        tree = "personal"
    os.makedirs(tree, exist_ok=True)  # Create the directory if it doesn't exist
    with open(f"{tree}/{name}.json", "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"{name.capitalize()} JSON data saved to personal/{name}.json")
    return f"{tree}/{name}.json"

def download_files(folder, json_file):
    # Create directory for the course
    folder = f"{folder}/files"
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Read JSON data
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Iterate over each file entry in the JSON data
    # Only keep file entries that end in .pdf
    data = [entry for entry in data if 'content-type' in entry and ("pdf" in entry['content-type'] or "docx" in entry['content-type'] or "doc" in entry['content-type'])]
    for entry in data:
        file_url = entry['url']
        file_name = entry['filename']
        file_path = os.path.join(folder, file_name)

        # Download the file
        response = requests.get(file_url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {file_name}")
        else:
            print(f"Failed to download: {file_name}")

if __name__ == "__main__":
    main()