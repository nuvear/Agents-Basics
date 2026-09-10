"""Lab 3: discover the schema and execute through a real local MCP connection."""
import os
import sys
from contextlib import asynccontextmanager
from datetime import timedelta
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from agent_core import ROOT, parser, run_agent, launch

@asynccontextmanager
async def weather_session(mock):
    # Only the weather credential is passed to the server, never the model key.
    env = {key: os.environ[key] for key in ("PATH", "SYSTEMROOT", "TEMP", "TMP", "SERPAPI_KEY", "HTTP_TIMEOUT_SECONDS") if key in os.environ}
    params = StdioServerParameters(command=sys.executable,
        args=[str(ROOT / "weather_mcp_server.py")] + (["--mock-weather"] if mock else []), env=env)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=45)) as session:
            await session.initialize()
            yield session

async def main():
    p = parser(__doc__)
    p.add_argument("--inspect", action="store_true", help="Real MCP discovery and sample call without any model.")
    args = p.parse_args()
    async with weather_session(args.mock_weather or args.offline or args.inspect) as session:
        listed = await session.list_tools()
        tools = [{"type": "function", "function": {"name": t.name, "description": t.description or "", "parameters": t.inputSchema}}
                 for t in listed.tools if t.name == "get_current_weather"]
        if not tools:
            raise ValueError("Weather tool not discovered.")
        print("[MCP tools/list]", tools)
        async def execute(name, arguments):
            print("[MCP tools/call]", name)
            result = await session.call_tool(name, arguments)
            return {"isError": result.isError, "content": [c.model_dump() for c in result.content]}
        if args.inspect:
            print(await execute("get_current_weather", {"city": "Tokyo", "country_code": "JP", "units": "celsius"}))
        else:
            print("FINAL ANSWER:", await run_agent(args, tools, execute))

if __name__ == "__main__":
    launch(main())
