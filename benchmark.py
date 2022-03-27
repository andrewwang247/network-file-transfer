"""
Benchmark performance of file transfer.

Copyright 2022. Andrew Wang.
"""
from typing import Callable
from time import sleep
from threading import Thread
from queue import Queue
from logging import WARNING, basicConfig
import numpy as np
from click import command, option
from send import send
from receive import receive
# pylint: disable=no-value-for-parameter


def queue_wrapper(func: Callable[..., int], que: Queue) \
        -> Callable[..., None]:
    """Wrap function and put return value in queue."""
    def wrapped(*args, **kwargs):
        """Put return value in queue."""
        elapsed = func(*args, **kwargs)
        que.put(elapsed)
    return wrapped


@command()
@option('--size', '-s', type=int, required=True,
        help='The number of bytes to generate.')
def benchmark(size: int):
    """Benchmark performance of file transfer."""
    fname = 'random_bytes'
    wait_time = .15
    with open(fname, 'wb') as writer:
        writer.write(np.random.bytes(size))
    print(f'Wrote {fname} file with {size} bytes.')
    time_queue: Queue = Queue()
    basicConfig(level=WARNING)
    print('Executing receiver and sender.')
    receiver = Thread(target=queue_wrapper(receive, time_queue))
    sender = Thread(target=queue_wrapper(send, time_queue), args=(fname,))
    receiver.start()
    sleep(wait_time)
    sender.start()
    for thread in (sender, receiver):
        thread.join()
    time_one: int = time_queue.get()
    time_two: int = time_queue.get()
    elapsed = max(time_one, time_two) - 1e9 * wait_time
    print(f'Transfer time: {round(elapsed / 1e6)} ms.')


if __name__ == '__main__':
    benchmark()
