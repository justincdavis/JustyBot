import asyncio
from typing import List, Union, Callable, Optional, Deque, Dict, Any
from threading import Thread
from concurrent.futures import Future
import atexit
import time
from dataclasses import dataclass
from collections import deque

from discord.ext import commands


class CommandQueue:
    """
    A queue for sending messages given context within discord
    """

    def __init__(self) -> "CommandQueue":
        self._queue: Deque = deque()
        self._loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self._thread: Thread = Thread(target=self._process_command_loop, daemon=True)
        self._loop_thread: Thread = Thread(target=self._run_loop, daemon=True)
        self._stopped: bool = False
        self._task_cache: Deque[Future] = deque(maxlen=50)
        self._time_slice: float = 0.001

        atexit.register(self.stop)

        self._thread.start()
        self._loop_thread.start()

    def _cleanup(self):
        self._stopped = True
        for task in self._task_cache:
            task.cancel()

    @dataclass
    class Command:
        """
        A more complex object for the command queue which includes extra flags
         such as preempt, priority, and handler
        """

        cmd_func: Callable
        preempt: bool = False
        priority: int = 1
        handler: Optional[Callable] = None

        def __str__(self):
            return f"{self.cmd_func.__module__}.{self.cmd_func.__qualname__}"

    def _process_command(self, command_obj: Command, args: List, kwargs: Dict) -> None:
        print(
            f"Processing: {command_obj} with args: {args} and kwargs: {kwargs}"
        )
        if asyncio.iscoroutinefunction(
            command_obj.cmd_func
        ):  # if it is an async function
            new_future: Future = asyncio.run_coroutine_threadsafe(
                command_obj.cmd_func(*args, **kwargs), loop=self._loop
            )
            new_future.add_done_callback(
                lambda f: print(
                    f"Completed: {command_obj} with args: {args} and kwargs: {kwargs}"  # type: ignore
                )
            )
            self._task_cache.append(new_future)
        else:  # typical sync function
            command_obj.cmd_func(*args, **kwargs)

        # If a handler is present, call it when the command has been processed
        if command_obj.handler is not None:
            command_obj.handler()

    # loop for processing commands. Uses the time slice determined in the contructor for its maximum rate.
    def _process_command_loop(self) -> None:
        try:
            while not self._stopped:
                start_time = time.perf_counter()
                try:
                    command_obj, args, kwargs = self._queue.popleft()
                    if args is None:
                        args = []
                    if kwargs is None:
                        kwargs = {}

                    self._priority_sort_queue()

                    self._process_command(command_obj, args, kwargs)
                # TODO, perform logging on these exceptions
                except IndexError as e:
                    # this exception is expected since we expect the deque to not have elements sometimes
                    if str(e) != "pop from an empty deque":
                        # if the exception makes it here, it is unexpected
                        print(e)
                finally:
                    end_time = time.perf_counter() - start_time
                    if end_time < self._time_slice:
                        time.sleep(self._time_slice - end_time)
        finally:
            self._cleanup()

    def _priority_sort_queue(self):
        # Reorder according to priority (highest priority at the end of the queue)
        # Sorted function keeps order within same priorities
        self._queue = deque(
            sorted(
                self._queue,
                key=lambda cmd_tup: cmd_tup[0].priority,
                reverse=True,
            )
        )

    # method for running telemetry data
    def _run_loop(self):
        self._loop.run_forever()

    async def _send_message(self, ctx: commands.Context, msg_data: List[str]) -> None:
        async with ctx.typing():
            for msg in msg_data:
                await ctx.send(msg)

    def put(
        self,
        obj: Union[Callable, Command],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Used to put functions/methods in a queue for execution in a separate thread asynchronously or otherwise
        :param obj: A callable function/method which will get executed in the command loop thread
        :type obj: Union[Callable, AbstractDrone.Command]
        :param args: The arguments for the function/method
        :param kwargs: The keyword arguments for the function/method
        """

        command_obj: CommandQueue.Command

        if callable(obj):
            command_obj = self.Command(obj)
        else:
            command_obj = obj

        if command_obj.preempt:
            command_obj.priority = 1

        print(f"User called: {command_obj}, putting call in queue")
        if command_obj.preempt:
            self._queue.appendleft((command_obj, args, kwargs))
        else:
            self._queue.append((command_obj, args, kwargs))

        self._priority_sort_queue()

    def put_message(self, ctx: commands.Context, msg_data: List[str]) -> None:
        """
        Puts a message send into the queue
        """
        self.put(self._send_message, ctx, msg_data)

    def stop(self) -> None:
        """
        Stops the thread from sending messages
        """
        self._stopped = True
        try:
            self._thread.join(timeout=2*self._time_slice)
            self._loop_thread.join(timeout=2*self._time_slice)
        except RuntimeError:
            pass
