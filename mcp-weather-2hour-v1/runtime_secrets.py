"""Load workshop credentials for hosted Colab or a local runtime.

Hosted Colab (`/content` exists) prefers Google Secrets.
A local Jupyter / Mac runtime prefers already-set environment variables,
then a local `.env` file. The other source is always a fallback.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

SECRET_NAMES = ("OPENAI_API_KEY", "SERPAPI_KEY")
OPTIONAL_SETTINGS = (
    "MODEL_PROVIDER",
    "OPENAI_MODEL",
    "LM_STUDIO_MODEL",
    "LM_STUDIO_API_KEY",
    "LM_STUDIO_BASE_URL",
    "SERPAPI_TIMEOUT_SECONDS",
    "HTTP_TIMEOUT_SECONDS",
    "SERPAPI_RETRIES",
    "SERPAPI_NO_CACHE",
)
MISSING_OPENAI_KEY = (
    "Set OPENAI_API_KEY in Colab Secrets on hosted Colab, "
    "or in this package's .env on a local runtime, or use --offline."
)
MISSING_SERPAPI_KEY = (
    "SERPAPI_KEY is missing. Add it to Colab Secrets on hosted Colab, "
    "or copy .env.example to .env on a local runtime."
)


def is_hosted_colab() -> bool:
    return Path("/content").exists()


def locate_lab() -> Path:
    local_content = Path.home() / "colab-local-runtime" / "content"
    if Path("/content").exists():
        return Path("/content/mcp_weather_2hour")
    if local_content.exists():
        return local_content / "mcp_weather_2hour"
    return Path.cwd() / "mcp_weather_2hour"


def read_colab_secret(name: str) -> str:
    try:
        from google.colab import userdata
    except Exception:
        return ""
    try:
        value = userdata.get(name)
    except Exception:
        return ""
    if value is None:
        return ""
    return str(value).strip()


def parse_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        key = key.strip()
        if key and value:
            values[key] = value
    return values


def default_dotenv_paths(lab: Path | None = None) -> list[Path]:
    root = lab or locate_lab()
    home = Path.home()
    return [
        root / ".env",
        home / "colab-local-runtime" / "mcp_weather_2hour" / ".env",
        home / "colab-local-runtime" / "content" / "mcp_weather_2hour" / ".env",
        Path("/content/mcp_weather_2hour/.env"),
        Path.cwd() / "mcp_weather_2hour" / ".env",
        Path.cwd() / ".env",
    ]


def _read_dotenv_files(paths: Iterable[Path]) -> tuple[dict[str, str], Path | None]:
    merged: dict[str, str] = {}
    source: Path | None = None
    seen: set[Path] = set()
    for path in paths:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved in seen or not path.is_file():
            continue
        seen.add(resolved)
        try:
            parsed = parse_dotenv(path)
        except OSError:
            continue
        if not parsed:
            continue
        if source is None:
            source = path
        for key, value in parsed.items():
            merged.setdefault(key, value)
    return merged, source


def _set_if_empty(name: str, value: str) -> bool:
    value = value.strip()
    if not value:
        return False
    current = os.environ.get(name, "").strip()
    if current:
        return False
    os.environ[name] = value
    return True


def apply_runtime_secrets(
    *,
    dotenv_paths: Iterable[Path] | None = None,
    hosted: bool | None = None,
) -> dict[str, str]:
    """Populate process env from the source that matches this runtime.

    Returns a map of secret name → source label. Never prints secret values.
    """

    hosted_runtime = is_hosted_colab() if hosted is None else hosted
    file_values, _dotenv_path = _read_dotenv_files(
        dotenv_paths if dotenv_paths is not None else default_dotenv_paths()
    )
    dotenv_label = "local .env"
    sources: dict[str, str] = {}

    for name in SECRET_NAMES:
        if hosted_runtime:
            secret = read_colab_secret(name)
            if secret:
                os.environ[name] = secret
                sources[name] = "Colab Secrets"
                continue
            if os.environ.get(name, "").strip():
                sources[name] = "environment"
                continue
            if file_values.get(name) and _set_if_empty(name, file_values[name]):
                sources[name] = dotenv_label
                continue
            sources[name] = "missing"
            continue

        if os.environ.get(name, "").strip():
            sources[name] = "environment"
            continue
        if file_values.get(name) and _set_if_empty(name, file_values[name]):
            sources[name] = dotenv_label
            continue
        secret = read_colab_secret(name)
        if secret and _set_if_empty(name, secret):
            sources[name] = "Colab Secrets"
            continue
        sources[name] = "missing"

    for name in OPTIONAL_SETTINGS:
        value = file_values.get(name, "")
        if value:
            _set_if_empty(name, value)

    return sources


def report_runtime_credentials(sources: dict[str, str]) -> dict[str, bool]:
    use_openai = bool(os.environ.get("OPENAI_API_KEY", "").strip())
    have_serpapi = bool(os.environ.get("SERPAPI_KEY", "").strip())
    os.environ.setdefault("MODEL_PROVIDER", "openai")
    os.environ.setdefault("OPENAI_MODEL", "gpt-4.1-mini")

    print("=== Runtime credentials ===")
    print(
        f"Runtime:         "
        f"{'hosted Colab (Google Secrets first)' if is_hosted_colab() else 'local ( .env first)'}"
    )
    print(
        f"OpenAI API key:  {'found' if use_openai else 'not found'}  "
        f"({sources.get('OPENAI_API_KEY', 'missing')})"
    )
    print(
        f"SerpApi key:     {'found' if have_serpapi else 'not found'}  "
        f"({sources.get('SERPAPI_KEY', 'missing')})"
    )
    print()
    print("=== What the next labs will do ===")
    if use_openai:
        print("Model:   live OpenAI call  (provider=openai, model=gpt-4.1-mini)")
    else:
        print("Model:   offline script  (no OpenAI call; fixed Tokyo teaching turns)")
    if have_serpapi:
        print("Weather: live SerpApi request  (current conditions)")
    else:
        print("Weather: sample/mock only  (no live SerpApi request without SERPAPI_KEY)")
    print()
    if use_openai and have_serpapi:
        print("Summary: OpenAI inference + live weather")
    elif use_openai:
        print("Summary: OpenAI inference + sample weather")
    elif have_serpapi:
        print("Summary: scripted model fallback + live weather")
    else:
        print("Summary: scripted model fallback + sample weather")
    return {"USE_OPENAI": use_openai, "HAVE_SERPAPI": have_serpapi}


def has_openai_key() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY", "").strip())


def has_serpapi_key() -> bool:
    return bool(os.environ.get("SERPAPI_KEY", "").strip())


def should_mock_weather(*, mock_weather: bool = False, offline: bool = False, inspect: bool = False) -> bool:
    """Use labelled sample weather unless a live SerpApi key is available."""

    if mock_weather or offline or inspect:
        return True
    return not has_serpapi_key()


def lab_run_options(*, force_tool: bool = True) -> list[str]:
    """CLI flags for Lab 2/3 based on keys found in this runtime."""

    options: list[str] = []
    if has_openai_key():
        options.extend(["--provider", "openai"])
        if force_tool:
            options.append("--force-tool")
    else:
        options.append("--offline")
    if should_mock_weather():
        if "--offline" not in options:
            options.append("--mock-weather")
        print("[LAB OPTIONS] Weather will use labelled sample data.")
    else:
        print("[LAB OPTIONS] Weather will use a live SerpApi request.")
    print("[LAB OPTIONS]", " ".join(options) or "(defaults)")
    return options
