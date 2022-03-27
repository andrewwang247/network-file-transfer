"""
Get configuration from config.json.

Copyright 2022. Andrew Wang.
"""
from typing import Callable, Tuple, Dict
from os import path, mkdir
from time import perf_counter_ns
from json import load
from contextlib import contextmanager
from socket import socket, SHUT_RDWR, setdefaulttimeout
from hashlib import md5
from logging import debug
from jsonschema import validate  # type: ignore


def get_config() -> Tuple[int, int]:
    """Get configuration from config json."""
    debug('Loading config')
    with open('config.json', encoding='utf-8') as wrapper:
        config: Dict[str, int] = load(wrapper)
    with open('schema.json', encoding='utf-8') as wrapper:
        schema: dict = load(wrapper)
    debug('Validating config against JSON schema')
    validate(config, schema)
    port = config['port']
    size = config['size']
    timeout = config['timeout']
    debug('Using port %d for communications', port)
    debug('Sending and receiving maximum of %d bytes at a time', size)
    debug('Setting default socket timeout to %d seconds', timeout)
    setdefaulttimeout(timeout)
    return port, size


def ensure_dir(dir_name: str):
    """Ensure directory exists for receiving files."""
    if not path.exists(dir_name):
        mkdir(dir_name)


@contextmanager
def sock_manager(sock: socket):
    """Context manager that handles shutdown + closing of socket."""
    identifier = id(sock)
    debug('Socket open %d', identifier)
    yield sock
    sock.shutdown(SHUT_RDWR)
    debug('Socket shutdown %d', identifier)
    sock.close()
    debug('Socket close %d', identifier)


def checksum(fname: str) -> str:
    """Compute MD5 checksum of file."""
    with open(fname, 'rb') as reader:
        content = reader.read()
    return md5(content).hexdigest()


def timed(func: Callable[..., None]) -> Callable[..., int]:
    """Wrap no-return function in execution timer."""
    def wrapper(*args, **kwargs) -> int:
        """Time func execution in nanoseconds."""
        begin = perf_counter_ns()
        func(*args, **kwargs)
        end = perf_counter_ns()
        return end - begin
    return wrapper
