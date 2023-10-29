#!/usr/bin/env python

import asyncio
import socket
from websockets.server import serve

async def echo(websocket):
    async for message in websocket:
        print(message)
        await websocket.send(message)

def find_available_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

async def main():
    port = find_available_port()
    print(">>", port)
    async with serve(echo, "localhost", port):
        print("server started")
        await asyncio.Future()  # run forever

print("server script started")
# main()
asyncio.run(main())

