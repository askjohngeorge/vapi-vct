import unittest
import json
import os
from click.testing import CliRunner
from vapi_vct import cli


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


if __name__ == "__main__":
    unittest.main()
