import unittest
import json
import os
from click.testing import CliRunner
from vapi_vct import cli
from unittest.mock import patch, MagicMock, mock_open


class TestVapiVCTConfig(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.config_file = "test_vapi_config.json"

    def tearDown(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)

    @patch("vapi_vct.load_config")
    def test_assistants_add(self, mock_load_config):
        mock_config = {"assistant_ids": []}
        mock_load_config.return_value = mock_config

        with patch("vapi_vct.update_config") as mock_update_config:
            result = self.runner.invoke(
                cli,
                [
                    "config",
                    "assistants",
                    "add",
                    "assistant1",
                    "assistant2",
                    "--config",
                    self.config_file,
                ],
            )

        self.assertEqual(result.exit_code, 0)
        expected_call = mock_update_config.call_args[0][1]
        self.assertEqual(
            sorted(expected_call["assistant_ids"]), ["assistant1", "assistant2"]
        )

    def test_assistants_add_duplicate(self):
        # Add initial assistant
        self.runner.invoke(
            cli,
            ["config", "assistants", "add", "assistant1", "--config", self.config_file],
        )

        # Try to add the same assistant again
        result = self.runner.invoke(
            cli,
            ["config", "assistants", "add", "assistant1", "--config", self.config_file],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            "Assistant ID assistant1 already exists. Skipping.", result.output
        )

        with open(self.config_file, "r") as f:
            config_data = json.load(f)

        self.assertEqual(len(config_data["assistant_ids"]), 1)

    @patch("vapi_vct.load_config")
    def test_assistants_del(self, mock_load_config):
        mock_config = {
            "assistant_ids": ["assistant1", "assistant2"],
            "assistant_directories": {"assistant1": "dir1"},
        }
        mock_load_config.return_value = mock_config

        with patch("vapi_vct.update_config") as mock_update_config:
            result = self.runner.invoke(
                cli,
                [
                    "config",
                    "assistants",
                    "del",
                    "assistant1",
                    "--config",
                    self.config_file,
                ],
            )

        self.assertEqual(result.exit_code, 0)
        mock_update_config.assert_called_once_with(
            self.config_file,
            {"assistant_ids": ["assistant2"], "assistant_directories": {}},
        )

    def test_assistants_del_nonexistent(self):
        result = self.runner.invoke(
            cli,
            [
                "config",
                "assistants",
                "del",
                "nonexistent",
                "--config",
                self.config_file,
            ],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Assistant ID nonexistent not found. Skipping.", result.output)

    @patch("vapi_vct.load_config")
    def test_assistants_ids(self, mock_load_config):
        mock_config = {"assistant_ids": ["assistant1", "assistant2"]}
        mock_load_config.return_value = mock_config

        result = self.runner.invoke(
            cli, ["config", "assistants", "ids", "--config", self.config_file]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("assistant1", result.output)
        self.assertIn("assistant2", result.output)

    @patch("vapi_vct.load_config")
    def test_assistants_dirs(self, mock_load_config):
        mock_config = {
            "assistant_directories": {"assistant1": "dir1", "assistant2": "dir2"}
        }
        mock_load_config.return_value = mock_config

        result = self.runner.invoke(
            cli, ["config", "assistants", "dirs", "--config", self.config_file]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("assistant1 → dir1", result.output)
        self.assertIn("assistant2 → dir2", result.output)

    def test_assistants_list(self):
        # Add assistants first
        self.runner.invoke(
            cli,
            [
                "config",
                "assistants",
                "add",
                "assistant1",
                "assistant2",
                "--config",
                self.config_file,
            ],
        )

        result = self.runner.invoke(
            cli, ["config", "assistants", "ids", "--config", self.config_file]
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("assistant1", result.output)
        self.assertIn("assistant2", result.output)

    def test_assistants_list_empty(self):
        result = self.runner.invoke(
            cli, ["config", "assistants", "ids", "--config", self.config_file]
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("No assistant IDs found in the configuration.", result.output)

    def test_api_key_add(self):
        result = self.runner.invoke(
            cli,
            ["config", "api_key", "add", "test_api_key", "--config", self.config_file],
        )
        self.assertEqual(result.exit_code, 0)

        with open(self.config_file, "r") as f:
            config_data = json.load(f)

        self.assertEqual(config_data["api_key"], "test_api_key")

    def test_api_key_del(self):
        # Set API key first
        self.runner.invoke(
            cli,
            ["config", "api_key", "add", "test_api_key", "--config", self.config_file],
        )

        # Delete API key
        result = self.runner.invoke(
            cli, ["config", "api_key", "del", "--config", self.config_file]
        )
        self.assertEqual(result.exit_code, 0)

        with open(self.config_file, "r") as f:
            config_data = json.load(f)

        self.assertNotIn("api_key", config_data)

    def test_api_key_del_nonexistent(self):
        result = self.runner.invoke(
            cli, ["config", "api_key", "del", "--config", self.config_file]
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("No API key found in the configuration", result.output)


class TestVapiVCTFetchUpdate(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.config_file = "test_vapi_config.json"
        self.mock_assistant_id = "asst_mock123456"
        self.mock_api_key = "vapi_mock_api_key_123456"

    def tearDown(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        if os.path.exists(f"assistant_{self.mock_assistant_id[:8]}_fetched.json"):
            os.remove(f"assistant_{self.mock_assistant_id[:8]}_fetched.json")

    def create_test_config(self):
        config = {
            "api_key": self.mock_api_key,
            "assistant_ids": [self.mock_assistant_id],
        }
        with open(self.config_file, "w") as f:
            json.dump(config, f)

    @patch("vapi_vct.requests.get")
    @patch("vapi_vct.load_config")
    @patch("vapi_vct.decompose_assistant")
    def test_fetch(self, mock_decompose, mock_load_config, mock_get):
        mock_config = {
            "api_key": self.mock_api_key,
            "assistant_ids": [self.mock_assistant_id],
        }
        mock_load_config.return_value = mock_config

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": self.mock_assistant_id,
            "name": "Mock Assistant",
            "model": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "systemPrompt": "You are a helpful assistant.",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."}
                ],
            },
            "voice": {
                "provider": "elevenlabs",
                "voiceId": "mock_voice_id",
                "stability": 0.5,
                "similarity": 0.75,
            },
            "firstMessage": "Hello! How can I assist you today?",
            "analysisPlan": {
                "enabled": True,
                "summaryPrompt": "Summarize the conversation.",
                "structuredDataPrompt": "Extract key information.",
                "structuredDataSchema": {"type": "object", "properties": {}},
            },
        }
        mock_get.return_value = mock_response

        with patch("builtins.open", mock_open()) as mock_file:
            result = self.runner.invoke(cli, ["fetch", "--config", self.config_file])

        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            f"Assistant data saved to mock_assistant--{self.mock_assistant_id[:8]}_fetched.json",
            result.output,
        )
        mock_decompose.assert_called_once()

    @patch("vapi_vct.requests.patch")
    @patch("vapi_vct.load_config")
    @patch("vapi_vct.recompose_assistant")
    @patch("os.path.isdir", return_value=True)
    def test_update(self, mock_isdir, mock_recompose, mock_load_config, mock_patch):
        mock_config = {
            "api_key": self.mock_api_key,
            "assistant_ids": [self.mock_assistant_id],
            "assistant_directories": {self.mock_assistant_id: "mock_assistant"},
        }
        mock_load_config.return_value = mock_config

        mock_recompose.return_value = "mock_assistant_recomposed.json"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": self.mock_assistant_id,
            "name": "Updated Mock Assistant",
        }
        mock_patch.return_value = mock_response

        with patch("builtins.open", mock_open(read_data='{"id": "asst_mock123456"}')):
            result = self.runner.invoke(cli, ["update", "--config", self.config_file])

        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            f"Assistant {self.mock_assistant_id} updated successfully", result.output
        )
        mock_recompose.assert_called_once_with("mock_assistant")
        mock_patch.assert_called_once()

    @patch("vapi_vct.requests.get")
    @patch("vapi_vct.load_config")
    @patch("vapi_vct.decompose_assistant")
    def test_project_specific_config(self, mock_decompose, mock_load_config, mock_get):
        mock_config = {
            "api_key": "vapi_project_specific_mock_api_key_789012",
            "assistant_ids": [self.mock_assistant_id],
        }
        mock_load_config.return_value = mock_config

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": self.mock_assistant_id,
            "name": "Project Specific Config Assistant",
            "model": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "systemPrompt": "You are a helpful assistant.",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."}
                ],
            },
            "voice": {
                "provider": "elevenlabs",
                "voiceId": "mock_voice_id",
                "stability": 0.5,
                "similarity": 0.75,
            },
            "firstMessage": "Hello! How can I assist you today?",
            "analysisPlan": {
                "enabled": True,
                "summaryPrompt": "Summarize the conversation.",
                "structuredDataPrompt": "Extract key information.",
                "structuredDataSchema": {"type": "object", "properties": {}},
            },
        }
        mock_get.return_value = mock_response

        with patch("builtins.open", mock_open()) as mock_file:
            result = self.runner.invoke(cli, ["fetch", "--config", self.config_file])

        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            f"Assistant data saved to project_specific_config_assistant--{self.mock_assistant_id[:8]}_fetched.json",
            result.output,
        )
        mock_load_config.assert_called_once_with(self.config_file)
        mock_decompose.assert_called_once()

    @patch("vapi_vct.load_config")
    @patch("os.path.exists", return_value=False)
    def test_missing_api_key(self, mock_exists, mock_load_config):
        mock_load_config.return_value = {"assistant_ids": [self.mock_assistant_id]}

        result = self.runner.invoke(cli, ["fetch", "--config", self.config_file])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error: API key not found in configuration file.", result.output)

        result = self.runner.invoke(cli, ["update", "--config", self.config_file])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error: API key not found in configuration file.", result.output)


if __name__ == "__main__":
    unittest.main()
