import asyncio
from typing import List, Union, Callable
from functools import partial
from threading import Thread
from queue import Queue, Empty
from concurrent.futures import Future
import atexit
import time

from discord.ext import commands


class CommandQueue:
    """
    A queue for sending messages given context within discord
    """

    def __init__(self) -> "CommandQueue":
        self._queue: Queue = Queue()
        self._loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self._thread: Thread = Thread(target=self._thread_target)
        self._stopped: bool = False
        self._thread.start()

        atexit.register(self.stop)

    def _thread_target(self) -> None:
        while not self._stopped:
            try:
                command = self._queue.get(block=True, timeout=0.05)
                if asyncio.iscoroutinefunction(command):
                    future: Future = asyncio.run_coroutine_threadsafe(
                        command, loop=self._loop
                    )
                    future.add_done_callback(partial(print, "Finished another command"))
                else:
                    command()
            except Empty:
                time.sleep(0.05)

    def _message_done_callback(
        self, command: Union[Callable, asyncio.coroutine]
    ) -> None:
        pass

    async def _send_message(self, ctx: commands.Context, msg_data: List[str]) -> None:
        async with ctx.typing():
            for msg in msg_data:
                await ctx.send(msg)

    def put_message(self, ctx: commands.Context, msg_data: List[str]) -> None:
        """
        Puts a message send into the queue
        """
        self._queue.put_nowait(partial(self._send_message, ctx, msg_data))

    def put(self, command: Union[Callable, asyncio.coroutine]) -> None:
        """
        Puts a generic Callable or coroutine into the queue
        """
        self._queue.put_nowait(command)

    def stop(self) -> None:
        """
        Stops the thread from sending messages
        """
        self._stopped = True
        self._thread.join()
