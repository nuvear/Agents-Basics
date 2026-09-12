"""SerpApi weather adapter reused by all three two-hour workshop labs.

Derived from the original lmstudio_serpapi_api_to_mcp package. In Lab 3,
the local MCP server owns this adapter; the host discovers its tool.
"""

from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse

import requests

SERPAPI_SEARCH_URL = "https://serpapi.com/search.json"
_NUMBER_PATTERN = re.compile(r"[-+]?\d+(?:[.,]\d+)?")


class SerpApiWeatherError(RuntimeError):
    """Safe, user-displayable failure raised by the provider adapter."""


@dataclass(frozen=True)
class SerpApiConfig:
    """Runtime configuration for the direct SerpApi REST call."""

    api_key: str
    timeout_seconds: float = 60.0
    no_cache: bool = True
    retries: int = 2

    @classmethod
    def from_environment(cls) -> "SerpApiConfig":
        api_key = os.getenv("SERPAPI_KEY", "").strip()
        if not api_key:
            raise SerpApiWeatherError(
                "SERPAPI_KEY is missing. Add it to Colab Secrets on hosted "
                "Colab, or copy .env.example to .env on a local runtime."
            )

        timeout_raw = os.getenv(
            "SERPAPI_TIMEOUT_SECONDS",
            os.getenv("HTTP_TIMEOUT_SECONDS", "60"),
        ).strip()
        try:
            timeout_seconds = float(timeout_raw)
        except ValueError as exc:
            raise SerpApiWeatherError(
                "SERPAPI_TIMEOUT_SECONDS must be numeric."
            ) from exc
        if timeout_seconds <= 0:
            raise SerpApiWeatherError(
                "SERPAPI_TIMEOUT_SECONDS must be greater than zero."
            )

        retries_raw = os.getenv("SERPAPI_RETRIES", "2").strip()
        try:
            retries = int(retries_raw)
        except ValueError as exc:
            raise SerpApiWeatherError("SERPAPI_RETRIES must be an integer.") from exc
        if retries < 0:
            raise SerpApiWeatherError("SERPAPI_RETRIES cannot be negative.")

        no_cache = parse_boolean_environment(
            name="SERPAPI_NO_CACHE",
            default=True,
        )
        return cls(
            api_key=api_key,
            timeout_seconds=timeout_seconds,
            no_cache=no_cache,
            retries=retries,
        )


def build_weather_query(
    *,
    city: str,
    country_code: str | None = None,
    units: str = "celsius",
) -> str:
    """Build the human-readable Google query sent through SerpApi."""

    normalized_city = validate_city(city)
    normalized_country = normalize_country_code(country_code)
    normalized_units = normalize_units(units)
    location = (
        f"{normalized_city}, {normalized_country}"
        if normalized_country
        else normalized_city
    )
    unit_name = "Celsius" if normalized_units == "celsius" else "Fahrenheit"
    return f"current weather in {location} in {unit_name}"


def build_search_parameters(
    *,
    api_key: str,
    city: str,
    country_code: str | None = None,
    units: str = "celsius",
    language: str = "en",
    no_cache: bool = True,
) -> dict[str, str]:
    """Build the provider-specific query-string parameters.

    The returned dictionary contains the private API key and therefore should
    not be logged without passing it through :func:`redact_search_parameters`.
    """

    key = api_key.strip()
    if not key:
        raise SerpApiWeatherError("A non-empty SerpApi API key is required.")

    normalized_country = normalize_country_code(country_code)
    params: dict[str, str] = {
        "engine": "google",
        "q": build_weather_query(
            city=city,
            country_code=normalized_country,
            units=units,
        ),
        "api_key": key,
        "hl": normalize_language(language),
        "device": "desktop",
        "no_cache": "true" if no_cache else "false",
    }
    if normalized_country:
        params["gl"] = country_code_to_google_country(normalized_country)
    return params


def redact_search_parameters(params: Mapping[str, Any]) -> dict[str, Any]:
    """Return a copy of query parameters that is safe to display."""

    sanitized = dict(params)
    if "api_key" in sanitized:
        sanitized["api_key"] = "***REDACTED***"
    return sanitized


def request_timeout(timeout_seconds: float) -> tuple[float, float]:
    """Split connect vs read so a hung scrape can wait longer than DNS/TCP."""

    connect = min(10.0, float(timeout_seconds))
    return (connect, float(timeout_seconds))


def perform_serpapi_search(
    *,
    params: Mapping[str, str],
    timeout_seconds: float,
    session: requests.Session | None = None,
    retries: int = 2,
) -> Mapping[str, Any]:
    """Execute one SerpApi Google Search request and return parsed JSON."""

    if "api_key" not in params or not str(params["api_key"]).strip():
        raise SerpApiWeatherError("The SerpApi request is missing api_key.")
    if timeout_seconds <= 0:
        raise SerpApiWeatherError("timeout_seconds must be greater than zero.")
    if retries < 0:
        raise SerpApiWeatherError("retries cannot be negative.")

    request_session = session or requests.Session()
    request_session.headers.update(
        {
            "Accept": "application/json",
            "User-Agent": "lmstudio-serpapi-api-to-mcp-classroom/1.0",
        }
    )

    attempts = retries + 1
    response = None
    last_error: requests.RequestException | None = None
    for attempt in range(1, attempts + 1):
        try:
            response = request_session.get(
                SERPAPI_SEARCH_URL,
                params=dict(params),
                timeout=request_timeout(timeout_seconds),
            )
            break
        except (requests.Timeout, requests.ConnectionError) as exc:
            last_error = exc
            if attempt < attempts:
                print(
                    f"[retry {attempt}/{retries}] SerpApi timed out or dropped "
                    f"the connection; trying again."
                )
                continue
        except requests.RequestException as exc:
            last_error = exc
            break

    if response is None:
        detail = str(last_error or "unknown network error")
        secret = str(params.get("api_key") or "")
        if secret:
            detail = detail.replace(secret, "***REDACTED***")
        raise SerpApiWeatherError(
            "SerpApi connected but did not finish in "
            f"{timeout_seconds:.0f}s after {attempts} attempt(s). "
            "Set SERPAPI_TIMEOUT_SECONDS higher, or rerun; a no_cache Google "
            f"scrape can be slow. Last error: {detail}"
        ) from last_error

    raise_for_provider_status(response)

    try:
        payload = response.json()
    except ValueError as exc:
        raise SerpApiWeatherError(
            "SerpApi returned a non-JSON response."
        ) from exc
    if not isinstance(payload, Mapping):
        raise SerpApiWeatherError(
            "SerpApi returned an unexpected JSON response."
        )

    provider_error = payload.get("error")
    if provider_error:
        raise SerpApiWeatherError("SerpApi returned a provider error; check the query and account dashboard.")
    return payload


def get_current_weather(
    city: str,
    country_code: str | None = None,
    units: str = "celsius",
    language: str = "en",
    *,
    mock: bool = False,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """Return normalized current weather using SerpApi's Google Search API.

    Expected failures are returned as JSON rather than raised so this function
    can be safely used as an LLM tool result.
    """

    try:
        normalized_city = validate_city(city)
        normalized_country = normalize_country_code(country_code)
        normalized_units = normalize_units(units)
        normalized_language = normalize_language(language)

        if mock:
            return build_mock_weather_result(
                city=normalized_city,
                country_code=normalized_country,
                units=normalized_units,
            )

        config = SerpApiConfig.from_environment()
        params = build_search_parameters(
            api_key=config.api_key,
            city=normalized_city,
            country_code=normalized_country,
            units=normalized_units,
            language=normalized_language,
            no_cache=config.no_cache,
        )
        payload = perform_serpapi_search(
            params=params,
            timeout_seconds=config.timeout_seconds,
            session=session,
            retries=config.retries,
        )
        return normalize_serpapi_weather_result(
            payload=payload,
            requested_city=normalized_city,
            requested_country_code=normalized_country,
            requested_units=normalized_units,
            query=params["q"],
        )
    except SerpApiWeatherError as exc:
        return {
            "ok": False,
            "error_type": "serpapi_weather_error",
            "message": str(exc),
        }
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        return {
            "ok": False,
            "error_type": "provider_response_error",
            "message": f"Unexpected SerpApi weather response: {exc}",
        }


def normalize_serpapi_weather_result(
    *,
    payload: Mapping[str, Any],
    requested_city: str,
    requested_country_code: str | None,
    requested_units: str,
    query: str,
) -> dict[str, Any]:
    """Normalize Google's weather answer box into compact agent JSON."""

    if not isinstance(payload, Mapping):
        raise SerpApiWeatherError("SerpApi did not return a JSON object.")

    provider_error = payload.get("error")
    if provider_error:
        raise SerpApiWeatherError("SerpApi returned a provider error; check the query and account dashboard.")

    metadata = payload.get("search_metadata")
    if isinstance(metadata, Mapping):
        status = str(metadata.get("status") or "").strip().lower()
        if status == "error":
            raise SerpApiWeatherError(
                "SerpApi search failed; inspect the account dashboard."
            )

    answer_box = find_current_weather_answer_box(payload)
    provider_temperature = parse_number(
        answer_box.get("temperature"),
        field_name="temperature",
    )
    provider_unit = canonical_temperature_unit(
        answer_box.get("unit"),
        temperature_text=answer_box.get("temperature"),
    )
    normalized_units = normalize_units(requested_units)
    target_unit = "C" if normalized_units == "celsius" else "F"
    converted_temperature = convert_temperature(
        provider_temperature,
        from_unit=provider_unit,
        to_unit=target_unit,
    )

    result: dict[str, Any] = {
        "ok": True,
        "mock": False,
        "provider": "SerpApi Google Search API",
        "query": query,
        "location": {
            "requested_city": requested_city,
            "requested_country_code": requested_country_code,
            "resolved": optional_text(answer_box.get("location")),
        },
        "temperature": {
            "value": clean_number(converted_temperature),
            "unit": target_unit,
            "requested_units": normalized_units,
            "provider_value": clean_number(provider_temperature),
            "provider_unit": provider_unit,
        },
        "condition": optional_text(answer_box.get("weather")),
        "observation_label": optional_text(answer_box.get("date")),
        "feels_like": normalize_optional_temperature(
            answer_box.get("feels_like"),
            provider_unit=provider_unit,
            target_unit=target_unit,
        ),
        "precipitation": optional_text(answer_box.get("precipitation")),
        "humidity": optional_text(answer_box.get("humidity")),
        "wind": optional_text(answer_box.get("wind")),
        "today": extract_today_high_low(
            answer_box=answer_box,
            provider_unit=provider_unit,
            target_unit=target_unit,
        ),
        "air_quality": normalize_air_quality(answer_box.get("air_quality")),
        "alerts": normalize_alerts(
            answer_box.get("alert") or answer_box.get("alerts")
        ),
        "sources": normalize_sources(answer_box),
        "retrieved_at_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
    }

    if isinstance(metadata, Mapping):
        search_id = optional_text(metadata.get("id"))
        if search_id:
            result["serpapi_search_id"] = search_id

    return drop_none_values(result)


def find_current_weather_answer_box(
    payload: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Locate a current-weather result without falling back to web snippets."""

    candidates: list[Any] = [
        payload.get("answer_box"),
        payload.get("weather_result"),
        payload.get("weather_results"),
    ]
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            continue
        answer_type = str(candidate.get("type") or "").strip().lower()
        if answer_type == "weather_result":
            return candidate
        if "temperature" in candidate and (
            "weather" in candidate or "location" in candidate
        ):
            return candidate

    answer_box = payload.get("answer_box")
    returned_type = (
        answer_box.get("type") if isinstance(answer_box, Mapping) else None
    )
    suffix = (
        f" Returned answer-box type: {returned_type!r}."
        if returned_type
        else ""
    )
    raise SerpApiWeatherError(
        "Google did not return a current-weather answer box. Try a more "
        "specific city and country code." + suffix
    )


def build_mock_weather_result(
    *,
    city: str,
    country_code: str | None,
    units: str,
) -> dict[str, Any]:
    """Return clearly labelled teaching data without a network request."""

    value_c = 21.0
    target_unit = "C" if units == "celsius" else "F"
    value = convert_temperature(value_c, from_unit="C", to_unit=target_unit)
    return {
        "ok": True,
        "mock": True,
        "provider": "Classroom sample — not a live SerpApi request",
        "location": {
            "requested_city": city,
            "requested_country_code": country_code,
            "resolved": city,
        },
        "temperature": {
            "value": clean_number(value),
            "unit": target_unit,
            "requested_units": units,
        },
        "condition": "Cloudy",
        "observation_label": "DEMO DATA — not a live observation",
        "sources": [{"title": "Classroom demonstration data"}],
    }


def extract_today_high_low(
    *,
    answer_box: Mapping[str, Any],
    provider_unit: str,
    target_unit: str,
) -> dict[str, Any] | None:
    high_value: Any = answer_box.get("high")
    low_value: Any = answer_box.get("low")

    if high_value is None and low_value is None:
        forecast = answer_box.get("forecast")
        if (
            isinstance(forecast, Sequence)
            and not isinstance(forecast, (str, bytes, bytearray))
            and forecast
        ):
            first = forecast[0]
            if isinstance(first, Mapping):
                temperature = first.get("temperature")
                if isinstance(temperature, Mapping):
                    high_value = temperature.get("high")
                    low_value = temperature.get("low")

    high = normalize_optional_temperature(
        high_value,
        provider_unit=provider_unit,
        target_unit=target_unit,
    )
    low = normalize_optional_temperature(
        low_value,
        provider_unit=provider_unit,
        target_unit=target_unit,
    )
    if high is None and low is None:
        return None
    return drop_none_values({"high": high, "low": low, "unit": target_unit})


def normalize_optional_temperature(
    value: Any,
    *,
    provider_unit: str,
    target_unit: str,
) -> int | float | None:
    if value is None or value == "":
        return None
    parsed = parse_number(value, field_name="optional temperature")
    converted = convert_temperature(
        parsed,
        from_unit=provider_unit,
        to_unit=target_unit,
    )
    return clean_number(converted)


def normalize_air_quality(value: Any) -> dict[str, Any] | str | None:
    if isinstance(value, Mapping):
        normalized = {
            "text": optional_text(value.get("text")),
            "index": value.get("index"),
            "category": optional_text(value.get("category")),
        }
        return drop_none_values(normalized) or None
    return optional_text(value)


def normalize_alerts(value: Any) -> list[dict[str, Any]] | None:
    if not isinstance(value, Sequence) or isinstance(
        value, (str, bytes, bytearray)
    ):
        return None

    alerts: list[dict[str, Any]] = []
    for item in value[:5]:
        if not isinstance(item, Mapping):
            continue
        normalized = drop_none_values(
            {
                "type": optional_text(item.get("type") or item.get("title")),
                "source": optional_text(item.get("source")),
                "link": safe_http_url(item.get("link")),
            }
        )
        if normalized:
            alerts.append(normalized)
    return alerts or None


def normalize_sources(answer_box: Mapping[str, Any]) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    raw_sources = answer_box.get("sources")
    if isinstance(raw_sources, Sequence) and not isinstance(
        raw_sources, (str, bytes, bytearray)
    ):
        for item in raw_sources:
            if not isinstance(item, Mapping):
                continue
            append_source(
                sources,
                seen,
                title=optional_text(item.get("title") or item.get("name")),
                link=safe_http_url(item.get("link")),
            )

    raw_source = answer_box.get("source")
    if isinstance(raw_source, Mapping):
        append_source(
            sources,
            seen,
            title=optional_text(
                raw_source.get("title") or raw_source.get("name")
            ),
            link=safe_http_url(raw_source.get("link")),
        )
    else:
        source_text = optional_text(raw_source)
        if source_text:
            link = safe_http_url(source_text)
            append_source(
                sources,
                seen,
                title=hostname_title(link) if link else source_text,
                link=link,
            )

    if not sources:
        sources.append({"title": "Google weather result via SerpApi"})
    return sources


def append_source(
    sources: list[dict[str, str]],
    seen: set[tuple[str, str]],
    *,
    title: str | None,
    link: str | None,
) -> None:
    if not title and not link:
        return
    if not title and link:
        title = hostname_title(link)
    key = (title or "", link or "")
    if key in seen:
        return
    seen.add(key)
    item: dict[str, str] = {}
    if title:
        item["title"] = title
    if link:
        item["link"] = link
    sources.append(item)


def hostname_title(url: str | None) -> str | None:
    if not url:
        return None
    hostname = urlparse(url).hostname
    return hostname.removeprefix("www.") if hostname else None


def safe_http_url(value: Any) -> str | None:
    text = optional_text(value)
    if not text:
        return None
    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return text


def raise_for_provider_status(response: requests.Response) -> None:
    if response.status_code in {401, 403}:
        raise SerpApiWeatherError(
            f"SerpApi rejected the API key or request "
            f"(HTTP {response.status_code})."
        )
    if response.status_code == 429:
        raise SerpApiWeatherError(
            "SerpApi rate-limited the request or the account quota was "
            "reached (HTTP 429)."
        )
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        body = response.text.strip().replace("\n", " ")[:400]
        raise SerpApiWeatherError(
            f"SerpApi returned HTTP {response.status_code}: "
            "check the provider dashboard (response body suppressed)."
        ) from exc


def validate_city(city: str) -> str:
    if not isinstance(city, str):
        raise SerpApiWeatherError("city must be a string.")
    normalized = " ".join(city.strip().split())
    if not normalized:
        raise SerpApiWeatherError("city cannot be empty.")
    if len(normalized) > 120:
        raise SerpApiWeatherError("city is too long.")
    if any(ord(character) < 32 for character in normalized):
        raise SerpApiWeatherError("city contains invalid control characters.")
    return normalized


def normalize_country_code(country_code: str | None) -> str | None:
    if country_code is None:
        return None
    if not isinstance(country_code, str):
        raise SerpApiWeatherError(
            "country_code must be a two-letter string."
        )
    normalized = country_code.strip().upper()
    if not normalized:
        return None
    if len(normalized) != 2 or not normalized.isalpha():
        raise SerpApiWeatherError(
            "country_code must be a two-letter code, such as JP or PT."
        )
    return normalized


def country_code_to_google_country(country_code: str) -> str:
    # Google uses "uk" rather than ISO alpha-2 "gb" for this parameter.
    return "uk" if country_code == "GB" else country_code.lower()


def normalize_units(units: str) -> str:
    if not isinstance(units, str):
        raise SerpApiWeatherError("units must be a string.")
    normalized = units.strip().lower()
    aliases = {
        "c": "celsius",
        "metric": "celsius",
        "celsius": "celsius",
        "f": "fahrenheit",
        "imperial": "fahrenheit",
        "fahrenheit": "fahrenheit",
    }
    if normalized not in aliases:
        raise SerpApiWeatherError(
            "units must be either celsius or fahrenheit."
        )
    return aliases[normalized]


def normalize_language(language: str) -> str:
    if not isinstance(language, str):
        raise SerpApiWeatherError("language must be a string.")
    normalized = language.strip().lower().replace("_", "-")
    if not normalized:
        return "en"
    primary = normalized.split("-", 1)[0]
    if len(primary) != 2 or not primary.isalpha():
        raise SerpApiWeatherError(
            "language must begin with a two-letter code, such as en or ja."
        )
    return primary


def canonical_temperature_unit(
    value: Any,
    *,
    temperature_text: Any = None,
) -> str:
    for candidate in (value, temperature_text):
        if candidate is None:
            continue
        text = str(candidate).strip().upper()
        compact = (
            text.replace("°", "")
            .replace("DEGREES", "")
            .replace("DEGREE", "")
            .replace(" ", "")
        )
        if compact in {"C", "CELSIUS", "CENTIGRADE"} or compact.endswith("C"):
            return "C"
        if compact in {"F", "FAHRENHEIT"} or compact.endswith("F"):
            return "F"
    raise SerpApiWeatherError(
        f"Unsupported temperature unit in weather result: {value!r}."
    )


def parse_number(value: Any, *, field_name: str) -> float:
    if isinstance(value, bool):
        raise SerpApiWeatherError(f"{field_name} was not numeric.")
    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str):
        match = _NUMBER_PATTERN.search(value.replace("\u2212", "-"))
        if not match:
            raise SerpApiWeatherError(
                f"{field_name} was missing or not numeric."
            )
        number = float(match.group(0).replace(",", "."))
    else:
        raise SerpApiWeatherError(
            f"{field_name} was missing or not numeric."
        )
    if not math.isfinite(number):
        raise SerpApiWeatherError(f"{field_name} was not finite.")
    return number


def convert_temperature(value: float, *, from_unit: str, to_unit: str) -> float:
    if from_unit == to_unit:
        return value
    if from_unit == "C" and to_unit == "F":
        return (value * 9.0 / 5.0) + 32.0
    if from_unit == "F" and to_unit == "C":
        return (value - 32.0) * 5.0 / 9.0
    raise SerpApiWeatherError(
        f"Cannot convert temperature from {from_unit!r} to {to_unit!r}."
    )


def clean_number(value: float) -> int | float:
    rounded = round(value, 1)
    if math.isclose(rounded, round(rounded), abs_tol=1e-9):
        return int(round(rounded))
    return rounded


def optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def drop_none_values(mapping: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in mapping.items() if value is not None}


def parse_boolean_environment(*, name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise SerpApiWeatherError(
        f"{name} must be true/false, yes/no, on/off, or 1/0."
    )
