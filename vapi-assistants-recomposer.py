import json
import os
import argparse


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


def process_directory(directory):
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


def main():
    parser = argparse.ArgumentParser(
        description="Recompose Vapi assistant JSON files from extracted components."
    )
    parser.add_argument(
        "directories",
        nargs="+",
        help="Path to one or more directories containing extracted assistant components",
    )
    args = parser.parse_args()

    for directory in args.directories:
        if not os.path.isdir(directory):
            print(f"Error: {directory} is not a valid directory.")
            continue
        try:
            process_directory(directory)
        except Exception as e:
            print(f"Error processing {directory}: {str(e)}")


if __name__ == "__main__":
    main()
