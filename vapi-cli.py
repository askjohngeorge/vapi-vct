import click
import os
import json
import requests
import sys


def load_config(config_file):
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        click.echo(f"Error: Configuration file '{config_file}' not found.", err=True)
        sys.exit(1)
    except json.JSONDecodeError:
        click.echo(
            f"Error: Invalid JSON in configuration file '{config_file}'.", err=True
        )
        sys.exit(1)


def get_api_key(config):
    api_key = config.get("api_key")
    if not api_key:
        click.echo("Error: API key not found in configuration file.", err=True)
        sys.exit(1)
    return api_key


def get_assistant_ids(config):
    assistant_ids = config.get("assistant_ids", [])
    if not assistant_ids:
        click.echo("Warning: No assistant IDs found in configuration file.", err=True)
    return assistant_ids


# Fetching
def fetch_assistant_and_save(assistant_ids, api_key):
    filenames = []
    for assistant_id in assistant_ids:
        # API endpoint
        url = f"https://api.vapi.ai/assistant/{assistant_id}"

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
    with open(
        os.path.join(directory, "assistant-config.json"), "w", encoding="utf-8"
    ) as f:
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
    config_path = os.path.join(directory, "assistant-config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"assistant-config.json not found in {directory}")

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


def update_assistant(assistant_id, assistant_data, api_key):
    url = f"https://api.vapi.ai/assistant/{assistant_id}"
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


def update_assistants_from_files(json_files, api_key):
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

            update_assistant(assistant_id, assistant_data, api_key)


# CLI
@click.group()
def cli():
    """Vapi Version Control Tools CLI"""
    pass


@cli.command()
@click.option("--config", default="vapi-config.json", help="Configuration file")
@click.option(
    "--no-decompose", is_flag=True, help="Skip decomposing fetched assistants"
)
def fetch(config: str, no_decompose: bool):
    """Fetch Vapi assistants and decompose them (unless --no-decompose is specified)"""
    config_data = load_config(config)
    api_key = get_api_key(config_data)
    assistant_ids = get_assistant_ids(config_data)

    if not assistant_ids:
        click.echo("No assistants to fetch. Exiting.", err=True)
        return

    fetched_files = fetch_assistant_and_save(assistant_ids, api_key)

    if not no_decompose:
        for file in fetched_files:
            decompose_assistant(file)
            click.echo(f"Decomposed {file}")


@cli.command()
@click.option("--config", default="vapi-config.json", help="Configuration file")
@click.option(
    "--no-recompose", is_flag=True, help="Skip recomposing assistants before updating"
)
def update(config: str, no_recompose: bool):
    """Update Vapi assistants, recomposing them first (unless --no-recompose is specified)"""
    config_data = load_config(config)
    api_key = get_api_key(config_data)
    assistant_ids = get_assistant_ids(config_data)

    if not assistant_ids:
        click.echo("No assistants to update. Exiting.", err=True)
        return

    files = [f"assistant_{assistant_id}.json" for assistant_id in assistant_ids]

    if not no_recompose:
        recomposed_files = []
        for assistant_id in assistant_ids:
            directory = assistant_id
            if os.path.isdir(directory):
                output_file = recompose_assistant(directory)
                recomposed_files.append(output_file)
            else:
                click.echo(f"Skipping {directory} as it's not a directory")
        files = recomposed_files

    update_assistants_from_files(files, api_key)


if __name__ == "__main__":
    cli()
