import asyncio


def async_to_sync(function, *args):
    loop = asyncio.get_event_loop()
    coroutine = function(*args)
    loop.run_until_complete(coroutine)

