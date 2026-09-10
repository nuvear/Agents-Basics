# Validation record

Verified 10 September 2026 on macOS, Python 3.14.3, using a new virtual environment inside this package. Installed dependency versions are recorded in `requirements-tested.txt` (including MCP 1.30.0 and OpenAI SDK 2.54.0).

## Passed

| Check | Evidence |
|---|---|
| Original main package | All 13 existing offline unit tests passed using the new environment |
| New package | All 16 tests passed: 5 reused provider tests and 11 new host/configuration/protocol boundary tests |
| Real local MCP integration | Subprocess startup, initialization, discovery, sample call, Fahrenheit conversion and invalid-unit rejection passed |
| Lab 1 sample | Direct script parsed fixture and returned 69.8°F for the 21°C sample |
| Lab 2 offline | Scripted request executed the real local adapter with labelled sample data |
| Lab 3 inspect | Real `tools/list` and `tools/call`, without a model service |
| Lab 3 offline | Scripted model connected through an actual stdio MCP client/server session |
| Dependency compatibility | `python -m pip check`: no broken requirements |
| Source preservation | SHA-256 comparison of all 65 inventoried original non-secret, non-cache files: no changes, including the three ZIPs |

Original `.env` files were neither read nor copied. The preservation inventory excludes `.env`, `.venv`, caches and `.DS_Store`. ZIPs were hashed for preservation only, not opened or extracted. Running the original tests may create Python cache files; original source files were unchanged.

## What the tests establish

They check normalized weather conversion, sample labelling, credential scrubbing, missing-key diagnostics, provider-specific configuration, tool-result correlation IDs, rejection of unknown tools and invalid arguments, call budgets, provider failure propagation and refusal to accept a no-tool weather answer. The MCP integration test really launches the Python server process; its weather data is synthetic.

## Not verified live

- OpenAI account credentials, model access, actual tool selection or final generated answers.
- LM Studio server availability, loaded model or actual model tool behavior.
- Live SerpApi weather retrieval, freshness, quota or geographic correctness.
- Original provider-hosted SerpApi MCP integration.
- Windows/Linux execution or delivery to an actual student cohort within 120 minutes.

The OpenAI implementation is prepared for a locally configured key; no real key is required for the delivered offline checks. Before teaching a live class, run the selected model through Labs 2 and 3 with sample weather, then optionally rehearse one live weather request per layer. The final model prose must be compared with tool evidence, including its sample marker.

## Repeat checks

```bash
python -m unittest discover -s tests -v
python -m pip check
python 01_direct_serpapi_api.py --sample --units fahrenheit
python 02_custom_tool_agent.py --offline
python 03_mcp_agent.py --inspect
python 03_mcp_agent.py --offline
```

Do not distribute the installed `.venv`; each student builds their own environment. No new ZIP has been created.

## Google Colab adaptation — 10 September 2026

The self-contained notebook at `colab/MCP_Weather_2Hour_Colab.ipynb` is now the primary classroom format. Its 14 Python code cells were executed in order locally from a fresh temporary working directory with OpenAI, SerpApi and LM Studio credentials removed from the execution environment. The notebook created its embedded files and installed its isolated Python environment successfully. All 16 embedded tests passed; sample API, scripted agent, real MCP inspection and scripted-model MCP exercises completed. Optional unforced and live-weather cells stayed disabled. The delivered notebook contains no execution outputs or credentials.

This is local cell-by-cell execution, not a hosted Colab session or browser rendering test. Google account access, hosted runtime provisioning, Colab Secrets permissions and actual OpenAI/SerpApi calls remain unverified. Rehearse those paths on Colab before class. Original ZIPs and extracted source packages remain unchanged.

## Student workbook - 10 September 2026

Created a separately titled draft workbook in Markdown and PDF, authored by Rajkumar Rajagobalan. PDF checks confirmed 12 pages, all 38 numbered steps, author metadata, all seven external link targets, and complete visible Markdown word coverage in extracted PDF text. Rendered all pages with Poppler and visually inspected the full set; dense pages received additional full-page inspection. No clipping, overlaps, broken tables or missing glyphs were observed. The workbook follows the existing Colab commands; no application code or live-service validation changed.
