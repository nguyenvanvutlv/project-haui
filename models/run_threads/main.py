import asyncio


def run_async(coroutime, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coroutime(*args))
    loop.close()

# thread = threading.Thread(target = run_async,
#                 args = (self.enhance_audio, self.current_audio.path))
# thread.start()