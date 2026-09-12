from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import requests

from serpapi_weather import (
    SERPAPI_SEARCH_URL,
    SerpApiWeatherError,
    build_search_parameters,
    get_current_weather,
    normalize_serpapi_weather_result,
    perform_serpapi_search,
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
        self.last_timeout: float | tuple[float, float] | None = None

    def get(
        self,
        url: str,
        *,
        params: dict[str, str],
        timeout: float | tuple[float, float],
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
        self.assertNotIn("Fahrenheit", params["q"])
        self.assertNotIn("Celsius", params["q"])
        fahrenheit = build_search_parameters(
            api_key="super-secret",
            city="Tokyo",
            country_code="JP",
            units="fahrenheit",
        )
        self.assertEqual(fahrenheit["q"], params["q"])
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
        self.assertEqual(session.last_timeout, (10.0, 12.0))

    def test_retries_timeout_then_succeeds(self) -> None:
        class FlakySession:
            def __init__(self) -> None:
                self.headers: dict[str, str] = {}
                self.calls = 0

            def get(self, url, *, params, timeout):
                self.calls += 1
                if self.calls == 1:
                    raise requests.Timeout("read timed out")
                return FakeResponse(WEATHER_PAYLOAD_F)

        session = FlakySession()
        params = build_search_parameters(
            api_key="test-secret-key",
            city="Dallas",
            country_code="US",
            units="celsius",
        )
        payload = perform_serpapi_search(
            params=params,
            timeout_seconds=12,
            session=session,  # type: ignore[arg-type]
            retries=2,
        )
        self.assertEqual(session.calls, 2)
        self.assertEqual(payload["search_metadata"]["id"], "demo-search-id")

    def test_timeout_retries_are_exhausted(self) -> None:
        class AlwaysTimeout:
            def __init__(self) -> None:
                self.headers: dict[str, str] = {}
                self.calls = 0

            def get(self, url, *, params, timeout):
                self.calls += 1
                raise requests.Timeout("read timed out")

        session = AlwaysTimeout()
        params = build_search_parameters(
            api_key="test-secret-key",
            city="Dallas",
            country_code="US",
            units="celsius",
        )
        with self.assertRaises(SerpApiWeatherError) as caught:
            perform_serpapi_search(
                params=params,
                timeout_seconds=12,
                session=session,  # type: ignore[arg-type]
                retries=2,
            )
        self.assertEqual(session.calls, 4)
        self.assertIn("12s", str(caught.exception))
        self.assertNotIn("test-secret-key", str(caught.exception))

    def test_timeout_falls_back_to_serpapi_cache(self) -> None:
        class TimeoutThenCache:
            def __init__(self) -> None:
                self.headers: dict[str, str] = {}
                self.calls = 0
                self.last_no_cache: str | None = None

            def get(self, url, *, params, timeout):
                self.calls += 1
                self.last_no_cache = params.get("no_cache")
                if params.get("no_cache") == "true":
                    raise requests.Timeout("read timed out")
                return FakeResponse(WEATHER_PAYLOAD_F)

        session = TimeoutThenCache()
        params = build_search_parameters(
            api_key="test-secret-key",
            city="Dallas",
            country_code="US",
            units="celsius",
        )
        payload = perform_serpapi_search(
            params=params,
            timeout_seconds=12,
            session=session,  # type: ignore[arg-type]
            retries=1,
        )
        self.assertGreaterEqual(session.calls, 2)
        self.assertEqual(session.last_no_cache, "false")
        self.assertEqual(payload["search_metadata"]["id"], "demo-search-id")

    def test_retries_city_only_when_answer_box_missing(self) -> None:
        class TwoQuerySession:
            def __init__(self) -> None:
                self.headers: dict[str, str] = {}
                self.queries: list[str] = []

            def get(self, url, *, params, timeout):
                self.queries.append(params["q"])
                if "SG" in params["q"]:
                    return FakeResponse({"search_metadata": {"status": "Success"}})
                return FakeResponse(WEATHER_PAYLOAD_F)

        session = TwoQuerySession()
        environment = {"SERPAPI_KEY": "test-secret-key", "SERPAPI_NO_CACHE": "true"}
        with patch.dict(os.environ, environment, clear=False):
            result = get_current_weather(
                city="Singapore",
                country_code="SG",
                units="celsius",
                session=session,  # type: ignore[arg-type]
            )
        self.assertTrue(result["ok"])
        self.assertEqual(len(session.queries), 2)
        self.assertIn("Singapore, SG", session.queries[0])
        self.assertEqual(session.queries[1], "current weather in Singapore")

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
