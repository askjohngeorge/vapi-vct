#!/usr/bin/env python3

import click
import os
import json
import requests
import sys
import re


# Helpers
def load_config(config_file, project_specific=False):
    config = {}

    if not project_specific:
        default_config_path = os.path.expanduser("~/.vapi_vct/vapi_config.json")

        # Load default config if it exists
        if os.path.exists(default_config_path):
            with open(default_config_path, "r") as f:
                config = json.load(f)

    # Load and merge project-specific config
    try:
        with open(config_file, "r") as f:
            project_config = json.load(f)
            config.update(project_config)
    except FileNotFoundError:
        click.echo(
            f"Warning: Project configuration file '{config_file}' not found.{' Using default configuration.' if not project_specific else ''}",
            err=True,
        )
    except json.JSONDecodeError:
        click.echo(
            f"Error: Invalid JSON in configuration file '{config_file}'.", err=True
        )
        sys.exit(1)

    if "assistant_directories" not in config:
        config["assistant_directories"] = {}

    return config


def get_api_key(config):
    api_key = config.get("api_key")
    if not api_key:
        click.echo("Error: API key not found in configuration file.", err=True)
        raise SystemExit(1)
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
    return f"file:///{filename}"


def sanitize_folder_name(name):
    return re.sub(r"\s+", "_", name.lower())


def decompose_assistant(file_path, config_file):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assistant_id = data["id"]
    assistant_name = sanitize_folder_name(data.get("name", assistant_id))
    directory = assistant_name

    # Update the configuration with the new mapping
    config = load_config(config_file, project_specific=True)
    config["assistant_directories"][assistant_id] = directory
    update_config(config_file, config)

    if not os.path.exists(directory):
        os.makedirs(directory)

    # Extract secrets
    secrets = {
        key: data.pop(key)
        for key in ["id", "orgId", "createdAt", "updatedAt", "isServerUrlSecretSet"]
        if key in data
    }

    with open(os.path.join(directory, "secrets.json"), "w", encoding="utf-8") as f:
        json.dump(secrets, f, indent=2)

    # Extract system prompt
    system_message = next(
        (msg for msg in data["model"]["messages"] if msg["role"] == "system"), None
    )
    if system_message:
        data["model"]["messages"][0]["content"] = extract_and_save(
            system_message["content"], "system_prompt.txt", directory
        )

    # Extract firstMessage
    if "firstMessage" in data:
        data["firstMessage"] = extract_and_save(
            data["firstMessage"], "first_message.txt", directory
        )

    # Extract analysisPlan components
    if "analysisPlan" in data:
        analysis_plan = data["analysisPlan"]

        if "summaryPrompt" in analysis_plan:
            analysis_plan["summaryPrompt"] = extract_and_save(
                analysis_plan["summaryPrompt"], "summary_prompt.txt", directory
            )

        if "structuredDataPrompt" in analysis_plan:
            analysis_plan["structuredDataPrompt"] = extract_and_save(
                analysis_plan["structuredDataPrompt"],
                "structured_data_prompt.txt",
                directory,
            )

        if "structuredDataSchema" in analysis_plan:
            schema_path = os.path.join(directory, "structured_data_schema.json")
            with open(schema_path, "w", encoding="utf-8") as f:
                json.dump(analysis_plan["structuredDataSchema"], f, indent=2)
            analysis_plan["structuredDataSchema"] = (
                "file:///structured_data_schema.json"
            )

        if "successEvaluationPrompt" in analysis_plan:
            analysis_plan["successEvaluationPrompt"] = extract_and_save(
                analysis_plan["successEvaluationPrompt"],
                "success_evaluation_prompt.txt",
                directory,
            )

    # Save the modified JSON
    with open(
        os.path.join(directory, "assistant_config.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(data, f, indent=2)

    print(f"Extraction complete for {file_path}. Files saved in directory: {directory}")


# Recomposition
def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def resolve_file_path(file_reference, directory):
    if isinstance(file_reference, str) and file_reference.startswith("file:///"):
        return os.path.join(directory, file_reference[8:])
    return file_reference


def read_file_if_exists(file_path):
    if os.path.exists(file_path):
        return read_file(file_path)
    return None


def recompose_assistant(directory):
    config_path = os.path.join(directory, "assistant_config.json")
    secrets_path = os.path.join(directory, "secrets.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"assistant_config.json not found in {directory}")

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Reincorporate secrets
    if os.path.exists(secrets_path):
        with open(secrets_path, "r", encoding="utf-8") as f:
            secrets = json.load(f)
        data.update(secrets)

    # Recompose system prompt
    system_message = next(
        (msg for msg in data["model"]["messages"] if msg["role"] == "system"), None
    )
    if system_message:
        system_message["content"] = (
            read_file_if_exists(resolve_file_path(system_message["content"], directory))
            or system_message["content"]
        )

    # Recompose firstMessage
    if "firstMessage" in data:
        data["firstMessage"] = (
            read_file_if_exists(resolve_file_path(data["firstMessage"], directory))
            or data["firstMessage"]
        )

    # Recompose analysisPlan components
    if "analysisPlan" in data:
        analysis_plan = data["analysisPlan"]

        for key in ["summaryPrompt", "structuredDataPrompt", "successEvaluationPrompt"]:
            if key in analysis_plan:
                analysis_plan[key] = (
                    read_file_if_exists(
                        resolve_file_path(analysis_plan[key], directory)
                    )
                    or analysis_plan[key]
                )

        if "structuredDataSchema" in analysis_plan:
            schema_path = resolve_file_path(
                analysis_plan["structuredDataSchema"], directory
            )
            if os.path.exists(schema_path):
                with open(schema_path, "r", encoding="utf-8") as f:
                    analysis_plan["structuredDataSchema"] = json.load(f)

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
@click.group(name="vapi_vct")
def cli():
    """Vapi Version Control Tools CLI"""
    pass


@cli.group(name="config")
def config():
    """Configuration commands"""
    pass


@config.group(name="assistants")
def assistants():
    """Assistant commands"""
    pass


@config.group(name="api_key")
def api_key():
    """API key commands"""
    pass


@cli.command(name="fetch")
@click.option(
    "--config", default="vapi_config.json", help="Project-specific configuration file"
)
@click.option(
    "--no-decompose", is_flag=True, help="Skip decomposing fetched assistants"
)
def fetch(config: str, no_decompose: bool):
    """Fetch and optionally decompose Vapi assistants"""
    config_data = load_config(config)
    try:
        api_key = get_api_key(config_data)
    except SystemExit:
        raise click.Abort()

    assistant_ids = get_assistant_ids(config_data)

    if not assistant_ids:
        click.echo("No assistants to fetch. Exiting.", err=True)
        raise click.Abort()

    fetched_files = fetch_assistant_and_save(assistant_ids, api_key)

    if not no_decompose:
        for file in fetched_files:
            decompose_assistant(file, config)
            click.echo(f"Decomposed {file}")


@cli.command(name="update")
@click.option(
    "--config", default="vapi_config.json", help="Project-specific configuration file"
)
@click.option(
    "--no-recompose", is_flag=True, help="Skip recomposing assistants before updating"
)
def update(config: str, no_recompose: bool):
    """Update Vapi assistants, optionally recomposing first"""
    config_data = load_config(config)
    try:
        api_key = get_api_key(config_data)
    except SystemExit:
        raise click.Abort()
    assistant_ids = get_assistant_ids(config_data)
    assistant_directories = config_data.get("assistant_directories", {})

    if not assistant_ids:
        click.echo("No assistants to update. Exiting.", err=True)
        raise click.Abort()

    files = [f"assistant_{assistant_id}.json" for assistant_id in assistant_ids]

    if not no_recompose:
        recomposed_files = []
        for assistant_id in assistant_ids:
            directory = assistant_directories.get(assistant_id, assistant_id)
            if os.path.isdir(directory):
                output_file = recompose_assistant(directory)
                recomposed_files.append(output_file)
            else:
                click.echo(f"Skipping {directory} as it's not a directory")
        files = recomposed_files

    update_assistants_from_files(files, api_key)


def update_config(config_file, updated_config):
    with open(config_file, "w") as f:
        json.dump(updated_config, f, indent=2)


# Config commands
@assistants.command(name="add")
@click.argument("assistant_ids", nargs=-1, required=True)
@click.option(
    "--config", default="vapi_config.json", help="Project-specific configuration file"
)
def add_assistant(assistant_ids, config):
    """Add one or more assistant IDs to the configuration"""
    current_config = load_config(config, project_specific=True)
    current_assistants = set(current_config.get("assistant_ids", []))
    for assistant_id in assistant_ids:
        if assistant_id in current_assistants:
            click.echo(f"Assistant ID {assistant_id} already exists. Skipping.")
        else:
            current_assistants.add(assistant_id)
            click.echo(f"Added assistant ID {assistant_id}")
    current_config["assistant_ids"] = list(current_assistants)
    update_config(config, current_config)


@assistants.command(name="del")
@click.argument("assistant_ids", nargs=-1, required=True)
@click.option(
    "--config", default="vapi_config.json", help="Project-specific configuration file"
)
def del_assistant(assistant_ids, config):
    """Remove one or more assistant IDs from the configuration"""
    current_config = load_config(config, project_specific=True)
    current_assistants = set(current_config.get("assistant_ids", []))

    for assistant_id in assistant_ids:
        if assistant_id in current_assistants:
            current_assistants.remove(assistant_id)
            click.echo(f"Removed assistant ID {assistant_id}")
        else:
            click.echo(f"Assistant ID {assistant_id} not found. Skipping.")

    current_config["assistant_ids"] = list(current_assistants)
    update_config(config, current_config)


@assistants.command(name="list")
@click.option(
    "--config", default="vapi_config.json", help="Project-specific configuration file"
)
def list_assistants(config):
    """List all assistant IDs in the configuration"""
    current_config = load_config(config, project_specific=True)
    assistant_ids = current_config.get("assistant_ids", [])

    if assistant_ids:
        click.echo("Assistant IDs in the configuration:")
        for assistant_id in assistant_ids:
            click.echo(f"- {assistant_id}")
    else:
        click.echo("No assistant IDs found in the configuration.")


@api_key.command(name="add")
@click.argument("api_key")
@click.option(
    "--config", default="vapi_config.json", help="Project-specific configuration file"
)
def add_api_key(api_key, config):
    """Set an API key in the configuration"""
    current_config = load_config(config, project_specific=True)
    current_config["api_key"] = api_key
    update_config(config, current_config)
    click.echo("API key set successfully")


@api_key.command(name="del")
@click.option(
    "--config", default="vapi_config.json", help="Project-specific configuration file"
)
def del_api_key(config):
    """Clear the API key from the configuration"""
    current_config = load_config(config, project_specific=True)
    if "api_key" in current_config:
        del current_config["api_key"]
        update_config(config, current_config)
        click.echo("API key cleared successfully")
    else:
        click.echo("No API key found in the configuration")


if __name__ == "__main__":
    cli()
