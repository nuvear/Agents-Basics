# Google Colab — primary classroom delivery

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb)

Use the badge to open the published notebook directly from this repository. The upload instructions below are an alternative for a downloaded copy.

Use [MCP_Weather_2Hour_Colab.ipynb](MCP_Weather_2Hour_Colab.ipynb) for the student labs. The notebook includes the complete two-hour sequence, embedded Python scripts and fixtures, explanatory notes, exercises and exit ticket.

## Student preparation

1. Open [Google Colab](https://colab.research.google.com/).
2. Choose **File → Upload notebook** and select `MCP_Weather_2Hour_Colab.ipynb`.
3. Connect a standard hosted Python runtime with no accelerator. No GPU or LM Studio is needed.
4. Run Preparation A and B to create the bundled files and install an isolated environment. No ZIP files or Google Drive mount are needed.
5. In **Secrets**, add `OPENAI_API_KEY` and grant this notebook access. Add `SERPAPI_KEY` only for optional live weather. Then run Preparation C and D.
6. Follow the notebook from Lab 1 onwards. Save a personal copy with your notes.

If no OpenAI key is available, the notebook uses scripted model turns and sample weather. The MCP server and protocol calls are still real. Mark model inference as pending; this fallback does not claim to run a language model.

Do not put keys in notebook source, comments or outputs. The optional masked prompt is available when Colab Secrets is not being used. Keys are read into runtime environment variables, not written to the embedded scripts.

## Instructor delivery

Keep the existing 120-minute timetable. Complete notebook upload, dependency installation and key setup before class. Students use the notebook as their workbook; the folder's facilitator guide provides pacing, questions and answers. Its terminal commands correspond to the notebook cells, so students do not need to open a terminal.

- 0–10: prediction and actors.
- 10–25: Lab 1 sample and unit conversion.
- 25–50: Lab 2 model/tool loop, schema and execution trace.
- 50–55: break.
- 55–70: host/client/server map.
- 70–100: Lab 3 real discovery, execution and model integration.
- 100–113: pair challenge and failure tests.
- 113–120: exit ticket.

Use `OPENAI_MODEL` in the credential cell to select the rehearsed model; the default is `gpt-4.1-mini`. The sample labs with real inference consume OpenAI usage. Live SerpApi calls are disabled by default behind `RUN_LIVE_WEATHER=False`. The notebook does not reuse any API key from the original local packages.

**Local means local to the Colab runtime.** The host and MCP subprocess run on Google's hosted machine. A laptop's LM Studio server is not reachable using the hosted notebook's `localhost`. Keep the existing local-computer LM Studio scripts as an optional alternative, outside this Colab class. No public tunnel is required for the core lab.

Rehearse the notebook in an actual hosted Colab session and run the OpenAI path before teaching. This delivery's local checks do not establish Google account/runtime access, Secrets permissions, live model behavior or live weather availability.

## Maintenance

Rebuild after changing the classroom scripts:

```bash
python colab/build_notebook.py
```

The builder embeds only selected Python source files, sample JSON and dependency requirements. It does not copy `.env`, installed environments, ZIPs or local notebook outputs. Share the `.ipynb` file; students do not need the builder or the original folders.

Sources: [Colab notebook upload, sharing and runtime guidance](https://research.google.com/colaboratory/faq.html), [official Colab Secrets implementation](https://github.com/googlecolab/colabtools/blob/main/google/colab/userdata.py).
