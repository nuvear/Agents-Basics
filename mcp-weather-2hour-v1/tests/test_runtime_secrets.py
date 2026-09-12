from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runtime_secrets import apply_runtime_secrets, lab_run_options, should_mock_weather


class RuntimeSecretTests(unittest.TestCase):
    def test_hosted_prefers_colab_secrets_over_dotenv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text(
                "OPENAI_API_KEY=from-file\nSERPAPI_KEY=file-serp\n",
                encoding="utf-8",
            )
            secrets = {
                "OPENAI_API_KEY": "from-colab",
                "SERPAPI_KEY": "colab-serp",
            }
            with patch.dict(os.environ, {"OPENAI_API_KEY": "stale-env"}, clear=True), patch(
                "runtime_secrets.read_colab_secret",
                side_effect=lambda name: secrets.get(name, ""),
            ):
                sources = apply_runtime_secrets(dotenv_paths=[env_path], hosted=True)
                self.assertEqual(os.environ["OPENAI_API_KEY"], "from-colab")
                self.assertEqual(os.environ["SERPAPI_KEY"], "colab-serp")
                self.assertEqual(sources["OPENAI_API_KEY"], "Colab Secrets")
                self.assertEqual(sources["SERPAPI_KEY"], "Colab Secrets")

    def test_hosted_falls_back_to_dotenv_when_secrets_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text(
                "OPENAI_API_KEY=from-file\nSERPAPI_KEY=file-serp\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {}, clear=True), patch(
                "runtime_secrets.read_colab_secret",
                return_value="",
            ):
                sources = apply_runtime_secrets(dotenv_paths=[env_path], hosted=True)
                self.assertEqual(os.environ["OPENAI_API_KEY"], "from-file")
                self.assertEqual(sources["OPENAI_API_KEY"], "local .env")
                self.assertEqual(sources["SERPAPI_KEY"], "local .env")

    def test_local_prefers_dotenv_when_environment_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text(
                "OPENAI_API_KEY=local-openai\nSERPAPI_KEY=local-serp\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {}, clear=True), patch(
                "runtime_secrets.read_colab_secret",
                return_value="",
            ):
                sources = apply_runtime_secrets(dotenv_paths=[env_path], hosted=False)
                self.assertEqual(os.environ["OPENAI_API_KEY"], "local-openai")
                self.assertEqual(os.environ["SERPAPI_KEY"], "local-serp")
                self.assertEqual(sources["OPENAI_API_KEY"], "local .env")
                self.assertEqual(sources["SERPAPI_KEY"], "local .env")

    def test_local_does_not_override_existing_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text("OPENAI_API_KEY=from-file\n", encoding="utf-8")
            with patch.dict(os.environ, {"OPENAI_API_KEY": "already-set"}, clear=True), patch(
                "runtime_secrets.read_colab_secret",
                return_value="",
            ):
                sources = apply_runtime_secrets(dotenv_paths=[env_path], hosted=False)
                self.assertEqual(os.environ["OPENAI_API_KEY"], "already-set")
                self.assertEqual(sources["OPENAI_API_KEY"], "environment")

    def test_local_falls_back_to_colab_secrets(self) -> None:
        with patch.dict(os.environ, {}, clear=True), patch(
            "runtime_secrets.read_colab_secret",
            side_effect=lambda name: "notebook-secret" if name == "OPENAI_API_KEY" else "",
        ):
            sources = apply_runtime_secrets(dotenv_paths=[], hosted=False)
            self.assertEqual(os.environ["OPENAI_API_KEY"], "notebook-secret")
            self.assertEqual(sources["OPENAI_API_KEY"], "Colab Secrets")
            self.assertEqual(sources["SERPAPI_KEY"], "missing")

    def test_live_weather_when_serpapi_key_present(self) -> None:
        with patch.dict(os.environ, {"SERPAPI_KEY": "live-key", "OPENAI_API_KEY": "model-key"}, clear=True):
            self.assertFalse(should_mock_weather())
            options = lab_run_options()
            self.assertIn("--provider", options)
            self.assertIn("openai", options)
            self.assertIn("--force-tool", options)
            self.assertNotIn("--mock-weather", options)
            self.assertNotIn("--offline", options)

    def test_sample_weather_when_serpapi_key_missing(self) -> None:
        with patch.dict(os.environ, {"OPENAI_API_KEY": "model-key"}, clear=True):
            self.assertTrue(should_mock_weather())
            options = lab_run_options()
            self.assertIn("--mock-weather", options)

    def test_offline_when_openai_key_missing(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            options = lab_run_options()
            self.assertIn("--offline", options)


if __name__ == "__main__":
    unittest.main()
