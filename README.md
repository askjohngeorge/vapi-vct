# Vapi-VCT (Vapi Version Control Tools)

Vapi-VCT is a suite of Python scripts designed to facilitate version control and management of Vapi AI assistants. These tools allow you to decompose, recompose, fetch, and update Vapi assistant configurations, making it easier to track changes, collaborate, and maintain your AI assistants.

## Features

- **Fetch**: Retrieve multiple Vapi assistant configurations from their IDs.
- **Decompose**: Extract components of a Vapi assistant JSON into separate files for easier version control.
- **Recompose**: Rebuild a Vapi assistant JSON from its decomposed components.

## Scripts

1. `vapi-fetch-assistants.py`: Fetches multiple Vapi assistant configurations based on IDs from a file.
2. `vapi-assistant-decomposer.py`: Extracts components from Vapi assistant JSON files.
3. `vapi-assistant-recomposer.py`: Rebuilds Vapi assistant JSON files from extracted components.
4. `vapi-update-assistants.py`: Updates Vapi assistant configurations from JSON files.

## Prerequisites

- Python 3.x
- Access to Vapi API (for fetching assistants)
- Vapi Private API Key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/askjohngeorge/vapi-vct.git
   cd vapi-vct
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Fetching Assistants

1. Create a file named `assistants.txt` with one assistant ID per line.

2. Export your Vapi Private API Key as an environment variable:
   ```
   export VAPI_PRIVATE_API_KEY=your_api_key_here
   ```

3. Run the fetch script:
   ```
   python vapi-fetch-assistants-from-file.py
   ```

This will create JSON files for each fetched assistant in the format `assistant_<assistantId>.json`.

### Decomposing Assistants

```
python vapi-assistant-decomposer.py path/to/assistant1.json path/to/assistant2.json
```

This will create a directory for each assistant, containing separate files for each component.

### Recomposing Assistants

```
python vapi-assistant-recomposer.py path/to/assistant1_directory path/to/assistant2_directory
```

This will create a JSON file for each assistant, combining the components from their respective directories.

### Updating Assistants

```
python vapi-update-assistants.py path/to/assistant1.json path/to/assistant2.json
```

This will update the Vapi assistant configurations from the JSON files.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## Acknowledgments

- Vapi for providing the voice AI assistant platform

## Disclaimer

This project is not officially affiliated with, authorized, maintained, sponsored or endorsed by Vapi or any of its affiliates or subsidiaries. This is an independent and unofficial software. Use at your own risk.
