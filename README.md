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
git clone https://github.com/askjohngeorge/vapi_vct.git
cd vapi_vct
```

2. Install required dependencies:

```
pip install -r requirements.txt
```

3. Make the `vapi_vct` script executable:

```
chmod a+x vapi_vct
```

4. (Optional) Move the `vapi_vct` script to a directory in your PATH for easy access:

```
sudo mv vapi_vct /usr/local/bin/
```

## Configuration

Vapi-VCT supports a default configuration file and project-specific configuration files.

### Default Configuration

Create a default configuration file at `~/.vapi_vct/vapi_config.json` with your Vapi API key:

```json
{
  "api_key": "your_vapi_api_key_here"
}
```

### Project-Specific Configuration

In your project directory, create a `vapi_config.json` file with the following structure:

```json
{
  "assistant_ids": ["assistant_id_1", "assistant_id_2", ...]
}
```

The tool will first load the default configuration (if it exists) and then merge it with the project-specific configuration, with the project-specific settings taking precedence.

## Usage

Vapi-VCT provides a command-line interface with several commands for managing assistants and configurations.

### Fetching Assistants

To fetch assistants and optionally decompose them:

```
vapi_vct fetch [--config CONFIG_FILE] [--no-decompose]
```

- `--config`: Specify a custom configuration file (default: `vapi_config.json` in the current directory)
- `--no-decompose`: Skip decomposing fetched assistants

### Updating Assistants

To update assistants, optionally recomposing them first:

```
vapi_vct update [--config CONFIG_FILE] [--no-recompose]
```

- `--config`: Specify a custom configuration file (default: `vapi_config.json` in the current directory)
- `--no-recompose`: Skip recomposing assistants before updating

### Managing Project-Specific Configurations

#### Assistant Management

To manage assistant IDs in the configuration:

```
vapi_vct config assistants add ASSISTANT_ID [ASSISTANT_ID ...] [--config CONFIG_FILE]
vapi_vct config assistants remove ASSISTANT_ID [ASSISTANT_ID ...] [--config CONFIG_FILE]
vapi_vct config assistants list [--config CONFIG_FILE]
```

#### API Key Management

To manage the API key in the configuration:

```
vapi_vct config api_key set API_KEY [--config CONFIG_FILE]
vapi_vct config api_key clear [--config CONFIG_FILE]
```

For all configuration management commands:
- `--config`: Specify a custom configuration file (default: `vapi_config.json` in the current directory)

## File Structure

After fetching and decomposing, each assistant will have its own directory:

```
assistant_id/
├── assistant_config.json
├── system_prompt.txt
├── first_message.txt
├── summary_prompt.txt
├── structured_data_prompt.txt
├── structured_data_schema.json
└── success_evaluation_prompt.txt
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This project is not officially affiliated with, authorized, maintained, sponsored or endorsed by Vapi or any of its affiliates or subsidiaries. This is an independent and unofficial software. Use at your own risk.