import asyncio

from agents import Agent, Runner, WebSearchTool, trace


async def main():
    agent = Agent(
        name="Sports Results Agent",
        instructions="You are a helpful agent that searches the web for sports results.",
        tools=[WebSearchTool()],
    )

    #with trace("Sports Results Agent"):
    async for chunk in Runner.run_streamed(
            agent,
            "who won the 2025 US Open Golf champiionship and where was it played",
        ):
        print(chunk, end="", flush=True)
    # The New York Giants are reportedly pursuing quarterback Aaron Rodgers after his ...


if __name__ == "__main__":
    asyncio.run(main())