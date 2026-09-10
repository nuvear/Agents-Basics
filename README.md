# Agents Basics — API to agent to MCP

A two-hour, hands-on weather-agent workshop for students, delivered through Google Colab.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb)

## Start the lab

1. Click **Open in Colab** above and save your own notebook copy.
2. Connect a standard hosted Python runtime; no GPU is required.
3. Run the notebook's preparation cells before class.
4. Add `OPENAI_API_KEY` in Colab Secrets and grant notebook access for real model inference. No key? The notebook includes a clearly labelled scripted fallback.
5. Follow the three labs in order.

The notebook contains the required scripts and sample data. Students do not need local Python, LM Studio, a repository clone, or ZIP extraction.

## The two-hour program

| Minutes | Activity |
|---|---|
| 0–10 | Weather problem; model versus agent |
| 10–25 | Direct weather API lab |
| 25–50 | Function-calling agent lab |
| 50–55 | Break |
| 55–70 | MCP host, client and server |
| 70–100 | MCP discovery and execution lab |
| 100–113 | Pair challenge and failure exercise |
| 113–120 | Exit assessment |

## Materials

- [Student notebook](mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb)
- [Colab preparation and instructor instructions](mcp-weather-2hour-v1/colab/README.md)
- [Timed facilitator guide and answer key](mcp-weather-2hour-v1/FACILITATOR.md)
- [Architecture and source map](mcp-weather-2hour-v1/README.md)
- [Review of the original training approach](mcp-weather-2hour-v1/REVIEW.md)
- [Validation and remaining live checks](mcp-weather-2hour-v1/VALIDATION.md)

OpenAI provides inference in the hosted Colab class. Both the Python host and the MCP server run inside the Colab runtime. A real MCP connection is used even in the scripted fallback; that fallback does not perform model inference. Weather is sample data by default. Optional live weather requires a separate `SERPAPI_KEY`.

The package also supports LM Studio for an optional local-computer exercise. Hosted Colab's localhost is not the student's laptop.

## Validation status

The notebook's 14 code cells completed locally in a fresh environment without credentials, and all 16 package tests passed. Hosted Colab execution, Colab Secrets permissions and live OpenAI/SerpApi calls still require instructor rehearsal.

## Maintaining the notebook

Edit the Python source in `mcp-weather-2hour-v1`, then rebuild the embedded notebook:

```bash
python mcp-weather-2hour-v1/colab/build_notebook.py
```

Run package tests from that folder in a prepared Python environment:

```bash
python -m unittest discover -s tests -v
```

Do not commit keys, `.env`, virtual environments or notebooks containing secret outputs. No credentials or original ZIP archives are included in this repository.
