"""Lab 2: the application owns the function schema and direct dispatch."""
from agent_core import parser, run_agent, launch
from runtime_secrets import should_mock_weather
from weather_contract import TOOL, execute_weather

async def main():
    args = parser(__doc__).parse_args()
    mock = should_mock_weather(mock_weather=args.mock_weather, offline=args.offline)
    async def execute(name, arguments):
        print("[EXECUTION] Python calls the weather adapter directly")
        print("[WEATHER SOURCE]", "sample/mock" if mock else "live SerpApi")
        return execute_weather(arguments, mock=mock)
    print("FINAL ANSWER:", await run_agent(args, [TOOL], execute))

if __name__ == "__main__":
    launch(main())
