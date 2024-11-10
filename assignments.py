# assignments.py

import requests
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timezone
import canvas

# Get the current time in UTC
current_time = datetime.now(timezone.utc)
all_incomplete_assignments = []

# Convert to ISO 8601 format
iso_time = current_time.isoformat()

# Load environment variables
load_dotenv()

# Canvas API setup
CANVAS_API_URL = "https://umich.instructure.com/api/v1"
CANVAS_ACCESS_TOKEN = os.getenv("CANVAS_ACCESS_TOKEN")

def get_non_completed_assignments(course_id):
    url = f"{CANVAS_API_URL}/courses/{course_id}/assignments"
    headers = {"Authorization": f"Bearer {CANVAS_ACCESS_TOKEN}"}
    
    non_completed_assignments = []
    
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching assignments: {response.status_code}")
            return []
        
        assignments = response.json()
        for assignment in assignments:
            # if assignment['has_submitted_submissions'] == False:
            # if assignment['unlock_at'] is not None and assignment['unlock_at'] < iso_time and assignment['lock_at'] is not None and assignment['lock_at'] > iso_time:
            if assignment['locked_for_user'] == False:
                # if assignment['submission_types'] == ['online_upload']:
                if assignment['submission_types'] == ['online_quiz'] and assignment['is_quiz_assignment'] == True:
                    non_completed_assignments.append(assignment)
                else: 
                    if assignment['has_submitted_submissions'] == False:
                        if assignment['due_at'] is not None and assignment['due_at'] > iso_time:
                            non_completed_assignments.append(assignment)
        
        # Check for pagination
        url = response.links.get('next', {}).get('url')
    
    return non_completed_assignments

def main():
    # non_completed_assignments = get_non_completed_assignments(course_id)
    for course_id in canvas.course_ids: 
        all_incomplete_assignments.extend(get_non_completed_assignments(course_id))
    # print(json.dumps(all_incomplete_assignments, indent=4))
    # if non_completed_assignments:
        # print(f"Found {len(non_completed_assignments)} non-completed assignments.")

        # Save to JSON file
        # filename = f"non_completed_assignments_course_{course_id}.json"
        # with open(filename, 'w') as f:
        #     json.dump(non_completed_assignments, f, indent=2)
        
        # print(f"Non-completed assignments saved to {filename}")
    # else:
    #     print("No non-completed assignments found or error occurred.")

if __name__ == "__main__":
    main()