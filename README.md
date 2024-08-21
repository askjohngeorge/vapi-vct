# Vapi-VCT (Vapi Version Control Tools)

Vapi-VCT is a Python-based CLI tool designed to facilitate version control and management of Vapi AI assistants. This tool allows you to fetch, decompose, recompose, and update Vapi assistant configurations, making it easier to track changes, collaborate, and maintain your AI assistants.

## Features

- **Fetch**: Retrieve Vapi assistant configurations from the Vapi API.
- **Decompose**: Extract components of a Vapi assistant JSON into separate files for easier version control.
- **Recompose**: Rebuild a Vapi assistant JSON from its decomposed components.
- **Update**: Push updated Vapi assistant configurations back to the Vapi API.

## Prerequisites

- Python 3.x
- Access to Vapi API
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

## Configuration

Create a `vapi-config.json` file in the root directory with the following structure:

```json
{
  "api_key": "your_vapi_api_key_here",
  "assistant_ids": ["assistant_id_1", "assistant_id_2", ...]
}
```

## Usage

Vapi-VCT provides a command-line interface with two main commands: `fetch` and `update`.

### Fetching Assistants

To fetch assistants and optionally decompose them:

```
python vapi-cli.py fetch [--config CONFIG_FILE] [--no-decompose]
```

- `--config`: Specify a custom configuration file (default: `vapi-config.json`)
- `--no-decompose`: Skip decomposing fetched assistants

### Updating Assistants

To update assistants, optionally recomposing them first:

```
python vapi-cli.py update [--config CONFIG_FILE] [--no-recompose]
```

- `--config`: Specify a custom configuration file (default: `vapi-config.json`)
- `--no-recompose`: Skip recomposing assistants before updating

## File Structure

After fetching and decomposing, each assistant will have its own directory:

```
assistant_id/
├── assistant-config.json
├── system-prompt.txt
├── first-message.txt
├── summary-prompt.txt
├── structured-data-prompt.txt
├── structured-data-schema.json
└── success-evaluation-prompt.txt
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This project is not officially affiliated with, authorized, maintained, sponsored or endorsed by Vapi or any of its affiliates or subsidiaries. This is an independent and unofficial software. Use at your own risk.
