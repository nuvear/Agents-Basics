"""Rebuild the self-contained learner notebook from the classroom source files."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
cells = []
def md(text):
    cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': text.splitlines(True)})
def code(text, *, tags=None, collapsed=False):
    cells.append({'cell_type': 'code', 'execution_count': None, 'outputs': [],
                  'metadata': {'tags': tags or [], **({'cellView': 'form'} if collapsed else {})},
                  'source': text.splitlines(True)})

md('''# Weather agents and MCP · 2-hour Google Colab lab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb)

**Run one weather example three ways: direct API → function-calling agent → MCP agent.**

Use a standard hosted Python CPU runtime. No GPU, local Python installation, LM Studio or Drive mount is needed. OpenAI supplies model inference; Python and the local MCP server run inside your Colab runtime.

Before class: open this notebook using the **Open in Colab** badge, save your own copy, connect a runtime, and run the preparation cells. You can also upload a downloaded `.ipynb` through **File → Upload notebook** at [Google Colab](https://colab.research.google.com/). Keep your own saved notebook copy. This notebook embeds the required scripts and sample data; no ZIP extraction or repository download is needed.

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
''')
md('''## Preparation A · create the lab files
Run this collapsed setup cell once. It writes only the bundled workshop files into a dedicated runtime folder. Expand it to inspect the embedded sources, or open the generated files in Colab's Files panel. Runtime files are temporary; download any work you want to keep before the runtime is deleted.
''')
files = {p.name: p.read_text() for p in ROOT.glob('*.py')}
files.update({str(p.relative_to(ROOT)): p.read_text() for p in (ROOT/'examples').glob('*.json')})
files.update({str(p.relative_to(ROOT)): p.read_text() for p in (ROOT/'tests').glob('*.py')})
# Isolate dependencies from Colab's preinstalled packages.
files['requirements.txt'] = (ROOT/'requirements.txt').read_text()
code('# @title Create the bundled workshop files\nfrom pathlib import Path\nimport json, os, sys, subprocess\nLAB = Path("/content/mcp_weather_2hour") if Path("/content").exists() else Path.cwd() / "mcp_weather_2hour"\nLAB.mkdir(parents=True, exist_ok=True)\nFILES = '+repr(files)+'\nfor name, content in FILES.items():\n    target = LAB / name\n    target.parent.mkdir(parents=True, exist_ok=True)\n    target.write_text(content, encoding="utf-8")\nprint("Workshop files ready:", LAB)\n', tags=['bootstrap'], collapsed=True)
md('''## Preparation B · install dependencies
The lab uses its own Python environment so installation does not replace Colab's preinstalled packages. Allow a few minutes. Run this before the timed session.
''')
code('''ENV = LAB / ".venv"
if not (ENV / "bin/python").exists():
    # Colab images may omit ensurepip; virtualenv supplies its own seed packages.
    env_tools = LAB / "_env_tools"
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--target", str(env_tools), "virtualenv>=20,<21"], check=True)
    creation_env = dict(os.environ, PYTHONPATH=str(env_tools))
    subprocess.run([sys.executable, "-m", "virtualenv", str(ENV)], env=creation_env, check=True)
PYTHON = str(ENV / "bin/python")
subprocess.run([PYTHON, "-m", "pip", "install", "-q", "-r", str(LAB / "requirements.txt")], check=True)
print("Dependencies installed in the isolated lab environment.")
''', tags=['install'])
md('''## Preparation C · choose real inference or the offline fallback
In Colab's **Secrets** panel (key icon), add `OPENAI_API_KEY` and allow this notebook to access it. For optional live weather, add a separate `SERPAPI_KEY`. Never paste either key into a code cell or notebook output.

If Secrets is unavailable, the optional masked prompt below accepts the OpenAI key without displaying it. It is kept in this runtime's environment, not saved in the notebook source. Leave it blank to use the fallback.

OpenAI API usage requires available account quota. The OpenAI key does not authenticate SerpApi. No credentials are needed for sample data and the scripted fallback.
''')
code('''import getpass

def load_secret(name):
    try:
        from google.colab import userdata
        value = userdata.get(name)
    except Exception:
        value = os.environ.get(name, "")
    if value:
        os.environ[name] = value.strip()

for name in ("OPENAI_API_KEY", "SERPAPI_KEY"):
    load_secret(name)

USE_MASKED_PROMPT = False  # Set True only if you want to enter an OpenAI key now.
if USE_MASKED_PROMPT and not os.environ.get("OPENAI_API_KEY"):
    value = getpass.getpass("OpenAI API key (blank for offline): ").strip()
    if value:
        os.environ["OPENAI_API_KEY"] = value
    del value

USE_OPENAI = bool(os.environ.get("OPENAI_API_KEY"))
os.environ["MODEL_PROVIDER"] = "openai"
os.environ["OPENAI_MODEL"] = "gpt-4.1-mini"
print("Mode:", "OpenAI inference + sample weather" if USE_OPENAI else "Scripted model fallback + sample weather")
print("Weather credential:", "configured" if os.environ.get("SERPAPI_KEY") else "not configured (sample labs still work)")
''', tags=['credentials'])
md('''## Preparation D · command helper and readiness
All commands use the isolated interpreter. Scripts run as subprocesses to avoid notebook event-loop conflicts; the MCP server itself is another process in this same runtime. Do not pass credentials as command arguments.
''')
code('''def run_lab(script, *arguments):
    result = subprocess.run([PYTHON, str(LAB / script), *arguments], cwd=LAB, timeout=300)
    if result.returncode:
        raise RuntimeError("Lab command failed. Read the diagnostic above; check setup or use offline mode.")

def model_options():
    return ["--provider", "openai", "--mock-weather", "--force-tool"] if USE_OPENAI else ["--offline"]

run_lab("03_mcp_agent.py", "--inspect")
''', tags=['readiness'])
md('''## 0–10 · What makes this an agent?
A user asks: **What is the current temperature in Tokyo?**

Before running anything, identify what comes from the model and what must come from an external source. In this lesson, the agent is the application containing a model, tools, conversation state and a controlled execution loop.

**Your prediction:** Who requests the weather? Who executes the request? What evidence would you inspect?
''')
md('''## Lab 1 · Direct API (10–25)
Run the sample, identify the endpoint and query, then compare the raw weather result with the normalized fields. No model is involved. This sample command reads a fixture instead of sending HTTP.
''')
code('run_lab("01_direct_serpapi_api.py", "--sample", "--show-raw")\n', tags=['lab1'])
md('''Predict the Fahrenheit value for 21°C, then run. The fixture is fixed Tokyo demonstration data; changing a requested city does not fetch a new observation in sample mode.
''')
code('run_lab("01_direct_serpapi_api.py", "--sample", "--units", "fahrenheit")\n', tags=['lab1'])
md('''**Record:** endpoint, temperature/unit, location, observation label, source and sample marker.

**Explain:** Why is an ordinary API useful without a model? Locate `perform_serpapi_search` in the generated `serpapi_weather.py` to see where live HTTP would happen.
''')
md('''## Lab 2 · Function-calling agent (25–50)
The application advertises a JSON schema. The model returns a name and arguments; Python validates and executes the function, then sends the result back to the model with the matching call ID.

With an OpenAI key, this cell makes real model calls and uses sample weather. `--force-tool` means the host requires the first call; the model supplies the arguments. Without a key, it runs a fixed, clearly labelled scripted exercise and skips the generated final answer.
''')
code('run_lab("02_custom_tool_agent.py", *model_options())\n', tags=['lab2'])
md('''Read the contract and the short entry point. The larger shared loop lives in `agent_core.py`; inspect its `run_loop` function using the Files panel.
''')
code('''print((LAB / "weather_contract.py").read_text())
print((LAB / "02_custom_tool_agent.py").read_text())
''', tags=['source-tour'])
md('''**Record:** tool name, city/country/unit arguments, execution trace, result and sample label in the final answer. Explain why the schema itself does not execute code.

**Optional, within the time block:** set `RUN_UNFORCED=True` to see whether the real model chooses the tool without being required. A no-tool weather answer is withheld by this host.
''')
code('''RUN_UNFORCED = False
if RUN_UNFORCED and USE_OPENAI:
    run_lab("02_custom_tool_agent.py", "--provider", "openai", "--mock-weather")
else:
    print("Optional unforced inference skipped.")
''', tags=['optional'])
md('''## 50–55 · Break

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

The host and MCP server run in Colab. OpenAI receives the question, tool description and weather result. It does not connect directly to the stdio server.

- **Host:** owns conversation, model requests, validation and budgets.
- **Client:** the host's MCP connection to this server.
- **Server:** advertises the tool and executes its weather function.
- **Provider API:** remains underneath the server when using live weather.

MCP standardizes discovery and tool invocation; it does not replace the provider API or guarantee data quality. Here, the tool schema is discovered from the server. In Lab 2, the host defines it. Tools are our focus; MCP resources and prompts are later topics.

A standard hosted Colab runtime's `localhost` is not your laptop. The core class therefore uses OpenAI, while the existing LM Studio option remains a separate local-computer exercise.
''')
md('''## Lab 3 · Real MCP discovery and execution (70–100)
First read the small server and discover its schema. `--inspect` actually starts a server, initializes a session, lists tools and calls the weather tool with sample data. It needs no OpenAI key.
''')
code('''print((LAB / "weather_mcp_server.py").read_text())
run_lab("03_mcp_agent.py", "--inspect")
''', tags=['lab3'])
md('''Now connect the agent to that same server. Find `tools/list`, requested arguments, `tools/call` and the tool result in the trace. Compare these with Lab 2.
''')
code('run_lab("03_mcp_agent.py", *model_options())\n', tags=['lab3'])
md('''Fill this table in your own notebook:

| Responsibility | Function tool | MCP tool |
|---|---|---|
| Where does the schema come from? | | |
| Who manages model conversation? | | |
| Which process executes weather code? | | |
| Where is the weather key used? | | |

**Checkpoint:** the MCP session is real even if the model and weather are simulated. Record model inference as pending if you used the fallback.
''')
md('''## 100–113 · Pair challenge and failure exercise
With OpenAI, change the question to Lisbon in Fahrenheit. Confirm the model arguments and output units. The weather remains synthetic; it is not a location-specific observation. Without inference, use the direct sample unit-conversion exercise.
''')
code('''if USE_OPENAI:
    run_lab("03_mcp_agent.py", "What is the weather in Lisbon, Portugal in Fahrenheit?", *model_options())
else:
    run_lab("01_direct_serpapi_api.py", "--sample", "--units", "fahrenheit")
''', tags=['challenge'])
md('''Run the boundary tests. Find the invalid-unit test over real MCP and the test rejecting a model weather answer without tool execution. Identify the boundary responsible for each failure.
''')
code('''subprocess.run([PYTHON, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=LAB, check=True, timeout=180)
''', tags=['tests'])
md('''## Optional instructor demonstration · live weather
Keep this disabled during **Run all**. It uses SerpApi quota and, if enabled, OpenAI inference. Run only when the instructor has configured and rehearsed the keys. Failure to obtain a weather answer box is a legitimate result; never substitute a guessed temperature.

SerpApi returns Google's weather search data. Report the returned source and observation label; do not automatically call it AccuWeather or Weather.com. Retrieval time is not observation time.
''')
code('''RUN_LIVE_WEATHER = False
if RUN_LIVE_WEATHER:
    if not os.environ.get("SERPAPI_KEY"):
        raise RuntimeError("Configure SERPAPI_KEY in Colab Secrets and rerun the credential cell.")
    run_lab("01_direct_serpapi_api.py", "Tokyo", "--country", "JP")
    if USE_OPENAI:
        run_lab("03_mcp_agent.py", "--provider", "openai", "--force-tool")
else:
    print("Live weather disabled; no provider requests made by this cell.")
''', tags=['live-gated'])
md('''## 113–120 · Exit ticket
1. Does a structured tool request mean the API has already run?
2. What does MCP standardize, and what API work remains?
3. Which part changes when substituting the model backend?
4. How does sample weather with real inference differ from the scripted fallback?
5. What should the agent do when it gets no usable weather result?

**Completion record:** direct sample inspected ☐ · real model tool loop completed/pending ☐ · real MCP discovery/call inspected ☐ · sample/live distinction explained ☐.

Save your notebook before leaving. Notebook code, comments and output may be shared with its recipients, so do not include keys. Runtime resets require rerunning preparation. The local MCP child server exits when each lab invocation finishes.

### References and validation scope
- [Colab FAQ](https://research.google.com/colaboratory/faq.html)
- [Colab Secrets API source](https://github.com/googlecolab/colabtools/blob/main/google/colab/userdata.py)
- [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling)
- [MCP Python SDK v1](https://github.com/modelcontextprotocol/python-sdk/tree/v1.x)

The notebook is designed for hosted Colab. Local execution validates the embedded files and no-key exercises; it does not establish a hosted Colab run or live OpenAI/SerpApi success. Instructor rehearsal on Colab is required before class.
''')
for i, cell in enumerate(cells): cell['id'] = f'mcp-lab-{i:02d}'
notebook = {'nbformat': 4, 'nbformat_minor': 5,
            'metadata': {'colab': {'name': 'MCP_Weather_2Hour_Colab.ipynb', 'provenance': []},
                         'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                         'language_info': {'name': 'python'}}, 'cells': cells}
output = ROOT / 'colab/MCP_Weather_2Hour_Colab.ipynb'
output.write_text(json.dumps(notebook, indent=1, ensure_ascii=False)+'\n')
print(output)
