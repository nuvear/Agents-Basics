# Facilitator run sheet — 120 minutes

**Delivery platform: Google Colab.** Give students [the self-contained notebook](colab/MCP_Weather_2Hour_Colab.ipynb) and complete its preparation cells before class. Keep the timings and questions below; run the corresponding notebook cells instead of terminal commands. OpenAI is the model backend for the hosted class. Use the notebook as the student workbook; LM Studio is an optional local-computer extension. See [Colab instructions](colab/README.md).

Use [SETUP.md](SETUP.md) before class. Rehearse the selected model with sample weather and keep an offline fallback ready. Pair students if any model setup is incomplete. Do not spend class time downloading models or opening billing accounts.

## 0–10 — Begin with the problem

Ask: “What is the current temperature in Tokyo? What would count as evidence?” Show the supplied jar image if useful. Explain that model training is not a live weather feed. Define an agent here as an application combining a model, tools, conversation state and a controlled execution loop.

Spend 3 minutes on the question, 4 on the actors and 3 on prediction. Students write who can actually fetch data. Show the three-stage path. Avoid introducing every MCP capability yet.

## 10–25 — Lab 1: ordinary API

- 10–13: explain endpoint, GET parameters, key and JSON response.
- 13–18: students run `python 01_direct_serpapi_api.py --sample --show-raw`.
- 18–22: change to `--units fahrenheit`; locate normalized temperature and source.
- 22–25: ask which line makes the network request in live mode and why no model is needed.

Code stops: `build_search_parameters`, `perform_serpapi_search`, `normalize_serpapi_weather_result`. Do not read the whole adapter. With `--sample`, the fixed fixture stays the same even if the requested city changes. Use Tokyo in this exercise.

Checkpoint: students identify the returned weather data, unit, source, observation label and sample flag. A bundled fixture is not live HTTP evidence. If prepared, show one live instructor call within this block.

## 25–50 — Lab 2: turn the function into a model tool

- 25–30: use the second supplied image. The schema describes a function; it is not executable code.
- 30–35: open `weather_contract.py`, then the small `02_custom_tool_agent.py` entry point.
- 35–43: students run the chosen backend with `--mock-weather --force-tool`.
- 43–47: point to the model's name/arguments, dispatch, tool result and matching `tool_call_id` in `agent_core.py`.
- 47–50: students explain the loop to a partner. If time permits rerun without `--force-tool` and compare.

Command: `python 02_custom_tool_agent.py --provider openai --mock-weather --force-tool`, or replace `openai` with `lmstudio`.

Fallback: `python 02_custom_tool_agent.py --offline`. Say explicitly that the model turns are scripted. Do not count this as a successful model-inference exercise.

Checkpoint: a learner explains “the model requests; Python executes; the result returns to the model.” For the forced run, the host required tool use while the model supplied the arguments.

## 50–55 — Break

Leave the three-stage path visible. Resume on time.

## 55–70 — MCP concepts

Use the README sequence diagram. Spend 5 minutes mapping roles, 5 tracing discovery/call/result and 5 comparing the two implementations.

- Host: the overall Python application, managing conversation, model access and policy.
- Client: the MCP connection inside that host, talking to one server.
- Server: a separate local process advertising and executing the weather tool.
- Provider: the external weather search API under the server in live mode.

Explain stdio as communication through the child process's standard input/output. It is local interprocess communication, not an HTTP URL. MCP can also use network transports, beyond this core lab.

Ask: “Where did the provider code go?” Answer: into the server boundary; it did not disappear. “Does OpenAI need to reach localhost?” Answer: no; our host exchanges model messages with OpenAI and runs the MCP connection locally.

## 70–100 — Lab 3: real MCP

- 70–75: open `weather_mcp_server.py`; identify the tool decorator, typed arguments and function call. Explain why stdout is reserved for protocol messages.
- 75–82: run `python 03_mcp_agent.py --inspect`. Identify the discovered schema and the sample tool result. No model and no live weather.
- 82–90: run the notebook Lab 3 agent cell. It uses live SerpApi when `SERPAPI_KEY` is present, otherwise labelled sample weather — the same rule as Labs 1 and 2. Then run the Singapore question.
- 90–95: open `03_mcp_agent.py`; locate `initialize`, `list_tools` and `call_tool`. Point to `[WEATHER SOURCE]`.
- 95–100: pairs fill the responsibility table in the workbook. Ask what stayed constant.

Fallback: `python 03_mcp_agent.py --offline`. The SDK still launches the server and performs protocol calls; only the model and weather data are simulated. The trace is execution evidence for local MCP, not external service availability.

Checkpoint: each pair points to `tools/list` and `tools/call`, and names the process executing the weather adapter. If a student's setup is broken, have them observe their partner and annotate the evidence rather than spend the rest of class reinstalling.

## 100–113 — Pair challenge

Use 5 minutes for a variation, 5 for failure and 3 for explanation.

Variation with a real model: ask for Lisbon, Portugal in Fahrenheit using the Lab 3 agent cell. If `SERPAPI_KEY` is present the weather is live; otherwise it is labelled sample data and 21°C/69.8°F is not a location-specific observation. Compare request arguments to result fields.

Variation without a model: change the direct sample to Fahrenheit and predict 69.8°F before running it.

Failure exercise: run `python -m unittest discover -s tests -p test_training.py -v`. Locate the test for invalid units over real MCP, then the test withholding model text when no tool ran. Students identify which boundary rejects each failure. No source edits or real credentials are needed.

Ask: “If we choose OpenAI instead of LM Studio, do we rewrite the weather server?” Expected: no; the model connection settings change. “Does MCP ensure the final number is accurate?” Expected: no; compare model prose with tool result, location, units and time/source evidence.

## 113–120 — Assessment

Give 4 minutes for the five exit questions in the workbook and 3 minutes for debrief. Four correct answers is the conceptual completion target; the request-versus-execution answer must be correct. Record practical completion separately: direct sample, real model tool loop, actual MCP call.

If a learner used only offline mode, mark “protocol/control-flow complete; model integration pending.” Do not describe that as a fully live agent.

## What to omit if running late

Keep MCP discovery/execution and the exit assessment. Omit optional live weather, the second unforced model run and the provider-hosted extension. Preserve at least 20 minutes for the MCP lab. If installation consumes more than 5 minutes, switch the affected student to a partner demonstration.

## Answer key

1. A model tool call is a structured request. The host validates and dispatches it; the function/server executes it.
2. MCP supplies a standard host/client/server interaction for discovery and calls; the provider API remains underneath.
3. Model provider, URL, key and model ID change; weather tool/server stay the same.
4. Weather must be labelled sample. `--mock-weather` still makes a model request; `--offline` uses scripted model turns.
5. Explain the unavailable data, check location/query or setup as appropriate, and do not invent a weather value.
