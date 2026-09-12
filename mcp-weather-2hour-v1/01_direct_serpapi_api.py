"""Lesson 1: make a direct SerpApi REST call without an LLM.

This script deliberately shows the ordinary HTTP request/response boundary
before any tool calling or MCP abstraction is introduced.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from runtime_secrets import apply_runtime_secrets
from serpapi_weather import (
    SERPAPI_SEARCH_URL,
    SerpApiConfig,
    SerpApiWeatherError,
    build_search_parameters,
    normalize_serpapi_weather_result,
    perform_serpapi_search,
)

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_SAMPLE = PROJECT_DIR / "examples" / "weather_answer_box_sample.json"


def load_sample_payload(path: Path) -> Mapping[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SerpApiWeatherError(
            f"Could not read sample payload {path}: {exc}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise SerpApiWeatherError(
            f"Sample payload is invalid JSON: {exc}"
        ) from exc
    if not isinstance(payload, Mapping):
        raise SerpApiWeatherError("Sample payload must contain a JSON object.")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Demonstrate a direct SerpApi Google Search API call and extract "
            "the current-weather answer box."
        )
    )
    parser.add_argument("city", nargs="?", default="Tokyo")
    parser.add_argument(
        "--country",
        default="JP",
        help="Optional two-letter country code, such as JP or PT.",
    )
    parser.add_argument(
        "--units",
        choices=("celsius", "fahrenheit"),
        default="celsius",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Two-letter Google interface language.",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Use the bundled sample JSON and make no network request.",
    )
    parser.add_argument(
        "--sample-file",
        type=Path,
        default=DEFAULT_SAMPLE,
        help="JSON fixture used with --sample.",
    )
    parser.add_argument(
        "--show-raw",
        action="store_true",
        help="Also print the complete provider JSON after the brief summary.",
    )
    parser.add_argument(
        "--save-raw",
        type=Path,
        help="Save the complete provider JSON response to this path.",
    )
    return parser


def format_brief_weather(result: Mapping[str, Any]) -> str:
    location = result.get("location") or {}
    place = (
        location.get("resolved")
        or location.get("requested_city")
        or "Unknown place"
    )
    country = location.get("requested_country_code")
    if country and "," not in str(place):
        place = f"{place}, {country}"

    temperature = result.get("temperature") or {}
    value = temperature.get("value")
    unit = temperature.get("unit") or ""
    condition = result.get("condition") or "condition unknown"
    lines = [f"Now: {value}°{unit} in {place} ({condition})"]

    extras = [
        f"Humidity {result['humidity']}" if result.get("humidity") else "",
        f"Wind {result['wind']}" if result.get("wind") else "",
        f"Rain {result['precipitation']}" if result.get("precipitation") else "",
    ]
    extras = [item for item in extras if item]
    if extras:
        lines.append(" · ".join(extras))

    footer = []
    observed = result.get("observation_label")
    if observed:
        footer.append(f"Observed {observed}")
    today = result.get("today") or {}
    if today.get("high") is not None and today.get("low") is not None:
        today_unit = today.get("unit") or unit
        footer.append(f"Today {today['high']}°/{today['low']}°{today_unit}")
    if footer:
        lines.append(" · ".join(footer))
    return "\n".join(lines)


def main() -> None:
    apply_runtime_secrets(dotenv_paths=[PROJECT_DIR / ".env"])
    args = build_parser().parse_args()

    try:
        if args.sample:
            params = build_search_parameters(
                api_key="sample-key-not-used",
                city=args.city,
                country_code=args.country or None,
                units=args.units,
                language=args.language,
                no_cache=True,
            )
            print("[1] Build an ordinary HTTP GET request")
            print(f"    Endpoint: {SERPAPI_SEARCH_URL}")
            print(f"    Query: {params['q']}")
            print("[2] --sample selected: no network request is made")
            payload = load_sample_payload(args.sample_file)
        else:
            config = SerpApiConfig.from_environment()
            params = build_search_parameters(
                api_key=config.api_key,
                city=args.city,
                country_code=args.country or None,
                units=args.units,
                language=args.language,
                no_cache=config.no_cache,
            )
            print("[1] Build an ordinary HTTP GET request")
            print(f"    Endpoint: {SERPAPI_SEARCH_URL}")
            print(f"    Query: {params['q']}")
            print(
                f"[2] Application sends the request to SerpApi "
                f"(timeout={config.timeout_seconds:.0f}s, retries={config.retries})"
            )
            payload = perform_serpapi_search(
                params=params,
                timeout_seconds=config.timeout_seconds,
                retries=config.retries,
            )

        if args.save_raw:
            args.save_raw.parent.mkdir(parents=True, exist_ok=True)
            args.save_raw.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(f"    Saved raw response to: {args.save_raw}")

        print("[3] Current weather")
        result = normalize_serpapi_weather_result(
            payload=payload,
            requested_city=args.city,
            requested_country_code=args.country or None,
            requested_units=args.units,
            query=params["q"],
        )
        if args.sample:
            result["mock"] = True
            result["provider"] = "Bundled classroom sample — not live data"
        print(format_brief_weather(result))

        if args.show_raw:
            print()
            print("[4] Raw provider JSON")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
    except SerpApiWeatherError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc


if __name__ == "__main__":
    main()
