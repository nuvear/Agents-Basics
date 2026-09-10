# Instructor teaching materials

Author: **Rajkumar Rajagobalan**

- [PowerPoint teaching deck](../output/pptx/MCP_Weather_Teaching_Deck.pptx)
- [Speaker notes in Markdown](SPEAKER_NOTES.md)
- [Student workbook](../mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md)
- [Student workbook PDF](../output/pdf/MCP_Colab_Student_Workbook.pdf)
- [Open the student lab in Colab](https://colab.research.google.com/github/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb)

## Running the class

Slide 1 is the arrival and preparation screen. Start the 120-minute timer on slide 2. Slides 2–28 contain the complete two-hour sequence, including a five-minute break. Slides 29–30 are optional instructor references; they add no time to the planned core class.

Use the Notes pane or Presenter View to see the attached notes. Share only the slide show with students. The Markdown notes offer a separate reading copy.

Each teaching segment leads into the same weather example. The illustrations explain the model's information boundary, an API exchange, the function-calling loop, MCP host/client/server roles and the Colab deployment. Leave each lab slide visible while pairs complete the referenced notebook and workbook steps.

Notes provide explanations, questions, expected answers, checkpoints, transitions and recovery instructions. The footer shows the elapsed class window and the time allocated to the slide.

## Before students arrive

1. Run the notebook's Preparations A–D on a hosted Colab CPU runtime.
2. Rehearse both model labs using your OpenAI account and sample weather.
3. Confirm that students can access their own notebook copies and assigned API credentials through Colab Secrets.
4. Keep a working partner or instructor demonstration available for blocked students.
5. Keep optional live weather disabled unless you have separately rehearsed SerpApi access.

The offline path was exercised locally. Hosted Colab, Secrets access and live OpenAI/SerpApi calls still need instructor rehearsal. Scripted fallback demonstrates orchestration and actual MCP communication, but does not perform model inference. Weather is synthetic by default. Label both dimensions explicitly during class.

The hosted class uses OpenAI for inference; Python and the MCP server run inside Colab. Local LM Studio remains an optional extension on a student's own computer. Colab's localhost does not refer to that computer.

## Timing

| Minutes | Slides | Activity |
|---|---|---|
| 0–10 | 2–4 | Model boundary and workshop orientation |
| 10–25 | 5–8 | API concepts, Lab 1 and debrief |
| 25–50 | 9–14 | Function calling, Lab 2 and debrief |
| 50–55 | 15 | Break |
| 55–70 | 16–19 | MCP concepts |
| 70–100 | 20–24 | MCP server, Lab 3, debrief and deployment |
| 100–113 | 25–26 | Pair challenge and failure exercise |
| 113–120 | 27–28 | Exit ticket and close |

## Editing and rebuilding

Edit the PowerPoint directly for a one-off class, or edit the structured content in [slides.json](slides.json) for a reproducible revision. Illustrations are in [assets](assets/); prompt provenance is in [PROMPTS.md](assets/PROMPTS.md).

The source builder is [build_teaching_deck.mjs](../scripts/build_teaching_deck.mjs). It requires the Codex presentations runtime with `@oai/artifact-tool`, the presentations skill utilities, and Python. Set `PRESENTATIONS_SKILL_DIR`, `RUNTIME_NODE_MODULES`, and optionally `PYTHON_EXECUTABLE` to your local runtime paths, ensure Node can resolve the artifact package, then run:

```bash
node scripts/build_teaching_deck.mjs
```

The builder writes private intermediate files to `.deck-build/` and the final deck to `output/pptx/`. After changing notes in the JSON source, refresh the Markdown reading copy as well.
