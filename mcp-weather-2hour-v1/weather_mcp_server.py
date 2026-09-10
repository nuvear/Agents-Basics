"""A real local MCP server; stdout belongs exclusively to the protocol."""
import sys
from typing import Literal
from mcp.server.fastmcp import FastMCP
from weather_contract import execute_weather

mcp = FastMCP("Classroom weather")

@mcp.tool()
def get_current_weather(city: str, country_code: str,
                        units: Literal["celsius", "fahrenheit"]) -> dict:
    """Get current weather for a city and country; samples are explicitly labelled."""
    return execute_weather({"city": city, "country_code": country_code, "units": units},
                           mock="--mock-weather" in sys.argv)

if __name__ == "__main__":
    mcp.run(transport="stdio")
