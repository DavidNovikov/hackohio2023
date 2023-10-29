
import asyncio
import socket
import sys
import json
from websockets.server import serve
from yolo_demo import run_cv
import threading
from concurrent.futures import ThreadPoolExecutor

class Client:
    def __init__(self, websocket):
        self.websocket = websocket

    async def send(self, command, data={}):
        json_data = json.dumps({"command": command, "data": data})
        await self.websocket.send(json_data)
        self.print(f"sent {command} {data}")

    async def send_item_inserted(self, image_src, title):
        await self.send("itemInserted", {"imageSrc": image_src, "title": title})

    async def send_item_removed(self, title):
        await self.send("itemRemoved", {"title": title})

    def ping(self):
        self.print("ping")

    def print(self, str):
        sys.stdout.write(str + "\n")
        sys.stdout.flush()


def print_stdout(str):
    sys.stdout.write(str + "\n")
    sys.stdout.flush()

async def send(websocket, command, data={}):
    json_data = json.dumps({"command": command, "data": data})
    await websocket.send(json_data)

async def echo(websocket):
    client = Client(websocket)
    async for message in websocket:
        print_stdout(message)

        obj = json.loads(message)
        command = obj["command"]
        data = obj["data"]
        if command == "beginProcedure":
            loop = asyncio.get_event_loop()
            executor = ThreadPoolExecutor()
            loop.set_default_executor(executor)
            thread = threading.Thread(target=run_cv_thread, args=(client,))
            thread.start()
        
def run_cv_thread(client):
    asyncio.run(run_cv(client))

def find_available_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

async def main():
    port = find_available_port()
    print_stdout(">> " + str(port))
    print_stdout("server started")
    async with serve(echo, "localhost", port):
        await asyncio.Future()  # run forever

print_stdout("server script started")
asyncio.run(main())
