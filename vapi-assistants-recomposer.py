import json
import os
import argparse


def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def process_directory(directory):
    config_path = os.path.join(directory, "config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"config.json not found in {directory}")

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Helper function to resolve file paths
    def resolve_file_path(file_reference):
        if file_reference.startswith("file://"):
            return os.path.join(directory, file_reference[7:])
        return file_reference

    # Recompose system prompt
    system_message = next(
        msg for msg in data["model"]["messages"] if msg["role"] == "system"
    )
    system_prompt_path = resolve_file_path(system_message["content"])
    system_message["content"] = read_file(system_prompt_path)

    # Recompose firstMessage
    first_message_path = resolve_file_path(data["firstMessage"])
    data["firstMessage"] = read_file(first_message_path)

    # Recompose summaryPrompt
    summary_prompt_path = resolve_file_path(data["analysisPlan"]["summaryPrompt"])
    data["analysisPlan"]["summaryPrompt"] = read_file(summary_prompt_path)

    # Recompose structuredDataPrompt
    structured_data_prompt_path = resolve_file_path(
        data["analysisPlan"]["structuredDataPrompt"]
    )
    data["analysisPlan"]["structuredDataPrompt"] = read_file(
        structured_data_prompt_path
    )

    # Recompose structuredDataSchema
    structured_data_schema_path = resolve_file_path(
        data["analysisPlan"]["structuredDataSchema"]
    )
    data["analysisPlan"]["structuredDataSchema"] = json.loads(
        read_file(structured_data_schema_path)
    )

    # Recompose successEvaluationPrompt
    success_evaluation_prompt_path = resolve_file_path(
        data["analysisPlan"]["successEvaluationPrompt"]
    )
    data["analysisPlan"]["successEvaluationPrompt"] = read_file(
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
