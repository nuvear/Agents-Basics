"""Lab 3: discover the schema and execute through a real local MCP connection."""
import os
import sys
from contextlib import asynccontextmanager
from datetime import timedelta
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from agent_core import ROOT, parser, run_agent, launch
from runtime_secrets import should_mock_weather

def mcp_read_timeout() -> timedelta:
    """Keep the MCP client waiting longer than a live SerpApi scrape + retries."""

    timeout = float(os.getenv("SERPAPI_TIMEOUT_SECONDS", os.getenv("HTTP_TIMEOUT_SECONDS", "60")) or 60)
    retries = int(os.getenv("SERPAPI_RETRIES", "2") or 2)
    seconds = timeout * (retries + 2) + 30
    return timedelta(seconds=max(180, seconds))


@asynccontextmanager
async def weather_session(mock):
    # Only the weather credential is passed to the server, never the model key.
    env = {key: os.environ[key] for key in ("PATH", "SYSTEMROOT", "TEMP", "TMP", "SERPAPI_KEY", "HTTP_TIMEOUT_SECONDS", "SERPAPI_TIMEOUT_SECONDS", "SERPAPI_RETRIES", "SERPAPI_NO_CACHE") if key in os.environ}
    params = StdioServerParameters(command=sys.executable,
        args=[str(ROOT / "weather_mcp_server.py")] + (["--mock-weather"] if mock else []), env=env)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=mcp_read_timeout()) as session:
            await session.initialize()
            yield session

async def main():
    p = parser(__doc__)
    p.add_argument("--inspect", action="store_true", help="Real MCP discovery and sample call without any model.")
    args = p.parse_args()
    mock = should_mock_weather(
        mock_weather=args.mock_weather,
        offline=args.offline,
        inspect=args.inspect,
    )
    async with weather_session(mock) as session:
        listed = await session.list_tools()
        tools = [{"type": "function", "function": {"name": t.name, "description": t.description or "", "parameters": t.inputSchema}}
                 for t in listed.tools if t.name == "get_current_weather"]
        if not tools:
            raise ValueError("Weather tool not discovered.")
        print("[MCP tools/list]", tools)
        print("[WEATHER SOURCE]", "sample/mock" if mock else "live SerpApi")
        async def execute(name, arguments):
            print("[MCP tools/call]", name)
            print("[EXECUTION] MCP server runs the weather adapter")
            try:
                result = await session.call_tool(name, arguments)
            except Exception:
                return {
                    "ok": False,
                    "error_type": "mcp_tool_error",
                    "message": (
                        "MCP weather call timed out or failed. "
                        "A live SerpApi scrape can exceed the previous 45s client limit; rerun."
                    ),
                }
            return {"isError": result.isError, "content": [c.model_dump() for c in result.content]}
        if args.inspect:
            print("[MCP INSPECT] sample discovery call; no model and no live weather")
            print(await execute("get_current_weather", {"city": "Tokyo", "country_code": "JP", "units": "celsius"}))
        else:
            print("FINAL ANSWER:", await run_agent(args, tools, execute))

if __name__ == "__main__":
    launch(main())
