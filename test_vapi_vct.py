import unittest
import json
import os
from click.testing import CliRunner
from vapi_vct import cli, load_config
from unittest.mock import patch, MagicMock


class TestVapiVCTConfig(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.config_file = "test_vapi_config.json"

    def tearDown(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)

    def test_assistants_add(self):
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

        with open(self.config_file, "r") as f:
            config_data = json.load(f)

        self.assertIn("assistant_ids", config_data)
        self.assertIn("assistant1", config_data["assistant_ids"])
        self.assertIn("assistant2", config_data["assistant_ids"])

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

    def test_assistants_del(self):
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

        # Remove one assistant
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

        with open(self.config_file, "r") as f:
            config_data = json.load(f)

        self.assertNotIn("assistant1", config_data["assistant_ids"])
        self.assertIn("assistant2", config_data["assistant_ids"])

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
            cli, ["config", "assistants", "list", "--config", self.config_file]
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("assistant1", result.output)
        self.assertIn("assistant2", result.output)

    def test_assistants_list_empty(self):
        result = self.runner.invoke(
            cli, ["config", "assistants", "list", "--config", self.config_file]
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
        if os.path.exists(f"assistant_{self.mock_assistant_id}.json"):
            os.remove(f"assistant_{self.mock_assistant_id}.json")

    def create_test_config(self):
        config = {
            "api_key": self.mock_api_key,
            "assistant_ids": [self.mock_assistant_id],
        }
        with open(self.config_file, "w") as f:
            json.dump(config, f)

    @patch("vapi_vct.requests.get")
    def test_fetch(self, mock_get):
        self.create_test_config()

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

        result = self.runner.invoke(cli, ["fetch", "--config", self.config_file])

        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            f"Assistant data saved to assistant_{self.mock_assistant_id}.json",
            result.output,
        )

        self.assertTrue(os.path.exists(f"assistant_{self.mock_assistant_id}.json"))

    @patch("vapi_vct.requests.patch")
    def test_update(self, mock_patch):
        self.create_test_config()

        assistant_data = {
            "id": self.mock_assistant_id,
            "name": "Updated Mock Assistant",
            "model": {
                "provider": "openai",
                "model": "gpt-4",
                "temperature": 0.8,
                "systemPrompt": "You are an advanced AI assistant.",
                "messages": [
                    {"role": "system", "content": "You are an advanced AI assistant."}
                ],
            },
            "voice": {
                "provider": "elevenlabs",
                "voiceId": "updated_mock_voice_id",
                "stability": 0.6,
                "similarity": 0.8,
            },
            "firstMessage": "Greetings! How may I be of service?",
            "analysisPlan": {
                "enabled": True,
                "summaryPrompt": "Provide a detailed summary of the interaction.",
                "structuredDataPrompt": "Extract and categorize key information from the conversation.",
                "structuredDataSchema": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "sentiment": {"type": "string"},
                    },
                },
            },
        }
        with open(f"assistant_{self.mock_assistant_id}.json", "w") as f:
            json.dump(assistant_data, f)

        mock_response = MagicMock()
        mock_response.json.return_value = assistant_data
        mock_patch.return_value = mock_response

        result = self.runner.invoke(cli, ["update", "--config", self.config_file])

        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            f"Assistant {self.mock_assistant_id} updated successfully", result.output
        )

    def test_missing_api_key(self):
        config = {"assistant_ids": [self.mock_assistant_id]}
        with open(self.config_file, "w") as f:
            json.dump(config, f)

        result = self.runner.invoke(cli, ["fetch", "--config", self.config_file])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Error: API key not found in configuration file.", result.output)

        result = self.runner.invoke(cli, ["update", "--config", self.config_file])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Error: API key not found in configuration file.", result.output)

    @patch("vapi_vct.load_config")
    def test_api_key_from_default_config(self, mock_load_config):
        mock_load_config.return_value = {
            "api_key": "vapi_default_mock_api_key_789012",
            "assistant_ids": [self.mock_assistant_id],
        }

        with patch("vapi_vct.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "id": self.mock_assistant_id,
                "name": "Default Config Assistant",
                "model": {
                    "provider": "anthropic",
                    "model": "claude-2",
                    "temperature": 0.7,
                    "systemPrompt": "You are Claude, an AI assistant.",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are Claude, an AI assistant.",
                        }
                    ],
                },
                "voice": {
                    "provider": "elevenlabs",
                    "voiceId": "default_mock_voice_id",
                    "stability": 0.5,
                    "similarity": 0.75,
                },
                "firstMessage": "Hello, I'm Claude. How can I help you today?",
                "analysisPlan": {
                    "enabled": True,
                    "summaryPrompt": "Summarize the key points of our conversation.",
                    "structuredDataPrompt": "Extract relevant data from our interaction.",
                    "structuredDataSchema": {
                        "type": "object",
                        "properties": {
                            "intent": {"type": "string"},
                            "entities": {"type": "array"},
                        },
                    },
                },
            }
            mock_get.return_value = mock_response

            result = self.runner.invoke(cli, ["fetch", "--config", self.config_file])

        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            f"Assistant data saved to assistant_{self.mock_assistant_id}.json",
            result.output,
        )


if __name__ == "__main__":
    unittest.main()