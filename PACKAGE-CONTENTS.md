# Distribution contents

**Agents Basics - full two-hour course v1.1**

Author: **Rajkumar Rajagobalan**

This distribution contains the current course from `nuvear/Agents-Basics`. Open `START-HERE.md` after extracting the archive. Existing historical ZIPs and extracted source packages outside this repository are preserved separately.

| Folder or file | What it contains |
|---|---|
| `START-HERE.md` | English, Japanese and Simplified Chinese entry instructions |
| `output/pdf/` | Three 12-page student workbooks: English, Japanese and Simplified Chinese |
| `output/pptx/` | English 30-slide teaching deck with notes on every slide |
| `teaching/` | English speaker notes, deck usage guide, editable slide content and illustrations |
| `mcp-weather-2hour-v1/colab/` | Self-contained student notebook, notebook builder and setup instructions |
| `mcp-weather-2hour-v1/workbook/` | All three student guides in Markdown and localization notes |
| `mcp-weather-2hour-v1/` | Python labs, MCP server, weather adapter, sample data, tests, requirements, facilitator plan, local LM Studio extension and original approach review |
| `scripts/` | PDF/deck builders, localized-guide checks and distribution builder |
| `SHA256SUMS.txt` | Generated inside the ZIP; hashes of every other packaged file |

## Running the labs

The primary classroom environment is Google Colab. You need a Google account, internet access and a standard hosted Python runtime. Preparation installs the dependencies; no GPU is required. Real inference needs an OpenAI account with access to the configured model and available API quota. The optional live-weather demo needs a separate SerpApi key. No key is included.

A copy of `MCP_Weather_2Hour_Colab.ipynb` is bundled under `mcp-weather-2hour-v1/colab/`. If the repository link is unavailable, upload that notebook through Colab's notebook upload option, save a copy and run preparation. Files in the ZIP can be read locally, but this is not a preinstalled, disconnected lab environment.

The optional local-computer route, including LM Studio, is documented in the package setup guide. Colab's localhost is not the student's laptop.

## Language scope

The Japanese and Simplified Chinese student guides are localized technical drafts based on the English v1.0 workbook. They preserve all 38 steps, code and evidence checks, with natural explanatory prose for each language. The notebook and instructor materials remain English. No independent human translator or native-language reviewer is credited.

## Package hygiene and integrity

The archive excludes existing ZIPs, Git history, virtual environments, build caches, raw provider responses and credential files. The included `.env.example` contains placeholders only. The notebook contains no saved execution outputs.

To verify contents after extraction on macOS, run `shasum -a 256 -c SHA256SUMS.txt` from the extracted course folder. On Linux, use `sha256sum -c SHA256SUMS.txt`. A checksum confirms file integrity, not live-service availability.

## Rebuilding

Run `python scripts/build_course_package.py` from a Git checkout after adding intended course files to the Git index. It packages tracked course files, excludes generated distributions and private material, and creates a SHA-256 sidecar for the ZIP. The archive has one enclosing folder so extraction stays organized.
