import json
import os
import argparse


def extract_and_save(content, filename, directory):
    if content is None:
        return None
    with open(os.path.join(directory, filename), "w", encoding="utf-8") as f:
        f.write(content)
    return f"file://{filename}"


def process_assistant_json(file_path):
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


def main():
    parser = argparse.ArgumentParser(
        description="Extract components from Vapi assistant JSON files."
    )
    parser.add_argument("files", nargs="+", help="Path to one or more JSON files")
    args = parser.parse_args()

    for file_path in args.files:
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist.")
            continue
        if not file_path.lower().endswith(".json"):
            print(f"Error: {file_path} is not a JSON file.")
            continue
        try:
            process_assistant_json(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")


if __name__ == "__main__":
    main()
