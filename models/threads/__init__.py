import asyncio
import threading


def run_async(coroutime, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coroutime(*args))
    loop.close()