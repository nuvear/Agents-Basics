# Pre-class setup — complete before the two-hour session

**For the Google Colab class, follow [Colab preparation](colab/README.md) and the notebook cells.** No local Python or LM Studio installation is needed. The instructions below apply only to the optional local-computer route.

Allow 20–40 minutes, longer if downloading a local model. Bring Python 3.11 or newer, a terminal and a text editor. This edition was tested on macOS with Python 3.14; Windows commands are supplied but have not been executed here.

## 1. Open this package folder

Use the terminal's folder navigation or “Open in Terminal” on `mcp-weather-2hour-v1`. All commands below assume this is your current directory. Do not reuse an environment from another workshop folder.

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-tested.txt
cp .env.example .env
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-tested.txt
Copy-Item .env.example .env
```

On Windows, substitute `.\.venv\Scripts\python.exe` for `python` in lesson commands. No activation-policy change is needed. If exact dependency pins do not support your platform, have the facilitator resolve them before class using `requirements.txt`, then rerun validation.

## 2. Choose one model backend

**LM Studio:** load a model that supports tool calling, start its local server, and copy its exact model identifier into `LM_STUDIO_MODEL` in `.env`. Set `MODEL_PROVIDER=lmstudio`. The default base URL is `http://localhost:1234/v1`. If local authentication is enabled, put its token in `LM_STUDIO_API_KEY`. Model downloads and hardware suitability must be verified on each student's machine before class.

**OpenAI:** set `MODEL_PROVIDER=openai` and enter your API key locally as `OPENAI_API_KEY`. `OPENAI_MODEL=gpt-4.1-mini` is the default; the facilitator can set another compatible, accessible model after rehearsing it. This option requires internet access and an API account with available quota. Do not paste the key into chat or a worksheet. The code is ready for a key, but live OpenAI execution has not been verified as part of this delivery.

These are alternative inference services. Students on OpenAI do not need LM Studio installed. Both still run the Python host and local MCP server on their own computer.

## 3. Weather data is configured separately

Leave `SERPAPI_KEY` blank for the sample exercises. For live weather, enter a SerpApi key locally. An OpenAI key cannot authenticate SerpApi. This package uses `SERPAPI_KEY`; the older business-agent package uses the different name `SERPAPI_API_KEY`.

SerpApi provides a Google weather search result. Report the actual returned source and observation label; do not automatically call it AccuWeather or Weather.com. A successful search may contain no weather answer box. The adapter returns a failure rather than substituting an arbitrary web snippet.

## 4. Readiness gate

```bash
python -m unittest discover -s tests -v
python 01_direct_serpapi_api.py --sample
python 03_mcp_agent.py --inspect
```

Then run both agent lessons using your chosen backend with `--mock-weather --force-tool` (commands in README). Verify a tool request, execution result and an answer explicitly described as sample data. If the model is unavailable, complete `--offline` and pair with someone whose live model works. This fallback teaches protocol and control flow; it does not demonstrate model inference.

## 5. Optional live rehearsal

```bash
python 01_direct_serpapi_api.py Tokyo --country JP
python 02_custom_tool_agent.py --force-tool
python 03_mcp_agent.py --force-tool
```

The last two commands use `MODEL_PROVIDER`. Each run is bounded to four model turns and four tool requests, with no automatic model retries. Live weather requests consume SerpApi quota; hosted inference consumes OpenAI usage. Use sample weather for student repetitions and one facilitator live demonstration if credentials are ready.

## Common failures

| Symptom | First action |
|---|---|
| Missing package | Use the package's `.venv` Python and reinstall requirements |
| Missing OpenAI key | Edit this package's `.env`; do not put it in Python source |
| Model 401/403 | Check the selected provider's credential locally |
| Model 404 / missing model | Check the model ID, account access and endpoint |
| Model 429 | Check quota/rate limit; switch to offline rehearsal |
| LM Studio connection failure | Load model, start server, verify base URL |
| No tool executed | Try `--force-tool`; verify actual tool support |
| MCP startup/protocol failure | Run `--inspect`; use the pinned MCP v1 SDK; never add stdout prints to the server |
| No weather result | Specify city and country; explain unavailable evidence |
| Repeated calls | The budget stops execution; inspect the prompt/tool result |

Credential boundaries: the OpenAI key authenticates only the OpenAI model client; the local-model token authenticates only LM Studio. The MCP subprocess receives the weather key, not either model key. In OpenAI mode, the question, tool schema and weather result go to OpenAI. The SerpApi key is never intentionally included in model messages. Treat returned text as untrusted data. Never distribute `.env`, `.venv`, raw live response files or credentials with the teaching material.
