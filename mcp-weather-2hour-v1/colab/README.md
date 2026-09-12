# Google Colab — primary classroom delivery

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb)

Use the badge to open the published notebook directly from this repository. The upload instructions below are an alternative for a downloaded copy.

Use [MCP_Weather_2Hour_Colab.ipynb](MCP_Weather_2Hour_Colab.ipynb) for the student labs. The notebook includes the complete two-hour sequence, explanatory notes, exercises and exit ticket. Preparation A loads the workshop files from this GitHub repository on hosted Colab, or locates them on a local Colab runtime.

## Student workbook

Use the [step-by-step Markdown workbook](../workbook/MCP_Colab_Student_Workbook.md) or [printable PDF](../../output/pdf/MCP_Colab_Student_Workbook.pdf), authored by Rajkumar Rajagobalan, alongside the notebook.

## Student preparation

1. Open [Google Colab](https://colab.research.google.com/).
2. Choose **File → Upload notebook** and select `MCP_Weather_2Hour_Colab.ipynb`.
3. Connect either a hosted Python runtime or **Connect to a local runtime**. No GPU or LM Studio is needed.
4. Run Preparation A and B. Hosted Colab clones this repository into `/content/mcp_weather_2hour`. A local runtime uses the files already on the Mac. No Drive mount is needed.
5. On hosted Colab, add `OPENAI_API_KEY` in **Secrets** and grant this notebook access. Add `SERPAPI_KEY` for live weather. On a local runtime, put the same names in the workshop `.env`. Then run Preparation C and D.
6. Follow the notebook from Lab 1 onwards. Save a personal copy with your notes.

If no OpenAI key is available, the notebook uses scripted model turns and sample weather. The MCP server and protocol calls are still real. Mark model inference as pending; this fallback does not claim to run a language model.

Do not put keys in notebook source, comments or outputs. The optional masked prompt is available when Colab Secrets is not being used. Hosted Colab prefers Secrets; a local runtime prefers `.env`. Keys are read into environment variables, never printed.

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

Use `OPENAI_MODEL` in the credential cell to select the rehearsed model; the default is `gpt-4.1-mini`. Labs 2 and 3 use live SerpApi when `SERPAPI_KEY` is present and labelled sample weather otherwise. The extra instructor live-weather cell stays off during **Run all**.

**Local means local to the Colab runtime.** The host and MCP subprocess run on Google's hosted machine. A laptop's LM Studio server is not reachable using the hosted notebook's `localhost`. Keep the existing local-computer LM Studio scripts as an optional alternative, outside this Colab class. No public tunnel is required for the core lab.

Rehearse the notebook in an actual hosted Colab session and run the OpenAI path before teaching. This delivery's local checks do not establish Google account/runtime access, Secrets permissions, live model behavior or live weather availability.

## Maintenance

Rebuild after changing the classroom scripts:

```bash
python colab/build_notebook.py
```

The builder writes notebook cells only. Preparation A loads `mcp-weather-2hour-v1` from this repository. It does not copy `.env`, installed environments or local notebook outputs. After changing classroom scripts, rebuild and push so hosted Colab receives the new files.

Sources: [Colab notebook upload, sharing and runtime guidance](https://research.google.com/colaboratory/faq.html), [official Colab Secrets implementation](https://github.com/googlecolab/colabtools/blob/main/google/colab/userdata.py).
