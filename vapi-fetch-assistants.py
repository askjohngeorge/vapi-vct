import requests
import json
import os

def read_assistant_ids(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def fetch_assistant_and_save(assistant_ids):
    for assistant_id in assistant_ids:
        # API endpoint
        url = f"https://api.vapi.ai/assistant/{assistant_id}"

        # Get the private API key from an environment variable
        api_key = os.environ.get('VAPI_PRIVATE_API_KEY')
        if not api_key:
            raise ValueError("VAPI_PRIVATE_API_KEY environment variable is not set")

        # Headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        try:
            # Make the GET request
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Parse the JSON response
            assistant_data = response.json()

            # Save to a local JSON file
            filename = f"assistant_{assistant_id}.json"
            with open(filename, 'w') as f:
                json.dump(assistant_data, f, indent=2)

            print(f"Assistant data saved to {filename}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching assistant: {e}\nResponse details: {e.response.text}")

# Usage
assistant_ids_file = "assistants.txt"
assistant_ids = read_assistant_ids(assistant_ids_file)
fetch_assistant_and_save(assistant_ids)
