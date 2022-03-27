"""
Receive file over TCP socket.

Copyright 2022. Andrew Wang.
"""
from os import path
import socket as sock
from logging import debug, info, warning, basicConfig, INFO
from util import checksum, get_config, sock_manager, ensure_dir, timed


@timed
def receive():
    """Receive file over TCP socket."""
    port, size = get_config()
    host_ip = sock.gethostbyname(sock.gethostname())
    debug('Binding receiver to %s:%d', host_ip, port)
    with sock_manager(sock.socket(sock.AF_INET, sock.SOCK_STREAM)) as receiver:
        receiver.bind((host_ip, port))
        receiver.listen(5)
        info('Receiver is listening')
        sender_sock, addr = receiver.accept()  # pylint: disable=no-member
        info('Accepted connection from sender at %s:%s', *addr)
        with sock_manager(sender_sock) as client:
            filename = client.recv(size).decode('utf-8')
            client.send(f'Received file name {filename}'.encode('utf-8'))
            info('Received file name: %s', filename)
            filesize = int(client.recv(size).decode('utf-8'))
            client.send(f'Received file size {filesize}'.encode('utf-8'))
            info('Received file size: %d', filesize)
            recv_bytes = 0
            ensure_dir('bin')
            with open(path.join('bin', filename), 'wb') as writer:
                while recv_bytes < filesize:
                    msg = client.recv(
                        min(filesize - recv_bytes, 2**16), sock.MSG_WAITALL)
                    if not msg:
                        break
                    writer.write(msg)
                    recv_bytes += len(msg)
                    debug(
                        'Received %d bytes - total %d',
                        len(msg),
                        recv_bytes)
            info('Finished receiving file')
            debug('Received %d bytes from network', recv_bytes)
            recv_check = client.recv(size).decode('utf-8')
            debug('Received file checksum: %s', recv_check)
            file_check = checksum(path.join('bin', filename))
            debug('Actual file checksum: %s', file_check)
            if recv_check == file_check:
                client.send('success'.encode('utf-8'))
                info('Integrity check succeeded!')
            else:
                client.send('failure'.encode('utf-8'))
                warning('Integrity check failed!')


def driver():
    """Get config and pass parameters into receive."""
    basicConfig(level=INFO)
    exec_ns = receive()
    info('Execution time: %d ms', round(exec_ns / 1e6))


if __name__ == '__main__':
    driver()
