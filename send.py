"""
Send file over TCP socket.

Copyright 2022. Andrew Wang.
"""
from sys import argv
from os import path
import socket as sock
from logging import debug, info, warning, basicConfig, INFO
from util import get_config, sock_manager, checksum, timed


@timed
def send(fname: str):
    """Send file over TCP socket."""
    port, size = get_config()
    info('Sending file %s', fname)
    filename = path.basename(fname)
    filesize = path.getsize(fname)
    debug('Resolved filename %s with size %d', filename, filesize)
    host_ip = sock.gethostbyname(sock.gethostname())
    info('Establishing connection to %s:%d', host_ip, port)
    with sock_manager(sock.socket(sock.AF_INET, sock.SOCK_STREAM)) as sender:
        sender.connect((host_ip, port))
        info('Sending file metadata to receiver')
        for metadata in (filename, str(filesize)):
            sender.send(metadata.encode('utf-8'))
            resp = sender.recv(size).decode('utf-8')
            debug('Response: %s', resp)
        info('Sending file contents to receiver')
        with open(fname, 'rb') as reader:
            sent = sender.sendfile(reader)  # pylint: disable=no-member
        info('Finished sending file')
        debug('Sent %d bytes into network', sent)
        file_check = checksum(fname)
        debug('Sending file checksum: %s', file_check)
        sender.send(file_check.encode('utf-8'))
        check = sender.recv(size).decode('utf-8')
        assert check in ('success', 'failure'), 'Invalid checksum response.'
        if check == 'success':
            info('Integrity check succeeded!')
        else:
            warning('Integrity check failed!')


def driver():
    """Get config and pass parameters into send."""
    basicConfig(level=INFO)
    assert len(argv) == 2, 'Sender accepts a single command line argument.'
    fname = argv[1]
    assert path.isfile(fname), 'Argument must be a file.'
    exec_ns = send(fname)
    info('Execution time: %d ms', round(exec_ns / 1e6))


if __name__ == '__main__':
    driver()
