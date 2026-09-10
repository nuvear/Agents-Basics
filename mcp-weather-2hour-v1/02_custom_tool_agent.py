"""Lab 2: the application owns the function schema and direct dispatch."""
from agent_core import parser, run_agent, launch
from weather_contract import TOOL, execute_weather

async def main():
    args = parser(__doc__).parse_args()
    async def execute(name, arguments):
        print("[EXECUTION] Python calls the weather adapter directly")
        return execute_weather(arguments, mock=args.mock_weather or args.offline)
    print("FINAL ANSWER:", await run_agent(args, [TOOL], execute))

if __name__ == "__main__":
    launch(main())
