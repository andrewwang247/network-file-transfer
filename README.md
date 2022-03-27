# Network File Transfer

Transfer files via TCP socket between entities over a network.

How to successfully transfer a file:
1. Ensure `config.json` is set to your preferences. See `schema.json` for documentation.
2. Execute `receive.py` at the destination. Wait until you see the log message: `Receiver is listening`.
3. If you encounter an error about the address, retry with different `port` value in `config.json` at both source and destination.
4. Execute `send.py` at the source with a single command line argument giving the path to the target file.
5. Validate integrity of file with log message: `File integrity check succeeded!`.
6. If you receive an error log message `'File integrity check failed!'`, that means that the MD5 hash differs between source and destination. Try again at step 2.
7. Your transferred file will be stored in the `bin` directory. This will be created for you if it doesn't already exist.

## Sample Logs

Receiver logs:
```text
INFO:root:Receiver is listening
INFO:root:Accepted connection from sender at 127.0.0.1:59386
INFO:root:Received file name: random_bytes
INFO:root:Received file size: 500000000
INFO:root:Finished receiving file
INFO:root:Integrity check succeeded!
INFO:root:Execution time: 5570 ms
```

Sender logs:
```text
INFO:root:Sending file random_bytes
INFO:root:Establishing connection to 127.0.1.1:8000
INFO:root:Sending file metadata to receiver
INFO:root:Sending file contents to receiver
INFO:root:Finished sending file
INFO:root:Integrity check succeeded!
INFO:root:Execution time: 3428 ms
```

## Benchmarking

To test transfer speeds on the same machine, run the benchmark. A file called `random_bytes` will be generated and a file transfer will occur using 2 worker threads. The estimated transfer time will be reported.

```text
Usage: benchmark.py [OPTIONS]

  Benchmark performance of file transfer.

Options:
  -s, --size INTEGER  The number of bytes to generate.  [required]
  --help              Show this message and exit.
```

Example execution:
```text
Wrote random_bytes file with 10000000 bytes.
Executing receiver and sender.
Transfer time: 110 ms.
```