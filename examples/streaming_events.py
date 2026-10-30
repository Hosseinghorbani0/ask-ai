import asyncio

from ask_ai import Completed, OpenAI, TextDelta


async def main():
    async for event in OpenAI().ask_stream_events_async("Write a short story"):
        if isinstance(event, TextDelta):
            print(event.text, end="", flush=True)
        elif isinstance(event, Completed):
            print("\nCompleted")


asyncio.run(main())
