from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from serpapi_weather import (
    SERPAPI_SEARCH_URL,
    SerpApiWeatherError,
    build_search_parameters,
    get_current_weather,
    normalize_serpapi_weather_result,
    redact_search_parameters,
)


class FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code
        self.text = ""

    def json(self) -> dict:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.headers: dict[str, str] = {}
        self.last_url: str | None = None
        self.last_params: dict[str, str] | None = None
        self.last_timeout: float | None = None

    def get(
        self,
        url: str,
        *,
        params: dict[str, str],
        timeout: float,
    ) -> FakeResponse:
        self.last_url = url
        self.last_params = params
        self.last_timeout = timeout
        return FakeResponse(self.payload)


WEATHER_PAYLOAD_F = {
    "search_metadata": {"id": "demo-search-id", "status": "Success"},
    "answer_box": {
        "type": "weather_result",
        "temperature": "96",
        "unit": "Fahrenheit",
        "precipitation": "2%",
        "humidity": "43%",
        "wind": "8 mph",
        "location": "Dallas, TX",
        "date": "Monday 2:00 PM",
        "weather": "Partly cloudy",
        "feels_like": "99",
        "forecast": [
            {
                "day": "Monday",
                "temperature": {"high": "97", "low": "81"},
            }
        ],
        "sources": [
            {"title": "weather.com", "link": "https://weather.com/example"}
        ],
    },
}


class SerpApiWeatherTests(unittest.TestCase):
    def test_builds_google_search_parameters_and_redacts_key(self) -> None:
        params = build_search_parameters(
            api_key="super-secret",
            city="Tokyo",
            country_code="JP",
            units="celsius",
            language="en",
            no_cache=True,
        )
        self.assertEqual(params["engine"], "google")
        self.assertEqual(params["gl"], "jp")
        self.assertEqual(params["no_cache"], "true")
        self.assertIn("Tokyo", params["q"])
        self.assertEqual(redact_search_parameters(params)["api_key"], "***REDACTED***")

    def test_normalizes_and_converts_fahrenheit_to_celsius(self) -> None:
        result = normalize_serpapi_weather_result(
            payload=WEATHER_PAYLOAD_F,
            requested_city="Dallas",
            requested_country_code="US",
            requested_units="celsius",
            query="current weather in Dallas, US in Celsius",
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["temperature"]["value"], 35.6)
        self.assertEqual(result["temperature"]["unit"], "C")
        self.assertEqual(result["today"]["high"], 36.1)
        self.assertEqual(result["today"]["low"], 27.2)
        self.assertEqual(result["condition"], "Partly cloudy")

    def test_live_request_uses_serpapi_key_without_returning_it(self) -> None:
        session = FakeSession(WEATHER_PAYLOAD_F)
        environment = {
            "SERPAPI_KEY": "test-secret-key",
            "SERPAPI_NO_CACHE": "true",
            "HTTP_TIMEOUT_SECONDS": "12",
        }
        with patch.dict(os.environ, environment, clear=False):
            result = get_current_weather(
                city="Dallas",
                country_code="US",
                units="celsius",
                session=session,  # type: ignore[arg-type]
            )

        self.assertTrue(result["ok"])
        self.assertEqual(session.last_url, SERPAPI_SEARCH_URL)
        assert session.last_params is not None
        self.assertEqual(session.last_params["api_key"], "test-secret-key")
        self.assertNotIn("test-secret-key", str(result))
        self.assertEqual(session.last_timeout, 12.0)

    def test_missing_weather_answer_box_raises_safe_error(self) -> None:
        with self.assertRaises(SerpApiWeatherError):
            normalize_serpapi_weather_result(
                payload={"search_metadata": {"status": "Success"}},
                requested_city="Nowhere",
                requested_country_code=None,
                requested_units="celsius",
                query="current weather in Nowhere in Celsius",
            )

    def test_mock_mode_requires_no_key_and_is_labelled(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            result = get_current_weather(
                city="Tokyo",
                country_code="JP",
                units="fahrenheit",
                mock=True,
            )
        self.assertTrue(result["ok"])
        self.assertTrue(result["mock"])
        self.assertEqual(result["temperature"]["value"], 69.8)
        self.assertIn("not a live", result["provider"].lower())


if __name__ == "__main__":
    unittest.main()
