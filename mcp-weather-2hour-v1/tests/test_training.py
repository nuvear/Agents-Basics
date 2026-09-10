import copy
import importlib.util
import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from agent_core import ROOT, run_loop, client_config
from weather_contract import TOOL, execute_weather, scrub

def args(**changes):
    return SimpleNamespace(**({"question": "Weather in Tokyo?", "offline": False,
        "mock_weather": True, "force_tool": False, "provider": "openai", "model": None} | changes))

def tool_call(arguments=None, name="get_current_weather"):
    return {"role": "assistant", "tool_calls": [{"id": "call-1", "type": "function", "function": {
        "name": name, "arguments": json.dumps(arguments or {"city": "Tokyo", "country_code": "JP", "units": "celsius"})}}]}

class LoopTests(unittest.IsolatedAsyncioTestCase):
    async def test_tool_result_returned_with_matching_call_id(self):
        histories = []
        async def completion(messages, tools, force):
            histories.append(copy.deepcopy(messages))
            return tool_call() if len(histories) == 1 else {"role": "assistant", "content": "Sample weather only."}
        execute = AsyncMock(return_value={"ok": True, "mock": True})
        answer = await run_loop(args(), [TOOL], execute, completion)
        self.assertEqual(answer, "Sample weather only.")
        self.assertEqual(histories[1][-1]["tool_call_id"], "call-1")
        self.assertTrue(json.loads(histories[1][-1]["content"])["mock"])
        execute.assert_awaited_once()

    async def test_text_without_tool_withheld(self):
        with self.assertRaisesRegex(ValueError, "withheld"):
            await run_loop(args(), [TOOL], AsyncMock(), AsyncMock(return_value={"content": "Tokyo is hot"}))

    async def test_unknown_tool_never_executes(self):
        execute = AsyncMock()
        with self.assertRaises(ValueError):
            await run_loop(args(), [TOOL], execute, AsyncMock(return_value=tool_call(name="delete_files")))
        execute.assert_not_awaited()

    async def test_malformed_json_never_executes(self):
        msg = tool_call()
        msg["tool_calls"][0]["function"]["arguments"] = "{bad"
        execute = AsyncMock()
        with self.assertRaises(ValueError):
            await run_loop(args(), [TOOL], execute, AsyncMock(return_value=msg))
        execute.assert_not_awaited()

    async def test_tool_budget_stops_multiple_calls(self):
        msg = tool_call()
        msg["tool_calls"] *= 5
        execute = AsyncMock(return_value={"ok": True})
        with self.assertRaisesRegex(ValueError, "Tool budget"):
            await run_loop(args(), [TOOL], execute, AsyncMock(return_value=msg))
        self.assertEqual(execute.await_count, 4)

    async def test_provider_failure_returned_to_model(self):
        completion = AsyncMock(side_effect=[tool_call(), {"content": "Weather unavailable."}])
        answer = await run_loop(args(), [TOOL], AsyncMock(return_value={"ok": False, "error": "quota"}), completion)
        self.assertEqual(answer, "Weather unavailable.")

    async def test_openai_and_lmstudio_config_are_separate(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "cloud-secret", "LM_STUDIO_API_KEY": "local-secret", "LM_STUDIO_MODEL": "local-model"}, clear=True):
            cloud, _ = client_config(args())
            local, model = client_config(args(provider="lmstudio"))
            self.assertEqual(str(cloud.base_url), "https://api.openai.com/v1/")
            self.assertEqual(cloud.api_key, "cloud-secret")
            self.assertEqual(local.api_key, "local-secret")
            self.assertEqual(model, "local-model")
            await cloud.close()
            await local.close()

    async def test_real_stdio_discovery_execution_and_validation(self):
        spec = importlib.util.spec_from_file_location("mcp_lesson", ROOT / "03_mcp_agent.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        async with module.weather_session(True) as session:
            listed = await session.list_tools()
            self.assertEqual([t.name for t in listed.tools], ["get_current_weather"])
            result = await session.call_tool("get_current_weather", {"city": "Tokyo", "country_code": "JP", "units": "fahrenheit"})
            data = json.loads(result.content[0].text)
            self.assertFalse(result.isError)
            self.assertTrue(data["mock"])
            self.assertEqual(data["temperature"]["value"], 69.8)
            invalid = await session.call_tool("get_current_weather", {"city": "Tokyo", "country_code": "JP", "units": "kelvin"})
            self.assertTrue(invalid.isError)

class BoundaryTests(unittest.TestCase):
    def test_extra_and_invalid_arguments_rejected(self):
        for data in ({"city": "Tokyo"}, {"city": "Tokyo", "country_code": "JP", "units": "celsius", "api_key": "x"}):
            self.assertFalse(execute_weather(data, mock=True)["ok"])

    def test_credentials_redacted_from_nested_result(self):
        with patch.dict(os.environ, {"SERPAPI_KEY": "test-secret"}):
            self.assertNotIn("test-secret", str(scrub({"error": ["echo test-secret"]})))

    def test_openai_key_missing_clear_error(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaisesRegex(ValueError, "OPENAI_API_KEY"):
            client_config(args())

if __name__ == "__main__":
    unittest.main()
