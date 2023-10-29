#!/usr/bin/env python

import asyncio
import socket
import sys
import json
from websockets.server import serve

def print_stdout(str):
    sys.stdout.write(str + "\n")
    sys.stdout.flush()

async def send(websocket, command, data={}):
    json_data = json.dumps({"command": command, "data": data})
    await websocket.send(json_data)

UI_websocket = None
async def echo(websocket):
    global UI_websocket
    UI_websocket = websocket
    await send(websocket, "itemInserted", {"imageSrc": "C:\\Users\\alexg\\Documents\\code\\hackohio2023\\images\\knife\\knife1\\WIN_20231028_16_48_13_Pro.jpg", "title": "knife"})
    await asyncio.sleep(5)
    await send(websocket, "itemRemoved", {"imageSrc": "C:\\Users\\alexg\\Documents\\code\\hackohio2023\\images\\knife\\knife1\\WIN_20231028_16_48_13_Pro.jpg", "title": "knife"})
    async for message in websocket:
        print_stdout(message)
        

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
asyncio.run(main())
