# Student workbook — weather agents and MCP

**Colab students:** use the exercises and editable notes in [the lab notebook](colab/MCP_Weather_2Hour_Colab.ipynb). This Markdown workbook remains a companion for the optional local-computer route.

Name: __________  Partner: __________  Date: __________

Model route: LM Studio / OpenAI / offline fallback

Before class, follow [SETUP.md](SETUP.md). During class, run commands inside this package using its virtual environment. Do not write credentials here.

## Predict before running

A user asks for Tokyo's current weather. What can a model know from training? What must be fetched? Who executes that fetch?

Notes: ______________________________________________

## Lab 1 — direct API, 15 minutes

```bash
python 01_direct_serpapi_api.py --sample --show-raw
python 01_direct_serpapi_api.py --sample --units fahrenheit
```

Record the endpoint, query without the key, returned temperature/unit, resolved location, observation label and sample marker. Find the raw `answer_box` and normalized `temperature` object.

Prediction: 21°C = ______°F. Actual: ______°F.

Which function sends HTTP in live mode? __________________

Did either command make a network request? _______________

Why is this useful without an agent? ______________________

## Lab 2 — custom function tool, 25 minutes

Choose one:

```bash
python 02_custom_tool_agent.py --provider lmstudio --mock-weather --force-tool
python 02_custom_tool_agent.py --provider openai --mock-weather --force-tool
```

No model ready? Run `python 02_custom_tool_agent.py --offline`; mark inference pending.

Record a short trace showing:

| Evidence | Your observation |
|---|---|
| Requested tool name | |
| City, country and units | |
| Code that executes the function | |
| Tool result says mock=true? | |
| Final answer acknowledges sample data? | |

Explain why the function schema alone cannot fetch weather: __________

What did `--force-tool` control? ___________________________

Optional: remove `--force-tool` and observe whether the model chooses a tool. Do not assume the result before running.

## Lab 3 — MCP, 30 minutes

Start with real discovery and a sample call without a model:

```bash
python 03_mcp_agent.py --inspect
```

Then choose your model route:

```bash
python 03_mcp_agent.py --provider lmstudio --mock-weather --force-tool
python 03_mcp_agent.py --provider openai --mock-weather --force-tool
```

Fallback: `python 03_mcp_agent.py --offline`.

Find the discovered tool name and `inputSchema` (shown as `parameters` after mapping to the model tool format). Find the `[MCP tools/call]` line and returned sample marker.

| Responsibility | Custom function agent | MCP agent |
|---|---|---|
| Where does the tool schema come from? | | |
| Who manages model conversation? | | |
| Which process executes weather code? | | |
| Where does the live weather key belong? | | |

Draw the path: user → host ↔ model; host/client ↔ server → provider. Mark which connections remain inside your computer and which can leave it.

## Pair challenge, 13 minutes

With a real model, ask “What is the weather in Lisbon, Portugal in Fahrenheit?” using `--mock-weather` in either agent. Confirm the city, country and unit in the requested arguments. A different city does not make synthetic weather real.

With no model, repeat the direct API sample unit conversion and explain the fixed fixture.

Run the failure exercises:

```bash
python -m unittest discover -s tests -p test_training.py -v
```

Explain one failure: invalid units, unknown tool, missing OpenAI key, or a weather answer without a tool call. Which boundary caught it? __________________

## Exit ticket, 7 minutes

1. Does a structured tool request mean the API already ran? Explain.
2. What does MCP change, and what API work remains?
3. What changes when switching LM Studio to OpenAI in this package?
4. How do `--mock-weather` and `--offline` differ?
5. What should the agent do when the weather provider gives no usable result?

## Completion record

- [ ] Direct sample run and inspected
- [ ] Real model requested tool and received result (or pending)
- [ ] Actual local MCP discovery and call inspected
- [ ] Can explain request versus execution
- [ ] Can distinguish sample values from live evidence

One thing to investigate next: ____________________________
