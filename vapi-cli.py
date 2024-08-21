import click
import os
import json
import requests
from typing import List


# Fetching
def read_assistant_ids(filename):
    with open(filename, "r") as file:
        return [line.strip() for line in file if line.strip()]


def fetch_assistant_and_save(assistant_ids):
    filenames = []
    for assistant_id in assistant_ids:
        # API endpoint
        url = f"https://api.vapi.ai/assistant/{assistant_id}"

        # Get the private API key from an environment variable
        api_key = os.environ.get("VAPI_PRIVATE_API_KEY")
        if not api_key:
            raise ValueError("VAPI_PRIVATE_API_KEY environment variable is not set")

        # Headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            # Make the GET request
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Parse the JSON response
            assistant_data = response.json()

            # Save to a local JSON file
            filename = f"assistant_{assistant_id}.json"
            with open(filename, "w") as f:
                json.dump(assistant_data, f, indent=2)

            print(f"Assistant data saved to {filename}")
            filenames.append(filename)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching assistant: {e}\nResponse details: {e.response.text}")
    return filenames


# Decomposition
def extract_and_save(content, filename, directory):
    if content is None:
        return None
    with open(os.path.join(directory, filename), "w", encoding="utf-8") as f:
        f.write(content)
    return f"file://{filename}"


def decompose_assistant(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assistant_id = data["id"]
    directory = assistant_id

    if not os.path.exists(directory):
        os.makedirs(directory)

    # Extract system prompt
    system_message = next(
        (msg for msg in data["model"]["messages"] if msg["role"] == "system"), None
    )
    if system_message:
        data["model"]["messages"][0]["content"] = extract_and_save(
            system_message["content"], "system-prompt.txt", directory
        )

    # Extract firstMessage
    if "firstMessage" in data:
        data["firstMessage"] = extract_and_save(
            data["firstMessage"], "first-message.txt", directory
        )

    # Extract analysisPlan components
    if "analysisPlan" in data:
        analysis_plan = data["analysisPlan"]

        if "summaryPrompt" in analysis_plan:
            analysis_plan["summaryPrompt"] = extract_and_save(
                analysis_plan["summaryPrompt"], "summary-prompt.txt", directory
            )

        if "structuredDataPrompt" in analysis_plan:
            analysis_plan["structuredDataPrompt"] = extract_and_save(
                analysis_plan["structuredDataPrompt"],
                "structured-data-prompt.txt",
                directory,
            )

        if "structuredDataSchema" in analysis_plan:
            schema_path = os.path.join(directory, "structured-data-schema.json")
            with open(schema_path, "w", encoding="utf-8") as f:
                json.dump(analysis_plan["structuredDataSchema"], f, indent=2)
            analysis_plan["structuredDataSchema"] = "file://structured-data-schema.json"

        if "successEvaluationPrompt" in analysis_plan:
            analysis_plan["successEvaluationPrompt"] = extract_and_save(
                analysis_plan["successEvaluationPrompt"],
                "success-evaluation-prompt.txt",
                directory,
            )

    # Save the modified JSON
    with open(os.path.join(directory, "config.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Extraction complete for {file_path}. Files saved in directory: {directory}")


# Recomposition
def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def resolve_file_path(file_reference, directory):
    if isinstance(file_reference, str) and file_reference.startswith("file://"):
        return os.path.join(directory, file_reference[7:])
    return file_reference


def read_file_if_exists(file_path):
    if os.path.exists(file_path):
        return read_file(file_path)
    return None


def recompose_assistant(directory):
    config_path = os.path.join(directory, "config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"config.json not found in {directory}")

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Recompose system prompt
    system_prompt_path = os.path.join(directory, "system-prompt.txt")
    if os.path.exists(system_prompt_path):
        system_message = next(
            (msg for msg in data["model"]["messages"] if msg["role"] == "system"), None
        )
        if system_message:
            system_message["content"] = read_file(system_prompt_path)
        else:
            data["model"]["messages"].insert(
                0, {"role": "system", "content": read_file(system_prompt_path)}
            )

    # Recompose firstMessage
    first_message_path = os.path.join(directory, "first-message.txt")
    if os.path.exists(first_message_path):
        data["firstMessage"] = read_file(first_message_path)

    # Recompose analysisPlan components
    if "analysisPlan" not in data:
        data["analysisPlan"] = {}
    analysis_plan = data["analysisPlan"]

    summary_prompt_path = os.path.join(directory, "summary-prompt.txt")
    if os.path.exists(summary_prompt_path):
        analysis_plan["summaryPrompt"] = read_file(summary_prompt_path)

    structured_data_prompt_path = os.path.join(directory, "structured-data-prompt.txt")
    if os.path.exists(structured_data_prompt_path):
        analysis_plan["structuredDataPrompt"] = read_file(structured_data_prompt_path)

    structured_data_schema_path = os.path.join(directory, "structured-data-schema.json")
    if os.path.exists(structured_data_schema_path):
        analysis_plan["structuredDataSchema"] = json.loads(
            read_file(structured_data_schema_path)
        )

    success_evaluation_prompt_path = os.path.join(
        directory, "success-evaluation-prompt.txt"
    )
    if os.path.exists(success_evaluation_prompt_path):
        analysis_plan["successEvaluationPrompt"] = read_file(
            success_evaluation_prompt_path
        )

    # Save the recomposed JSON
    directory_name = os.path.basename(os.path.normpath(directory))
    output_filename = f"assistant_{directory_name}.json"

    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Recomposition complete for {directory}. Output saved as: {output_filename}")
    return output_filename


# Updating
def load_assistant_data(filename):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            assistant_id = data.get("id")
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
    api_key = os.environ.get("VAPI_PRIVATE_API_KEY")
    if not api_key:
        raise ValueError("VAPI_PRIVATE_API_KEY environment variable is not set")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        response = requests.patch(url, headers=headers, json=assistant_data)
        response.raise_for_status()
        print(f"Assistant {assistant_id} updated successfully")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(
            f"Error updating assistant {assistant_id}: {e}\nResponse details: {e.response.text}"
        )
        return None


def update_assistants_from_files(json_files):
    for json_file in json_files:
        assistant_id, assistant_data = load_assistant_data(json_file)
        if assistant_id and assistant_data:
            # Remove properties that should not be included in the update
            keys_to_remove = [
                "id",
                "orgId",
                "createdAt",
                "updatedAt",
                "isServerUrlSecretSet",
            ]
            for key in keys_to_remove:
                assistant_data.pop(key, None)

            update_assistant(assistant_id, assistant_data)


# CLI
@click.group()
def cli():
    """Vapi Version Control Tools CLI"""
    pass


@cli.command()
@click.option(
    "--ids-file", default="assistants.txt", help="File containing assistant IDs"
)
@click.option("--decompose", is_flag=True, help="Decompose fetched assistants")
def fetch(ids_file: str, decompose: bool):
    """Fetch Vapi assistants and optionally decompose them"""
    assistant_ids = read_assistant_ids(ids_file)
    fetched_files = fetch_assistant_and_save(assistant_ids)

    if decompose:
        for file in fetched_files:
            decompose_assistant(file)
            click.echo(f"Decomposed {file}")


@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("--recompose", is_flag=True, help="Recompose assistants before updating")
def update(files: List[str], recompose: bool):
    """Update Vapi assistants, optionally recomposing them first"""
    if recompose:
        recomposed_files = []
        for file in files:
            if os.path.isdir(file):
                output_file = recompose_assistant(file)
                recomposed_files.append(output_file)
            else:
                click.echo(f"Skipping {file} as it's not a directory")
        files = recomposed_files

    update_assistants_from_files(files)


if __name__ == "__main__":
    cli()
