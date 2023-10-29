#!/usr/bin/env python

import asyncio
import socket
import sys
from websockets.server import serve

# async def connect_stdin_stdout():
#     loop = asyncio.get_event_loop()
#     reader = asyncio.StreamReader()
#     protocol = asyncio.StreamReaderProtocol(reader)
#     await loop.connect_read_pipe(lambda: protocol, sys.stdin)
#     w_transport, w_protocol = await loop.connect_write_pipe(asyncio.streams.FlowControlMixin, sys.stdout)
#     writer = asyncio.StreamWriter(w_transport, w_protocol, reader, loop)
#     return reader, writer

def print_stdout(str):
    sys.stdout.write(str + "\n")
    sys.stdout.flush()

async def echo(websocket):
    async for message in websocket:
        print_stdout(message)
        await websocket.send(message)

def find_available_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

async def main():
    port = find_available_port()
    print_stdout(">> " + str(port))
    server = await serve(echo, "localhost", port)
    await server.wait_closed()
    print_stdout("server started")

print_stdout("server script started")
# main()
asyncio.run(main())
