# Vapi-VCT (Vapi Version Control Tools)

Vapi-VCT is a Python-based CLI tool designed to facilitate version control and management of Vapi AI assistants. This tool allows you to locally fetch, decompose, recompose, update, and publish Vapi assistant configurations, making it easier to track changes, collaborate, and maintain your AI assistants.

## Features

- **Fetch**: Retrieve Vapi assistant configurations from the Vapi API.
- **Decompose**: Extract components of a Vapi assistant JSON into separate files for easier version control.
- **Recompose**: Rebuild a Vapi assistant JSON from its decomposed components.
- **Update**: Push updated Vapi assistant configurations back to the Vapi API.
- **Publish**: Publish a new assistant from a decomposed directory.
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

3. (Optional) Make the `vapi_vct` script executable:

```
chmod a+x vapi_vct.py
```

4. (Optional) Create a symlink without the .py extension in a directory in your PATH:

```
sudo ln -s /path/to/vapi_vct.py /usr/local/bin/vapi_vct
```

*Examples in following sections assume you followed **all** these steps.*

Without the symlink created in step 4 you can use:

```
vapi_vct.py           # from the repo (if executable)
/path/to/vapi_vct.py  # from anywhere
```

Without making the script executable in step 3 you can use:

```
python vapi_vct.py           # from the repo
python /path/to/vapi_vct.py  # from anywhere
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

You can create and manage your local project-specific configuration using the command-line tools. For example, to add an assistant ID to the configuration:

```
vapi_vct config assistants add ASSISTANT_ID_1 [ASSISTANT_ID_2 ...]
```

This will create a `vapi_config.json` file in your project directory with the following structure:

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

### Publishing New Assistants

To publish a new assistant from a decomposed directory:

```
vapi_vct publish [--config CONFIG_FILE] DIRECTORY
```

- `--config`: Specify a custom configuration file (default: `vapi_config.json` in the current directory)
- `DIRECTORY`: The path to the decomposed assistant directory

This command will:
1. Recompose the assistant from the specified directory
2. Check for an existing name in the configuration
3. If no name is found, prompt the user for a name or generate a random one if the user enters "random"
4. Create a new assistant using the Vapi API
5. Update the local configuration with the new assistant's ID and directory mapping

After successful creation, the command will output the new assistant's name and ID, and update the configuration file.

### Managing Project-Specific Configurations

#### Assistant Management

To manage assistant IDs in the configuration:

```
vapi_vct config assistants add ASSISTANT_ID [ASSISTANT_ID ...] [--config CONFIG_FILE]
vapi_vct config assistants del ASSISTANT_ID [ASSISTANT_ID ...] [--config CONFIG_FILE]
vapi_vct config assistants ids [--config CONFIG_FILE]
vapi_vct config assistants dirs [--config CONFIG_FILE]
```

#### API Key Management

To manage the API key in the configuration:

```
vapi_vct config api_key add API_KEY [--config CONFIG_FILE]
vapi_vct config api_key del [--config CONFIG_FILE]
```

For all configuration management commands:
- `--config`: Specify a custom configuration file (default: `vapi_config.json` in the current directory)

## File Structure

After fetching and decomposing, each assistant will have its own directory named after the assistant's name:

```
assistant_name--assistant_id[:8]/
├── assistant_config.json
├── first_message.txt
├── metadata.json
├── structured_data_prompt.txt
├── structured_data_schema.json
├── success_evaluation_prompt.txt
├── summary_prompt.txt
└── system_prompt.txt
```

The `metadata.json` file contains assistant-specific information that you may wish to exclude from version control. You can easily exclude it by adding the following line to your `.gitignore` file:

```
**/metadata.json
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This project is not officially affiliated with, authorized, maintained, sponsored or endorsed by Vapi or any of its affiliates or subsidiaries. This is an independent and unofficial software. Use at your own risk.