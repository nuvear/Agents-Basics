# Weather agents and MCP - speaker notes

Author: Rajkumar Rajagobalan

Core class: 120 minutes. Slide 1 is pre-class; slides 29–30 are optional references.

## 1. Before we begin

SLIDE 1: Before we begin
TIMING: Before class; Outside the 120-minute core sequence.

PURPOSE: Use this holding slide as students arrive; it is not part of the timed class.
DO: Open your own notebook and workbook before projecting. Rehearse both model labs with sample weather beforehand. Use a standard CPU runtime. Ask students to run Preparation A, B, C and D in order. Preparation D should show actual MCP discovery and a sample call. Keep keys out of the projected screen. Check that your own OpenAI account and chosen model work.
ASK: Who has a tool result from Preparation D? Pair anyone who is blocked with a ready learner. Distinguish missing setup from missing inference access.
FALLBACK: No key is acceptable for protocol learning; real model inference must be recorded as pending. Do not spend more than five minutes of class installing packages. If connection issues persist, use a partner demonstration.
NEXT: Start the 120-minute timer when you advance to the title slide. Keep the optional live-weather flag False.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 2. Weather agents and MCP

SLIDE 2: Weather agents and MCP
TIMING: 00–02; 2 minutes.

SAY: Today we will ask one weather question in three different implementations. By the end, you should be able to explain who requests a tool, who executes it and how a result reaches the model. You will also observe a real MCP connection.
DO: Introduce yourself and invite students to work in pairs. Explain that the slides provide the concepts, the notebook runs the experiments and the workbook captures evidence.
ASK: What would you need to know to trust an answer about the weather right now? Take one response, without starting a long discussion.
TIME CONTROL: Spend no more than two minutes here. Installation and account setup belong before class. The timed lesson includes a five-minute break.
NEXT: Move to the model illustration and ask whether training data can supply a current observation.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 3. The model and current weather

SLIDE 3: The model and current weather
TIMING: 02–06; 4 minutes.

SAY: The illustration is a metaphor for the model's information boundary. The robot may have learned patterns about weather, but training alone cannot establish the current temperature. This applies to a model served locally or through a cloud API.
ASK: If the model answers with a plausible temperature, what would be missing? Expected answer: a current source or tool result, along with place, units and an observation label where available.
DO: Spend one minute asking students to write a prediction in workbook Section 1. Invite two students to name the actor that could fetch the data. Guide them toward executable application code, rather than saying the model itself browses the weather service.
MISCONCEPTION: A model can be embedded in an application that has tools. This illustration concerns the model without that external evidence path, not a claim that all AI applications lack internet access.
NEXT: Show how the same question will travel through three implementations.
ILLUSTRATION: Conceptual generated artwork; not a live observation.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 4. The two-hour route

SLIDE 4: The two-hour route
TIMING: 06–10; 4 minutes.

SAY: We keep the weather scenario stable so the architecture is easier to compare. First Python calls the API. Then a model asks Python to use a tool. Finally the host discovers and invokes that tool through MCP.
DO: Orient students to workbook Sections 4, 5–6 and 8. Ask them to keep the notebook beside the workbook. Explain that lab slides remain visible while they work; you are not trying to talk for two hours.
ASK: What evidence will we collect at every stage? Expected answer: inputs, execution trace, result, and whether the weather is sample or live.
TIME CONTROL: Begin Lab 1 concepts at minute 10. If running late later, omit optional unforced inference and live weather, but preserve MCP discovery/call time and the exit ticket.
NEXT: Focus on the API boundary before introducing a model.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 5. An ordinary API exchange

SLIDE 5: An ordinary API exchange
TIMING: 10–14; 4 minutes.

SAY: An API provides an interface that one piece of software can use. Here Python builds a request containing an endpoint, query parameters and authentication. The service returns JSON, which Python validates and normalizes.
DO: Point to the outbound HTTP arrow and the inbound JSON arrow. Emphasize that no model is present in this first implementation. The actual endpoint in the lesson is https://serpapi.com/search.json. SerpApi returns Google's weather search result; do not automatically name another weather publisher.
ASK: Can this be useful without an agent? Expected answer: yes, ordinary software can fetch and process data using a fixed procedure.
CLARIFY: The upcoming --sample command does not send HTTP; it demonstrates the response-processing path using a fixture. The diagram describes the live path.
NEXT: Inspect the fields that survive normalization.
ILLUSTRATION: Conceptual generated diagram of a request/response exchange.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 6. The weather evidence

SLIDE 6: The weather evidence
TIMING: 14–17; 3 minutes.

SAY: These are selected fields from classroom demonstration data. They show three things we must distinguish: the numeric value, its unit and the fact that it is synthetic. A value of 21 is not meaningful without context.
DO: Explain that the raw API-shaped fixture includes an answer_box; the adapter returns a more consistent result. The slide is an excerpt, not a complete JSON document. Ask students to locate location and sources in the actual notebook output as well.
ASK: Does a retrieval timestamp prove that a weather measurement is fresh? Expected answer: no, retrieval time and observation time are different.
MISCONCEPTION: A sample can use a city label and still be synthetic. Never present the 21°C figure as Tokyo's current temperature.
NEXT: Students run the two direct sample cells and fill their evidence table.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 7. Lab 1 · API sample and units

SLIDE 7: Lab 1 · API sample and units
TIMING: 17–23; 6 minutes.

DO: Leave this slide on screen for six minutes. Tell students to run run_lab("01_direct_serpapi_api.py", "--sample", "--show-raw"), followed by the Fahrenheit sample cell. These are already in the notebook; no terminal is needed.
COACH: Spend the first minute confirming the cells ran. During minutes two to four, ask students to point to the sample marker and compare raw answer_box with normalized temperature. Ask them to predict the conversion before running it. The expected result is 69.8°F. During the last two minutes, have partners compare their source and observation labels.
CHECKPOINT: Each pair should explain that the fixture was read locally and no live provider request occurred.
FALLBACK: If a helper is undefined, run Preparations A–D in order. If setup still blocks progress, observe a partner and record the evidence rather than consuming the rest of the block.
NEXT: Ask who executed the API operation in the live variant.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 8. Lab 1 debrief

SLIDE 8: Lab 1 debrief
TIMING: 23–25; 2 minutes.

ASK: Take one short answer for each question. Python application code sends the request in live mode. The sample flag and provider/observation wording identify demonstration data. The unit conversion changes the temperature representation, not the underlying observation.
DO: Ask a learner to name perform_serpapi_search in the source as the live network boundary. Avoid a line-by-line adapter tour.
CLARIFY: Changing a requested city in fixture mode does not fetch a new city's weather. The fixture remains fixed.
TRANSITION: We have a useful Python function. Next we will describe that function to a model, without giving the model the Python implementation or provider key.
TIME CONTROL: Move on at minute 25.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 9. The function-calling loop

SLIDE 9: The function-calling loop
TIMING: 25–30; 5 minutes.

SAY: Follow the four numbered arrows. The model first emits a structured request containing a tool name and arguments. The application validates the request and executes the weather function. The result returns to the application, which sends it back into the model conversation. A later model turn can explain the result to the user.
DO: Point at the application in the middle. It is the actor executing the function and maintaining the conversation. Say that the model does not directly call the weather site in this example.
ASK: At which arrow has weather data actually been returned? Expected answer: after execution, when the tool result comes back. A request alone is not enough.
CLARIFY: This diagram is about function calling, before MCP. The tool implementation may itself call a provider API.
NEXT: Show the distinction between the tool's description and its code.
SOURCE: https://developers.openai.com/api/docs/guides/function-calling
ILLUSTRATION: Conceptual generated diagram; arrows represent the application-run tool loop.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 10. Schema and implementation

SLIDE 10: Schema and implementation
TIMING: 30–34; 4 minutes.

SAY: A schema is a contract. It tells the model what a tool is called and what arguments are accepted. It is not executable Python code. The implementation is the function that performs the work after the host approves the input.
DO: Open weather_contract.py in the notebook's source-tour cell and find PARAMETERS and TOOL. Then identify execute_weather. The required inputs are city, country_code and units; extra properties are rejected by the direct contract.
ASK: Could the model send a key or arbitrary extra argument instead? Expected answer: the host should validate against the advertised contract and reject unsupported arguments.
TEACHING CHOICE: Do not expand into the full JSON Schema language. Students only need required fields, types and allowed values for this lab.
NEXT: Trace how a result is associated with the correct tool request.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 11. A request and its matching result

SLIDE 11: A request and its matching result
TIMING: 34–37; 3 minutes.

SAY: The tool call has an identifier. When the application returns a result, it includes the matching tool_call_id. This lets the model conversation associate the result with the correct request. The names on this slide are illustrative; real calls can use different identifiers.
DO: Find the role=tool message in agent_core.py. Point out that the host adds both the assistant's request and the tool result to conversation history.
ASK: What might go wrong if results were returned without a matching identity? Expected answer: the system could not reliably match a result to its request, especially when multiple calls exist.
CLARIFY: The ID is not a provider API key. It identifies a tool request within the conversation.
NEXT: Establish exactly which parts of the upcoming run will be real and which will be samples.
SOURCE: https://developers.openai.com/api/docs/guides/function-calling

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 12. Real inference and sample weather

SLIDE 12: Real inference and sample weather
TIMING: 37–39; 2 minutes.

SAY: These switches control different boundaries. --mock-weather still calls the selected model service. --offline substitutes fixed Tokyo model requests and sample weather; it does not interpret the user's question through a language model. The MCP server and connection remain real in the third lab.
DO: Ask students to identify their selected route from Preparation C. Have those on the fallback write inference pending in the workbook.
CLARIFY: The core class uses sample weather. Live calls need a separate SERPAPI_KEY, and OpenAI inference requires account quota. Do not treat the existence of a key as proof of a successful model call.
TIME CONTROL: Keep this to two minutes and start the hands-on loop at minute 39.
NEXT: Run Lab 2.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 13. Lab 2 · Model request to tool result

SLIDE 13: Lab 2 · Model request to tool result
TIMING: 39–47; 8 minutes.

DO: Keep this slide visible for eight minutes. Students run run_lab("02_custom_tool_agent.py", *model_options()). With OpenAI configured this uses --mock-weather and --force-tool. Without a key it uses --offline.
SAY: In the OpenAI route, the host requires a first tool call, while the model supplies the arguments. Do not describe this as fully autonomous tool selection.
COACH: At minute two, confirm a tool request appears. At minute four, ask pairs to identify the function execution and result. At minute six, compare sample markers and numbers with the final prose. The fallback deliberately skips a generated final answer.
CHECKPOINT: A learner can point to [TOOL REQUEST], [EXECUTION] and [TOOL RESULT], and explain their different meanings.
FALLBACK: If OpenAI fails, use run_lab("02_custom_tool_agent.py", "--offline"). Record the model integration as pending. Do not expose Secrets on the shared screen.
NEXT: Debrief why the schema alone could not fetch weather.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 14. Lab 2 debrief

SLIDE 14: Lab 2 debrief
TIMING: 47–50; 3 minutes.

ASK: The application executes the function after validation. The result re-enters through a role=tool message with a matching tool_call_id. In this forced run, the host required the initial tool call.
DO: Invite a student to complete the sentence: the model requests; application code executes; the result returns to the model. Ask a second learner to explain the sample versus inference distinction.
OPTIONAL: If a pair has spare time before the break, they may set RUN_UNFORCED=True in the optional cell and observe automatic tool selection. Do not require everyone to repeat the model call.
MISCONCEPTION: A final response can sound plausible even when unsupported. The weather host withholds an answer if no tool executed; prompts alone are not execution evidence.
TIME CONTROL: Begin the five-minute break at minute 50.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 15. Five-minute break

SLIDE 15: Five-minute break
TIMING: 50–55; 5 minutes.

DO: Announce the return time and leave the slide visible. Use this interval to check one or two blocked students without delaying the class. Do not ask learners to begin a long model download.
PREPARE: Bring the MCP server source and Lab 3 cells into view in your own notebook. Keep Secrets closed. Confirm that the offline inspect command is available if inference is unreliable.
TIME CONTROL: Resume at minute 55 even if a few individual setups remain incomplete; use pairs. The next 15 minutes explain MCP before the 30-minute MCP lab.
NEXT: Define what the protocol standardizes.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 16. MCP: a standard tool connection

SLIDE 16: MCP: a standard tool connection
TIMING: 55–59; 4 minutes.

SAY: Model Context Protocol, or MCP, provides a standard way for a host's client to communicate with a server. In our example the server advertises a tool, the client discovers its contract, and the client invokes it with arguments.
ASK: Does MCP remove the weather API? Expected answer: no. The weather adapter remains behind the server. Does MCP create the model's reasoning? No, the host still communicates with a model service.
DO: Compare the direct-dispatch entry point with the MCP entry point at a high level. Explain that this course focuses on tools; resources and prompts are other MCP topics for later lessons.
CLARIFY: Standardized integration does not guarantee trustworthy external data, correct model output or permission to use any tool.
NEXT: Name the host, client and server using the illustration.
SOURCE: https://github.com/modelcontextprotocol/python-sdk/tree/v1.x

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 17. Host, client and server

SLIDE 17: Host, client and server
TIMING: 59–64; 5 minutes.

SAY: The host is the overall Python application. It owns the model conversation, validation and call budgets. Inside it, the MCP client manages the connection to the weather server. The server is a separate process advertising and executing the weather capability.
DO: Trace the connection between host and model service, then the separate client/server connection. Emphasize that the model does not directly talk to the stdio server.
ASK: Which process actually runs the weather adapter in Lab 3? Expected answer: the weather MCP server. Who still runs the conversation loop? The Python host.
DEMONSTRATE: Have one student play the model, one the host/client and one the server. The model asks the host for weather; the host relays a call; the server returns data. Keep the role-play under 90 seconds.
NEXT: Separate discovery from execution.
SOURCE: https://github.com/modelcontextprotocol/python-sdk/tree/v1.x
ILLUSTRATION: Conceptual generated architecture; one host/client and one server.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 18. Discovery comes before invocation

SLIDE 18: Discovery comes before invocation
TIMING: 64–67; 3 minutes.

SAY: Initialize establishes a protocol session. Listing tools gives the host a name, description and schema. A later call requests execution with arguments. The result is the evidence that comes back from the tool boundary.
ASK: If I can list get_current_weather, has weather already been fetched? Expected answer: no. Discovery proves that the server advertises the tool. It does not prove execution.
DO: Explain that --inspect in this package does both discovery and a sample call, so students will see both kinds of evidence. The client and server communicate over stdio inside the Colab runtime; stdout is reserved for protocol messages.
MISCONCEPTION: Printing a configuration or dry-run payload is different from establishing an MCP connection. The upcoming lab performs actual protocol requests.
NEXT: Compare responsibilities while keeping weather behavior constant.
SOURCE: https://github.com/modelcontextprotocol/python-sdk/tree/v1.x

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 19. What changes with MCP

SLIDE 19: What changes with MCP
TIMING: 67–70; 3 minutes.

SAY: The weather task remains the same. The key change is the contract and invocation boundary. With the direct function tool, the host defines and dispatches it. With MCP, the host discovers the server's tool and asks the server to execute it. The conversation remains in the host in our teaching implementation.
ASK: What code moved rather than disappeared? Expected answer: the weather adapter and tool execution moved behind the server process.
CLARIFY: The older provider-hosted LM Studio example manages orchestration differently because that host implements the loop. That is a hosting choice, not a universal MCP requirement. Save that comparison for a later lesson.
DO: Ask learners to leave their responsibility table partly blank until they see the live local trace in Lab 3.
TIME CONTROL: Move to the server source at minute 70.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 20. The weather MCP server

SLIDE 20: The weather MCP server
TIMING: 70–74; 4 minutes.

SAY: This is simplified pseudocode illustrating the shape of the server; the notebook contains the exact runnable source with typed arguments and sample-mode handling. The decorator exposes a tool, the function delegates to the adapter, and the server runs over stdio.
DO: Run the source display in Lab 3. Point to @mcp.tool(), city/country_code/units and execute_weather. Explain that the entry point starts the child server automatically; students do not need a second terminal or a public URL.
ASK: What would happen if we added ordinary print statements to server stdout? Expected answer: they could corrupt protocol communication. Diagnostic logging belongs on stderr.
NEXT: Students will inspect an actual session with no model key needed.
SOURCE: https://github.com/modelcontextprotocol/python-sdk/tree/v1.x

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 21. Lab 3A · Discovery and a sample call

SLIDE 21: Lab 3A · Discovery and a sample call
TIMING: 74–82; 8 minutes.

DO: Leave this slide up for eight minutes while students run the first Lab 3 cell. It prints the server source and invokes run_lab("03_mcp_agent.py", "--inspect").
COACH: Spend minutes one to three finding the tool name and description. During minutes four to six, inspect required arguments and returned sample data. In the final two minutes, ask each pair to distinguish listing from calling.
EXPECTED: [MCP tools/list] includes get_current_weather. Its schema is mapped into model parameters. [MCP tools/call] precedes a result containing demonstration weather and a mock flag. The server runs as a real child process.
FALLBACK: This lab needs no OpenAI key. If it fails, troubleshoot runtime preparation or the local MCP process rather than model quota. Pair students after one unsuccessful recovery attempt.
NEXT: Add the model loop to the same MCP connection.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 22. Lab 3B · The model uses the MCP tool

SLIDE 22: Lab 3B · The model uses the MCP tool
TIMING: 82–92; 10 minutes.

DO: Keep this slide on screen for ten minutes. Students run run_lab("03_mcp_agent.py", *model_options()). OpenAI uses real inference with sample weather; the fallback supplies fixed requests and still executes actual MCP calls.
COACH: During the first three minutes confirm discovery completes. During minutes four to seven ask students to trace the requested city/country/units into the server result. During the final three minutes have pairs compare the output with Lab 2 and complete their evidence checklist.
EXPECTED: The model requests the discovered weather tool, the host validates, the MCP client calls the server and returns its result. In OpenAI mode the next model turn explains the result. Sample values must remain labelled.
FALLBACK: Use run_lab("03_mcp_agent.py", "--offline") if inference is unavailable. Do not call that a completed live-model integration. The protocol exercise still counts.
TIME CONTROL: Stop experimentation at minute 92 and collect the responsibility comparison.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 23. Lab 3 debrief

SLIDE 23: Lab 3 debrief
TIMING: 92–97; 5 minutes.

ASK: Have pairs answer without opening the source. The server advertises the schema. The server process executes the weather function. The host controls conversation, validation, model access and budgets. A tools/call request together with its returned result provides invocation evidence; tools/list alone does not.
DO: Spend two minutes letting pairs fill the workbook comparison table and three minutes hearing answers. Encourage precise actor names instead of saying “the AI did it.”
MISCONCEPTION: The host still translates the discovered tool into the model's function-calling format. MCP does not eliminate every piece of integration code. It standardizes the client/server boundary.
CHECKPOINT: Ask one learner who used the fallback to state exactly which components were simulated and which ran. They should say model turns and weather were synthetic while the MCP process and connection were real.
NEXT: Locate these processes in the actual Colab deployment.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 24. Where the class code runs

SLIDE 24: Where the class code runs
TIMING: 97–100; 3 minutes.

SAY: Local means local to the Colab runtime. Your browser is on your laptop, while the Python host and MCP server run on the hosted machine. The host calls OpenAI for inference. In live-weather mode the server calls SerpApi. Sample mode skips that weather-provider request.
ASK: Would localhost:1234 in hosted Colab reach LM Studio on your laptop? Expected answer: no. We avoid tunnels in this core class and use OpenAI; the repository's LM Studio route is a separate local-computer exercise.
CREDENTIAL BOUNDARY: The OpenAI key authenticates the model client. The MCP child process receives the weather key when needed, not the model key. The question, schema and tool data do travel to OpenAI in that mode.
NEXT: Change one weather request and diagnose a controlled failure.
SOURCE: https://research.google.com/colaboratory/faq.html
ILLUSTRATION: Conceptual deployment artwork for this workshop.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 25. Pair challenge · Lisbon in Fahrenheit

SLIDE 25: Pair challenge · Lisbon in Fahrenheit
TIMING: 100–107; 7 minutes.

DO: Students run the notebook's pair-challenge cell. With OpenAI it asks the MCP agent for Lisbon, Portugal in Fahrenheit; without inference it repeats the direct fixture conversion. Allow four minutes to run and inspect, then three for pairs to explain.
EXPECTED: In the inference route, inspect whether the model supplied Lisbon, PT and fahrenheit. The synthetic weather generator returns the same base sample for any city, so a Lisbon label does not establish a real Lisbon observation. The expected conversion of the fixed 21°C value is 69.8°F.
ASK: What would you need before saying the answer is current weather? Expected answer: a successful live result, resolved location, units, observation/source evidence and comparison of final prose with the result.
FALLBACK: Run the direct Fahrenheit sample. Students should not supply a custom question to --offline expecting it to be interpreted; the fallback is a fixed scripted exercise.
NEXT: Run tests that reject invalid or unsupported behavior.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 26. Failure exercise · Two boundaries

SLIDE 26: Failure exercise · Two boundaries
TIMING: 107–113; 6 minutes.

DO: Ask students to run the notebook's test cell. The package currently has 16 tests. Allow two minutes for execution and four minutes to inspect tests/test_training.py and discuss two boundaries.
EXPECTED: The real stdio test makes an invalid-unit call and checks isError. The host test presents weather prose without a tool and expects the host to withhold it. These are different responsibilities: tool input validation versus evidence requirements in the host.
ASK: Does passing these tests prove a real OpenAI account has quota? No. Does it prove current weather accuracy? No. It checks the simulated or local boundary under test.
FALLBACK: If execution is blocked, inspect the test source with a partner and predict the result. Record observed versus predicted evidence accurately.
TIME CONTROL: Stop at minute 113 even if students want to inspect every test. The exit assessment is more important than a complete code tour.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 27. Exit ticket

SLIDE 27: Exit ticket
TIMING: 113–118; 5 minutes.

DO: Give students three minutes to write independently in workbook Section 11, then two minutes to compare with a partner. Do not reveal answers immediately.
ANSWER KEY: 1. No; the application or server must execute the request and return a result. 2. MCP standardizes the client/server exchange for discovery and invocation; the provider API and model conversation still exist. 3. The model connection settings and possibly provider-specific model API handling change; the weather tool/server can remain. 4. --mock-weather still uses a real model, while --offline uses fixed scripted turns; both use synthetic weather. 5. Explain the failure and do not invent weather.
ASSESSMENT: Four of five correct is a useful conceptual target; question one must be correct. Track practical evidence separately: sample run, real model loop, real MCP call. An offline-only student should mark model inference pending.
NEXT: Close with the three essential responsibilities and the next learning task.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 28. The responsibilities to remember

SLIDE 28: The responsibilities to remember
TIMING: 118–120; 2 minutes.

SAY: The central lesson is responsibility, not the number of commands you ran. We saw the same weather capability through a direct API, a function-calling loop and an MCP server. MCP made discovery and invocation standard at the client/server boundary.
DO: Ask students to save their notebook copy and retain their workbook notes. Remind them not to share credentials or secret outputs. Point to the repository link for the workbook and source.
ASK: Invite each student to write one next experiment, such as a different tool schema or a provider replacement. Keep responses brief.
NEXT CLASS: A later session can compare this local server with the provider-hosted SerpApi MCP example, or explore one business-role agent. Do not begin that material inside these final two minutes.
TIME CONTROL: End at minute 120. Optional appendix slides are reference material, not additional required lesson time.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 29. Instructor reference · Recovery order

SLIDE 29: Instructor reference · Recovery order
TIMING: Appendix · as needed; Outside the 120-minute core sequence.

USE: This is an instructor reference, not an extra segment in the two-hour timeline. Show it only when a common issue affects the class, then return to the current lab.
DO: Diagnose the earliest failing boundary. Undefined LAB or run_lab means preparation is incomplete. An MCP inspect failure is independent of OpenAI. An OpenAI authentication or quota failure does not require changing the weather function. A missing weather answer box should lead to a clear error, not guessed conditions.
FALLBACK COMMANDS: run_lab("02_custom_tool_agent.py", "--offline") and run_lab("03_mcp_agent.py", "--offline"). The second still uses real MCP. Mark inference pending.
FACILITATION: After one unsuccessful recovery attempt, pair the student with a ready learner. If time slips, omit unforced inference and live weather. Keep actual discovery/call evidence and the exit ticket.
PRIVACY: Close Secrets before screen sharing. Never ask learners to paste a key into chat or workbook notes.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md

---

## 30. Instructor reference · Live weather

SLIDE 30: Instructor reference · Live weather
TIMING: Appendix · optional; Outside the 120-minute core sequence.

USE: Rehearse this before class. If used, fit it into an existing lab block or offer it after the two-hour class. It is not required for conceptual completion.
DO: Add SERPAPI_KEY in Colab Secrets, enable notebook access and rerun Preparation C. Change RUN_LIVE_WEATHER to True in the optional cell and run once. The cell performs the direct call and, if OpenAI is configured, the MCP agent. Restore False afterward to prevent accidental repeated provider calls during Run all.
SAY: The OpenAI key provides inference access, while the SerpApi key provides weather-search access. A successful search may still contain no usable weather answer box.
CHECK: Compare requested and resolved location, temperature units, source and observation label. A retrieval timestamp is not the observation time. Use the returned publisher identity rather than assuming AccuWeather or Weather.com.
FALLBACK: Explain the actual provider error and return to sample mode. Never improvise a current temperature. Live calls consume provider quota and model inference consumes API usage.

SOURCE: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb
WORKBOOK: https://github.com/nuvear/Agents-Basics/blob/main/mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md