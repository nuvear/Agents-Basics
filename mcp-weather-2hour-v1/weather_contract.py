"""The direct function's contract and implementation boundary."""
import json
import os
from jsonschema import validate, ValidationError
from serpapi_weather import get_current_weather

PARAMETERS = {
    "type": "object",
    "properties": {
        "city": {"type": "string", "minLength": 1},
        "country_code": {"type": "string", "pattern": "^[A-Za-z]{2}$"},
        "units": {"type": "string", "enum": ["celsius", "fahrenheit"]},
    },
    "required": ["city", "country_code", "units"],
    "additionalProperties": False,
}
TOOL = {"type": "function", "function": {
    "name": "get_current_weather",
    "description": "Get current weather for a city and country. Never guess live conditions.",
    "parameters": PARAMETERS,
}}

def scrub(value):
    """Remove known credentials before tool results reach a model or trace."""
    text = json.dumps(value, ensure_ascii=False)
    for name in ("SERPAPI_KEY", "OPENAI_API_KEY", "LM_STUDIO_API_KEY"):
        secret = os.getenv(name, "")
        if secret:
            text = text.replace(json.dumps(secret)[1:-1], "[REDACTED]")
    return json.loads(text)

def execute_weather(arguments, *, mock):
    try:
        validate(arguments, PARAMETERS)
    except ValidationError:
        return {"ok": False, "error": "Expected city, two-letter country_code, and celsius/fahrenheit; no extra fields."}
    return scrub(get_current_weather(**arguments, mock=mock))
