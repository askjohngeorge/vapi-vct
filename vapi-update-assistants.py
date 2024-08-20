import requests
import json
import os
import argparse

def load_assistant_data(filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            assistant_id = data.get('id')
            if not assistant_id:
                print(f"Error: No 'id' field found in {filename}")
                return None, None
            return assistant_id, data
    except FileNotFoundError:
        print(f"File {filename} not found. Skipping this file.")
        return None, None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {filename}. Skipping this file.")
        return None, None

def update_assistant(assistant_id, assistant_data):
    url = f"https://api.vapi.ai/assistant/{assistant_id}"
    api_key = os.environ.get('VAPI_PRIVATE_API_KEY')
    if not api_key:
        raise ValueError("VAPI_PRIVATE_API_KEY environment variable is not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.patch(url, headers=headers, json=assistant_data)
        response.raise_for_status()
        print(f"Assistant {assistant_id} updated successfully")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error updating assistant {assistant_id}: {e}\nResponse details: {e.response.text}")
        return None

def update_assistants_from_files(json_files):
    for json_file in json_files:
        assistant_id, assistant_data = load_assistant_data(json_file)
        if assistant_id and assistant_data:
            # Remove properties that should not be included in the update
            keys_to_remove = ['id', 'orgId', 'createdAt', 'updatedAt', 'isServerUrlSecretSet']
            for key in keys_to_remove:
                assistant_data.pop(key, None)

            update_assistant(assistant_id, assistant_data)

def main():
    parser = argparse.ArgumentParser(description="Update VAPI assistants from JSON files.")
    parser.add_argument('json_files', nargs='+', help='One or more JSON files containing assistant data')
    args = parser.parse_args()

    update_assistants_from_files(args.json_files)

if __name__ == "__main__":
    main()