# Review of the existing training folder

Reviewed 10 September 2026. Scope: the three extracted packages, source code, tests, curriculum/navigation material, example configuration, sample JSON and all three teaching images. ZIPs were left unopened and unchanged; no ZIP-to-folder equivalence is assumed. Local `.env` contents were not inspected. Installed environments, caches and OS metadata are not course content.

## My opinion

The central teaching idea is strong: use one familiar weather question to make the progression from HTTP to model tool use to MCP visible. The three-lesson SerpApi package already has the best instructional foundation: numbered traces, sample data, a provider adapter, tests, exercises, architecture notes and facilitator guidance. Keep that progression.

The problem is scope and comparison clarity. Its current facilitator plan is three 90-minute sessions, before considering the separate ten-role workshop. Compressing all of that into two hours would leave too little time for students to observe and explain the program. Teach three small experiments, with setup beforehand and broader material afterwards.

## Inventory and recommended placement

| Existing content | What it contributes | Place in the new program |
|---|---|---|
| `lmstudio_serpapi_api_to_mcp/` | Three scripts, adapter, HTTP support, 13 tests, full Obsidian learning layer | Main source and extended reference |
| `lmstudio_accuweather_agent/` | Direct provider integration and bounded local-model tool loop | Optional provider replacement exercise |
| `serpapi-agent-workshop/` | Ten business roles using a menu and multiple SerpApi functions | Follow-on application workshop |
| `images/` | Three readable model/tool/answer illustrations | Introductory function-calling aids, with verbal corrections below |
| Three root ZIP files | Archived packages, extraction status unverified | Leave untouched |

## What is especially effective

1. Weather makes the need for fresh external evidence obvious.
2. The custom-tool scripts distinguish a model request from Python execution.
3. Sample/mock modes keep the provider dependency out of early experiments.
4. The main vault emphasizes evidence, responsibility and safe errors instead of accepting polished final prose as proof.
5. The remote MCP example provides a useful later contrast with hand-built dispatch.

## What I would change for this class

**Make MCP observable.** The original MCP dry-run prints a request configuration; it does not establish a connection, discover tools or execute one. The new local-server lab demonstrates actual `initialize`, `tools/list` and `tools/call` without an external service. Explain that the connection is real even when the weather is simulated.

**Hold the tool behavior constant.** The original custom tool exposes normalized `get_current_weather`, but the remote MCP example exposes general `search`. That simultaneously changes the contract, result shape and hosting. The new core uses the same weather adapter in all three labs and changes only its connection and execution boundary. Remote `search` becomes an extension.

**Distinguish agent runtime from MCP.** MCP standardizes the host/server interface; it does not itself supply model reasoning, guarantee weather truth or eliminate the underlying provider API. In the original native LM Studio example the host handles orchestration. In this edition the Python host handles it. Both arrangements can use MCP. Tools are the focus of this class; resources and prompts are other MCP concepts for later study.

**Make model substitution explicit.** An OpenAI-compatible LM Studio endpoint does not imply that a cloud OpenAI key or native LM Studio MCP request can be used unchanged. This edition selects provider URL, key and model separately while keeping the host and MCP server shared.

**Move setup and Obsidian navigation out of class.** Students need only a terminal and editor. The full vault remains useful reference, but learning Obsidian features competes with the MCP objective in 120 minutes.

## Specific cautions in the supplied content

- The images show function calling, not an MCP host/client/server architecture. Use the new diagram when MCP begins.
- The image caption “sample live answer” and the illustrated 21°C can confuse demonstration data with a current observation. Say “illustrative sample, not current weather.” No image has been modified.
- The Weather.com/AccuWeather labels in the images are generic illustrations. The SerpApi scripts actually call Google's weather search through SerpApi; name an upstream weather publisher only if the result identifies one.
- `serpapi-agent-workshop` is a set of role-configured function-tool agents. It is not a demonstration of MCP or ten collaborating agents. Its `MAX_STEPS` bounds model turns, not total searches when a turn requests multiple tools.
- That package returns raw exception strings from `_serpapi`; request failures can contain URLs with query credentials. Its raw JSON truncation can also cut a tool result mid-document. These merit fixes before using it for projected live troubleshooting, but that package was preserved in this task.
- The main weather adapter also included provider error-body text in some errors. The new copy suppresses provider-body detail and scrubs known credentials at tool boundaries; the original remains unchanged.
- The main custom-tool lesson can return text without a tool call. The new weather-specific host withholds such an answer. A prompt alone is not proof of evidence use.
- The business workshop includes quota/hardware estimates that were not revalidated here. Check provider plans and actual student machines before reuse; do not make them guarantees in the two-hour handout.

## Retained limits

The new code is a teaching implementation, not a production agent platform. It has bounded calls and argument validation, but generated prose still needs comparison with tool evidence. The weather adapter's observation label may be incomplete, and country search settings do not guarantee correct location resolution. Students must inspect the returned location. A request timestamp is not proof of a fresh measurement.

Offline tests establish code and protocol behavior. They do not establish current weather accuracy, OpenAI account access, local model tool reliability or remote SerpApi MCP availability. See the validation record for the checks actually run.
