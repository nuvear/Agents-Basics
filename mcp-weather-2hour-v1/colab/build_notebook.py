"""Rebuild the learner notebook from the classroom source files."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
cells = []


def md(text):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": text.splitlines(True)})


def code(text, *, tags=None, collapsed=False):
    cells.append(
        {
            "cell_type": "code",
            "execution_count": None,
            "outputs": [],
            "metadata": {
                "tags": tags or [],
                **({"cellView": "form"} if collapsed else {}),
            },
            "source": text.splitlines(True),
        }
    )


md("""# Weather agents and MCP · 2-hour Google Colab lab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb)

**Run one weather example three ways: direct API → function-calling agent → MCP agent.**

This notebook works on a **hosted Colab runtime** and on a **local Colab runtime**. No GPU or Drive mount is needed. OpenAI supplies model inference when a key is present; Python and the MCP server run inside the connected runtime.

- **Hosted Colab:** Preparation A clones this GitHub repo into `/content/mcp_weather_2hour`. Put `OPENAI_API_KEY` and optional `SERPAPI_KEY` in Colab Secrets.
- **Local runtime:** Preparation A uses the workshop files already on this Mac. Keys come from the package `.env`.

Before class: open the notebook with the badge, save your own copy, connect a runtime, and run Preparation A–D.

| Time | Activity |
|---|---|
| 0–10 | Weather problem; model versus agent |
| 10–25 | Lab 1: direct API |
| 25–50 | Lab 2: function calling |
| 50–55 | Break |
| 55–70 | MCP host, client and server |
| 70–100 | Lab 3: discovery and execution |
| 100–113 | Pair challenge and failure exercise |
| 113–120 | Exit ticket |

**Evidence rule:** a tool request is not execution. A sample value is not live weather. Record what actually ran.
""")

md("""## Preparation A · create the lab files
Run this cell once. On a local Mac it locates the workshop folder. On hosted Colab it downloads the same files from [nuvear/Agents-Basics](https://github.com/nuvear/Agents-Basics). Runtime files are temporary; download any work you want to keep before the runtime is deleted.
""")

code(
    r'''# @title Create / locate the bundled workshop files
from pathlib import Path
from zipfile import ZipFile
import shutil
import subprocess
import urllib.request

REPO_URL = "https://github.com/nuvear/Agents-Basics.git"
REPO_ZIP_URL = "https://github.com/nuvear/Agents-Basics/archive/refs/heads/main.zip"
REPO_LAB_DIR = "mcp-weather-2hour-v1"

WORKSHOP_FILES = [
    "01_direct_serpapi_api.py",
    "02_custom_tool_agent.py",
    "03_mcp_agent.py",
    "agent_core.py",
    "serpapi_weather.py",
    "weather_contract.py",
    "weather_mcp_server.py",
    "runtime_secrets.py",
    "requirements.txt",
    ".env.example",
    "examples/weather_answer_box_sample.json",
    "tests/test_serpapi_weather.py",
    "tests/test_training.py",
    "tests/test_runtime_secrets.py",
]

SKIP_PARTS = {".venv", "__pycache__", ".git"}
SKIP_NAMES = {".env"}

LOCAL_CONTENT = Path.home() / "colab-local-runtime" / "content"
HOSTED = Path("/content").exists()

if HOSTED:
    LAB = Path("/content/mcp_weather_2hour")
    CACHE = Path("/content/Agents-Basics")
    runtime_kind = "hosted Colab (/content)"
elif LOCAL_CONTENT.exists():
    LAB = LOCAL_CONTENT / "mcp_weather_2hour"
    CACHE = Path.home() / "colab-local-runtime" / "Agents-Basics"
    runtime_kind = "local Mac"
else:
    LAB = Path.cwd() / "mcp_weather_2hour"
    CACHE = Path.cwd() / "Agents-Basics"
    runtime_kind = "current working directory"

LAB.mkdir(parents=True, exist_ok=True)


def missing_workshop_files():
    return [name for name in WORKSHOP_FILES if not (LAB / name).is_file()]


def copy_repo_lab(source: Path) -> None:
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        if SKIP_PARTS.intersection(path.parts):
            continue
        if path.name in SKIP_NAMES:
            continue
        dest = LAB / path.relative_to(source)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)


def fetch_from_git_clone() -> Path | None:
    source = CACHE / REPO_LAB_DIR
    if (source / "01_direct_serpapi_api.py").is_file():
        return source
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    if CACHE.exists():
        shutil.rmtree(CACHE)
    result = subprocess.run(
        ["git", "clone", "--depth", "1", REPO_URL, str(CACHE)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr or result.stdout)
        return None
    return source if (source / "01_direct_serpapi_api.py").is_file() else None


def fetch_from_github_zip() -> Path | None:
    zip_path = (Path("/content") if HOSTED else Path.cwd()) / "Agents-Basics-main.zip"
    print("Downloading workshop zip from GitHub:")
    print(f"  {REPO_ZIP_URL}")
    urllib.request.urlretrieve(REPO_ZIP_URL, zip_path)
    extracted = zip_path.parent / "Agents-Basics-main"
    if extracted.exists():
        shutil.rmtree(extracted)
    with ZipFile(zip_path) as archive:
        archive.extractall(zip_path.parent)
    source = extracted / REPO_LAB_DIR
    return source if (source / "01_direct_serpapi_api.py").is_file() else None


source_label = None
missing = missing_workshop_files()

if missing:
    print("Workshop files are missing; loading them from the git repo.")
    source = fetch_from_git_clone()
    if source is not None:
        source_label = f"git clone {REPO_URL}"
    else:
        source = fetch_from_github_zip()
        source_label = f"GitHub zip {REPO_ZIP_URL}"
    if source is None:
        raise FileNotFoundError(
            "Could not load the workshop from GitHub. "
            f"Check access to {REPO_URL}"
        )
    copy_repo_lab(source)
    missing = missing_workshop_files()

print("=== Preparation A ===")
print(f"Runtime:    {runtime_kind}")
print(f"LAB folder: {LAB}")
if source_label:
    print(f"Loaded:     {source_label}")
print()
print("Workshop files:")
for name in WORKSHOP_FILES:
    status = "ready  " if (LAB / name).is_file() else "MISSING"
    print(f"  {status} {name}")

print()
if missing:
    raise FileNotFoundError(
        "Workshop files are still missing after loading from GitHub. "
        f"Missing: {', '.join(missing)}"
    )
print("Workshop files ready.")
print("Lab 1 script:", LAB / "01_direct_serpapi_api.py")
''',
    tags=["bootstrap"],
    collapsed=True,
)

md("""## Preparation B · install dependencies
The lab uses its own Python environment so installation does not replace Colab's preinstalled packages. Allow a few minutes. Hosted Colab often lacks `ensurepip`, so this cell falls back to `virtualenv`.
""")

code(
    '''# @title Install lab dependencies (hosted Colab or local runtime)
import os
import shutil
import subprocess
import sys

ENV = LAB / ".venv"
PYTHON = ENV / "bin" / "python"


def run(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def lab_python_ready() -> bool:
    return PYTHON.is_file() and run([str(PYTHON), "-c", "import sys"]).returncode == 0


def create_with_venv() -> bool:
    result = run([sys.executable, "-m", "venv", str(ENV)])
    return result.returncode == 0 and lab_python_ready()


def create_with_virtualenv() -> tuple[bool, str]:
    env_tools = LAB / "_env_tools"
    install = run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-q",
            "--target",
            str(env_tools),
            "virtualenv>=20,<21",
        ]
    )
    if install.returncode != 0:
        return False, install.stderr or install.stdout
    creation_env = dict(os.environ)
    existing = creation_env.get("PYTHONPATH", "")
    creation_env["PYTHONPATH"] = (
        str(env_tools) if not existing else f"{env_tools}{os.pathsep}{existing}"
    )
    result = run([sys.executable, "-m", "virtualenv", str(ENV)], env=creation_env)
    return result.returncode == 0 and lab_python_ready(), result.stderr or result.stdout


if not lab_python_ready():
    if ENV.exists():
        shutil.rmtree(ENV, ignore_errors=True)
    if create_with_venv():
        print("Created isolated lab environment with stdlib venv.")
    else:
        if ENV.exists():
            shutil.rmtree(ENV, ignore_errors=True)
        ok, detail = create_with_virtualenv()
        if not ok:
            raise RuntimeError(
                "Could not create a lab virtualenv on this runtime. "
                "Hosted Colab often lacks ensurepip for `python -m venv`. "
                f"virtualenv fallback failed:\\n{detail}"
            )
        print("Created isolated lab environment with virtualenv.")
        print("(Hosted Colab's stdlib venv is missing ensurepip.)")
else:
    print("Lab virtual environment already exists.")

if run([str(PYTHON), "-m", "pip", "--version"]).returncode == 0:
    subprocess.run(
        [str(PYTHON), "-m", "pip", "install", "-q", "-r", str(LAB / "requirements.txt")],
        check=True,
    )
else:
    subprocess.run(
        ["uv", "pip", "install", "--python", str(PYTHON), "-r", str(LAB / "requirements.txt")],
        check=True,
    )

print("Dependencies installed in the isolated lab environment.")
print("Lab Python:", PYTHON)
''',
    tags=["install"],
)

md("""## Preparation C · choose real inference or the offline fallback
On **hosted Colab**, add `OPENAI_API_KEY` in Secrets and allow this notebook to access it. Add `SERPAPI_KEY` for live weather.

On a **local runtime**, keys come from the workshop `.env`. Never paste either key into a code cell or notebook output.

If Secrets is unavailable, the optional masked prompt accepts the OpenAI key without displaying it. Leave it blank to use the scripted fallback.

The OpenAI key does not authenticate SerpApi. Labs 2 and 3 use live weather only when `SERPAPI_KEY` is present; otherwise they use labelled sample data.
""")

code(
    '''# @title Load runtime credentials (Colab Secrets or local .env)
import getpass
import importlib.util
import os
from pathlib import Path

def _load_runtime_secrets_module():
    candidates = [
        LAB / "runtime_secrets.py",
        Path("/content/mcp_weather_2hour/runtime_secrets.py"),
        Path.home() / "colab-local-runtime" / "content" / "mcp_weather_2hour" / "runtime_secrets.py",
        Path.home() / "colab-local-runtime" / "mcp_weather_2hour" / "runtime_secrets.py",
        Path.cwd() / "mcp_weather_2hour" / "runtime_secrets.py",
        Path.cwd() / "runtime_secrets.py",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        spec = importlib.util.spec_from_file_location("runtime_secrets", path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    raise FileNotFoundError(
        "runtime_secrets.py was not found. Run the Preparation A cell first."
    )

runtime_secrets = _load_runtime_secrets_module()
secret_sources = runtime_secrets.apply_runtime_secrets()

USE_MASKED_PROMPT = False  # Set True only if you want to enter an OpenAI key now.
if USE_MASKED_PROMPT and not os.environ.get("OPENAI_API_KEY"):
    value = getpass.getpass("OpenAI API key (blank for offline): ").strip()
    if value:
        os.environ["OPENAI_API_KEY"] = value
        secret_sources["OPENAI_API_KEY"] = "typed in this cell"
    del value

flags = runtime_secrets.report_runtime_credentials(secret_sources)
USE_OPENAI = flags["USE_OPENAI"]
HAVE_SERPAPI = flags["HAVE_SERPAPI"]
''',
    tags=["credentials"],
)

md("""## Preparation D · command helper and readiness
All commands use the isolated interpreter. Scripts run as subprocesses to avoid notebook event-loop conflicts. `model_options()` chooses OpenAI vs offline and live vs sample weather from the keys found in this runtime.
""")

code(
    '''# @title Command helper and MCP readiness check
import ast
import json
import re
import sys

sys.path.insert(0, str(LAB))
from runtime_secrets import lab_run_options


def _as_pretty_json(value):
    if isinstance(value, dict):
        content = value.get("content")
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    try:
                        item["text"] = json.loads(item["text"])
                    except json.JSONDecodeError:
                        pass
    return json.dumps(value, indent=2, ensure_ascii=False)


def _pretty_line(line):
    text = line.rstrip()
    if not text:
        return text

    tag, rest = "", text
    matched = re.match(r"^(\\[[^\\]]+\\])\\s*(.*)$", text)
    if matched:
        tag, rest = matched.group(1), matched.group(2)
        if not rest:
            return tag

    for loader in (ast.literal_eval, json.loads):
        try:
            parsed = loader(rest)
        except (ValueError, SyntaxError, json.JSONDecodeError):
            continue
        if isinstance(parsed, (dict, list, tuple)):
            body = _as_pretty_json(parsed)
            return f"{tag}\\n{body}" if tag else body
    return text


def _pretty_text(blob):
    return "\\n".join(_pretty_line(line) for line in (blob or "").splitlines())


def run_lab(script, *arguments):
    result = subprocess.run(
        [str(PYTHON), str(LAB / script), *arguments],
        cwd=LAB,
        timeout=300,
        capture_output=True,
        text=True,
    )
    print(f"=== {script} {' '.join(arguments)} ===")
    pretty = _pretty_text(result.stdout)
    if pretty:
        print(pretty)
    noise = {
        "Processing request of type ListToolsRequest",
        "Processing request of type CallToolRequest",
    }
    extras = [
        line for line in (result.stderr or "").splitlines()
        if line.strip() and line.strip() not in noise
    ]
    if extras:
        print("\\n--- diagnostics ---")
        print("\\n".join(extras))
    if result.returncode:
        raise RuntimeError(
            "Lab command failed. Read the diagnostic above; "
            "check setup or use offline mode."
        )


def model_options(*, force_tool=True):
    return lab_run_options(force_tool=force_tool)


run_lab("03_mcp_agent.py", "--inspect")
''',
    tags=["readiness"],
)

md("""## 0–10 · What makes this an agent?
A user asks: **What is the current temperature in Tokyo?**

Before running anything, identify what comes from the model and what must come from an external source. In this lesson, the agent is the application containing a model, tools, conversation state and a controlled execution loop.

**Your prediction:** Who requests the weather? Who executes the request? What evidence would you inspect?
""")

md("""## Lab 1 · Direct API (10–25)
Run the sample first. It reads a fixture and makes no HTTP request. If `SERPAPI_KEY` is present, the next cells fetch current weather, including Singapore.
""")

code(
    '''print("=== Lab 1 · sample (no network) ===")
run_lab("01_direct_serpapi_api.py", "--sample")

if HAVE_SERPAPI:
    print("=== Lab 1 · live SerpApi (Tokyo) ===")
    run_lab("01_direct_serpapi_api.py")
    print("=== Lab 1 · Singapore temperature ===")
    run_lab("01_direct_serpapi_api.py", "Singapore", "--country", "SG")
else:
    print("Live Lab 1 skipped. Add SERPAPI_KEY and rerun Preparation C.")
''',
    tags=["lab1"],
)

md("""Predict the Fahrenheit value for 21°C, then run. The fixture is fixed Tokyo demonstration data; changing a requested city does not fetch a new observation in sample mode.
""")

code(
    '''print("=== Lab 1 · same fixture in Fahrenheit (predict 69.8°F) ===")
run_lab("01_direct_serpapi_api.py", "--sample", "--units", "fahrenheit")

if HAVE_SERPAPI:
    print("=== Lab 1 · current temperature in Fahrenheit ===")
    try:
        run_lab("01_direct_serpapi_api.py", "--units", "fahrenheit")
    except RuntimeError:
        print(
            "Live Fahrenheit request did not return a weather answer box. "
            "That is a Google/SerpApi result, not a conversion bug. "
            "The sample above already shows 21°C → 69.8°F."
        )
else:
    print("Live Fahrenheit request skipped; no SERPAPI_KEY.")
''',
    tags=["lab1"],
)

md("""**Record:** endpoint, temperature/unit, location, observation label, source and sample marker.

**Explain:** Why is an ordinary API useful without a model? Locate `perform_serpapi_search` in `serpapi_weather.py` to see where live HTTP would happen.
""")

md("""## Lab 2 · Function-calling agent (25–50)
The application advertises a JSON schema. The model returns a name and arguments; Python validates and executes the function, then sends the result back to the model with the matching call ID.

With an OpenAI key this cell makes a real model call. Weather is live when `SERPAPI_KEY` is present, otherwise labelled sample data. `--force-tool` means the host requires the first call; the model supplies the arguments. Without an OpenAI key, it runs a fixed scripted exercise and skips the generated final answer.
""")

code(
    '''print("=== Lab 2 · Function-calling agent ===")
run_lab("02_custom_tool_agent.py", *model_options())

print("=== Lab 2 · Singapore temperature ===")
run_lab(
    "02_custom_tool_agent.py",
    "What is the current weather in Singapore in Celsius?",
    *model_options(),
)
''',
    tags=["lab2"],
)

md("""Read the contract and the short entry point. The larger shared loop lives in `agent_core.py`; inspect its `run_loop` function using the Files panel.
""")

code(
    '''print((LAB / "weather_contract.py").read_text())
print((LAB / "02_custom_tool_agent.py").read_text())
''',
    tags=["source-tour"],
)

md("""**Record:** tool name, city/country/unit arguments, execution trace, result and sample or live label in the final answer. Explain why the schema itself does not execute code.

**Optional, within the time block:** set `RUN_UNFORCED=True` to see whether the real model chooses the tool without being required. A no-tool weather answer is withheld by this host.
""")

code(
    '''RUN_UNFORCED = False
if RUN_UNFORCED and USE_OPENAI:
    run_lab("02_custom_tool_agent.py", *model_options(force_tool=False))
else:
    print("Optional unforced inference skipped.")
''',
    tags=["optional"],
)

md("""## 50–55 · Break

## 55–70 · What MCP changes

```text
Student → Python host ↔ OpenAI model service
                 │
          MCP client (inside host)
                 │ initialize / tools/list / tools/call
                 ▼
          Weather MCP server process
                 │
                 └→ SerpApi Google Search API (live mode only)
```

The host and MCP server run in the connected Colab runtime. OpenAI receives the question, tool description and weather result. It does not connect directly to the stdio server.

- **Host:** owns conversation, model requests, validation and budgets.
- **Client:** the host's MCP connection to this server.
- **Server:** advertises the tool and executes its weather function.
- **Provider API:** remains underneath the server when using live weather.

MCP standardizes discovery and tool invocation; it does not replace the provider API or guarantee data quality. Here, the tool schema is discovered from the server. In Lab 2, the host defines it.

A hosted Colab runtime's `localhost` is not your laptop. The core class therefore uses OpenAI. LM Studio remains a separate local-computer exercise.
""")

md("""## Lab 3 · Real MCP discovery and execution (70–100)
First read the small server. `--inspect` starts it, lists tools and makes a **sample** weather call. That needs no OpenAI key and no SerpApi key. The next cell uses the same MCP server with the keys found in this runtime: live weather when `SERPAPI_KEY` is present, otherwise labelled sample data — the same rule as Labs 1 and 2.
""")

code(
    '''print((LAB / "weather_mcp_server.py").read_text())
print("=== Lab 3 · MCP inspect (sample, no model) ===")
run_lab("03_mcp_agent.py", "--inspect")
''',
    tags=["lab3"],
)

md("""Now connect the agent to that same server. Find `tools/list`, requested arguments, `tools/call` and the tool result in the trace. Compare these with Lab 2. Weather is live only when `SERPAPI_KEY` is present.
""")

code(
    '''print("=== Lab 3 · MCP agent ===")
run_lab("03_mcp_agent.py", *model_options())

print("=== Lab 3 · Singapore temperature ===")
run_lab(
    "03_mcp_agent.py",
    "What is the current weather in Singapore in Celsius?",
    *model_options(),
)
''',
    tags=["lab3"],
)

md("""Fill this table in your own notebook:

| Responsibility | Function tool | MCP tool |
|---|---|---|
| Where does the schema come from? | | |
| Who manages model conversation? | | |
| Which process executes weather code? | | |
| Where is the weather key used? | | |

**Checkpoint:** the MCP session is real even if the model is offline or weather is sample data. Record model inference as pending if you used the fallback. Record weather as live only when the trace says `live SerpApi`.
""")

md("""## 100–113 · Pair challenge and failure exercise
With OpenAI, change the question to Lisbon in Fahrenheit. Confirm the model arguments and output units. Weather is live only when `SERPAPI_KEY` is present. Without inference, use the direct sample unit-conversion exercise.
""")

code(
    '''if USE_OPENAI:
    run_lab(
        "03_mcp_agent.py",
        "What is the weather in Lisbon, Portugal in Fahrenheit?",
        *model_options(),
    )
else:
    run_lab("01_direct_serpapi_api.py", "--sample", "--units", "fahrenheit")
''',
    tags=["challenge"],
)

md("""Run the boundary tests. Find the invalid-unit test over real MCP and the test rejecting a model weather answer without tool execution. Identify the boundary responsible for each failure.
""")

code(
    '''subprocess.run([str(PYTHON), "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=LAB, check=True, timeout=180)
''',
    tags=["tests"],
)

md("""## Optional instructor demonstration · live weather
Lab 1–3 already use live SerpApi when `SERPAPI_KEY` is present. Keep this extra cell disabled during **Run all** if you want a second, explicit live demonstration. Failure to obtain a weather answer box is a legitimate result; never substitute a guessed temperature.

SerpApi returns Google's weather search data. Report the returned source and observation label. Retrieval time is not observation time.
""")

code(
    '''RUN_LIVE_WEATHER = False
if RUN_LIVE_WEATHER:
    if not HAVE_SERPAPI:
        raise RuntimeError("Add SERPAPI_KEY and rerun Preparation C.")
    run_lab("01_direct_serpapi_api.py", "Tokyo", "--country", "JP")
    if USE_OPENAI:
        run_lab("03_mcp_agent.py", *model_options())
else:
    print("Extra live-weather demonstration disabled.")
''',
    tags=["live-gated"],
)

md("""## 113–120 · Exit ticket
1. Does a structured tool request mean the API has already run?
2. What does MCP standardize, and what API work remains?
3. Which part changes when substituting the model backend?
4. How does sample weather with real inference differ from the scripted fallback?
5. What should the agent do when it gets no usable weather result?

**Completion record:** direct sample inspected ☐ · real model tool loop completed/pending ☐ · real MCP discovery/call inspected ☐ · sample/live distinction explained ☐.

Save your notebook before leaving. Do not include keys in notebook source or output. Runtime resets require rerunning preparation.

### References
- [Colab FAQ](https://research.google.com/colaboratory/faq.html)
- [Colab Secrets API source](https://github.com/googlecolab/colabtools/blob/main/google/colab/userdata.py)
- [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling)
- [MCP Python SDK v1](https://github.com/modelcontextprotocol/python-sdk/tree/v1.x)

The notebook supports hosted Colab and a local Colab runtime. Instructor rehearsal of Secrets, OpenAI and SerpApi is still required before class.
""")

for i, cell in enumerate(cells):
    cell["id"] = f"mcp-lab-{i:02d}"

notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "colab": {"name": "MCP_Weather_2Hour_Colab.ipynb", "provenance": []},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "cells": cells,
}
output = ROOT / "colab/MCP_Weather_2Hour_Colab.ipynb"
output.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")
print(output)
