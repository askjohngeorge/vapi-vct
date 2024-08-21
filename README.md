# Vapi-VCT (Vapi Version Control Tools)

Vapi-VCT is a Python-based CLI tool designed to facilitate version control and management of Vapi AI assistants. This tool allows you to fetch, decompose, recompose, and update Vapi assistant configurations, making it easier to track changes, collaborate, and maintain your AI assistants.

## Features

- **Fetch**: Retrieve Vapi assistant configurations from the Vapi API.
- **Decompose**: Extract components of a Vapi assistant JSON into separate files for easier version control.
- **Recompose**: Rebuild a Vapi assistant JSON from its decomposed components.
- **Update**: Push updated Vapi assistant configurations back to the Vapi API.
- **Config Management**: Manage project-specific configurations directly from the command line.

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

3. Make the `vapi-cli` script executable:

```
chmod a+x vapi-cli
```

4. (Optional) Move the `vapi-cli` script to a directory in your PATH for easy access:

```
sudo mv vapi-cli /usr/local/bin/
```

## Configuration

Vapi-VCT supports a default configuration file and project-specific configuration files.

### Default Configuration

Create a default configuration file at `~/.vapi-vct/vapi-config.json` with your Vapi API key:

```json
{
  "api_key": "your_vapi_api_key_here"
}
```

### Project-Specific Configuration

In your project directory, create a `vapi-config.json` file with the following structure:

```json
{
  "assistant_ids": ["assistant_id_1", "assistant_id_2", ...]
}
```

The tool will first load the default configuration (if it exists) and then merge it with the project-specific configuration, with the project-specific settings taking precedence. This allows you to keep your API key secure and separate from project files while still being able to override or add settings on a per-project basis.

## Usage

Vapi-VCT provides a command-line interface with several commands for managing assistants and configurations.

### Fetching Assistants

To fetch assistants and optionally decompose them:

```
vapi-cli fetch [--config CONFIG_FILE] [--no-decompose]
```

- `--config`: Specify a custom configuration file (default: `vapi-config.json` in the current directory)
- `--no-decompose`: Skip decomposing fetched assistants

### Updating Assistants

To update assistants, optionally recomposing them first:

```
vapi-cli update [--config CONFIG_FILE] [--no-recompose]
```

- `--config`: Specify a custom configuration file (default: `vapi-config.json` in the current directory)
- `--no-recompose`: Skip recomposing assistants before updating

### Managing Project-Specific Configurations

#### Adding Assistant IDs

To add one or more assistant IDs to the configuration:

```
vapi-cli add-assistant ASSISTANT_ID [ASSISTANT_ID ...] [--config CONFIG_FILE]
```

#### Deleting Assistant IDs

To delete one or more assistant IDs from the configuration:

```
vapi-cli del-assistant ASSISTANT_ID [ASSISTANT_ID ...] [--config CONFIG_FILE]
```

#### Adding an API Key

To add an API key to the configuration:

```
vapi-cli add-apikey API_KEY [--config CONFIG_FILE]
```

#### Deleting the API Key

To delete the API key from the configuration:

```
vapi-cli del-apikey [--config CONFIG_FILE]
```

For all configuration management commands:
- `--config`: Specify a custom configuration file (default: `vapi-config.json` in the current directory)

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