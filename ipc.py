import os
import sys
import json
import struct
import asyncio
import tempfile

import platform # OS detection.

import uuid     # For generating nonse.

import time

from enum import IntEnum

# Global variables

reader: asyncio.StreamReader = None
writer: asyncio.StreamWriter = None

is_connected = asyncio.Event()

message_queue = asyncio.Queue()


class OpCode(IntEnum):
    Handshake = 0,
    Frame = 1,
    Close = 2,
    Ping = 3,
    Pong = 4,

def pack_message(opcode:int, message:str) -> bytes:
    """
    Pack message into IPC frame.
    """

    # [UINT opcode][UINT length][payload]
    header = struct.pack('<II', opcode, len(message))
    return header + message.encode("utf-8")

def get_ipc_address(pipe_id=0) -> str:
    """
    Get Discord instance IPC address.
    """

    ipc_prexix = 'discord-ipc-'

    ipc = f"{ipc_prexix}{pipe_id}"

    # TODO: Scan IPC pipe id.

    if platform.system() in ['Linux', 'Darwin']:
        base_dir = os.environ.get('XDG_RUNTIME_DIR') or os.environ.get('TMP') or os.environ.get('TEMP') or os.environ.get('/tmp') or tempfile.gettempdir()

    elif platform.system() == 'Windows':
        base_dir = '\\\\?\\pipe'
    
    else:
        raise NotImplemented

    return os.path.join(base_dir, ipc)

async def connect(appid:str, loop=None):
    """
    Connect to Discord
    """
    global reader, writer

    is_connected.clear()

    if not loop:
        loop = asyncio.get_event_loop()

    async def _connect():

        global reader, writer

        if platform.system() in ['Linux', 'Darwin']:
            reader, writer = await asyncio.open_unix_connection(get_ipc_address(), loop=loop)

        elif platform.system() == 'Windows':

            reader = asyncio.StreamReader(loop=loop)
            writer, _ = await loop.create_pipe_connection(
                lambda: asyncio.StreamReaderProtocol(reader, loop=loop), 
                get_ipc_address())

    await _connect()

    # Send handshake.
    frame = pack_message(OpCode.Handshake, 
            json.dumps({'v': 1, 'client_id': str(appid)})
        )
    writer.write(frame)
    if platform.system() != "Windows": await writer.drain()

    # Read response
    read_header = await reader.read(8)

    opcode, length = struct.unpack('<II', read_header)

    read_frame = await reader.read(length)

    if opcode != 2:
        print("Connected.")
        is_connected.set()

async def disconnect(appid:str, loop=None):
    frame = pack_message(OpCode.Close, 
            json.dumps({'v': 1, 'client_id': str(appid)})
        )
    writer.write(frame)
    if platform.system() != "Windows": await writer.drain()

async def writer_loop():

    while True:

        # Wait until connect.
        await is_connected.wait()

        # Send message
        frame = await message_queue.get()
        writer.write(frame)
        if platform.system() != "Windows": await writer.drain()

async def reader_loop():
    while True:
        await is_connected.wait()

        # Read response
        read_header = await reader.read(8)

        opcode, length = struct.unpack('<II', read_header)
        print(opcode, length)

        read_frame = await reader.read(length)
        print(read_frame)

# TODO: Update loop.

def message_enqueue(opcode:int, message:dict):

    nonce = str(uuid.uuid4())
    message['nonce'] = nonce

    message_queue.put_nowait(
            pack_message(opcode, 
                json.dumps(message)
            )
        )
    return

if __name__ == "__main__":


    # python ipc.py <client_id> [<activity json file>]

    appid = sys.argv[1]
    
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'r', encoding="utf-8") as f:
            activity = json.load(f)
    else:
        activity = {
            "type": 0,
            "details": "Sample detail field.",
            "state": "Sample state field.",
        }

    # Append timestamp.
    activity["timestamps"] = {
        "start": int(time.time()),
        #"end": end
    }

    pid = os.getpid()
    loop = asyncio.get_event_loop()

    loop.run_until_complete(connect(appid, loop=loop))

    reader_task = loop.create_task(reader_loop())
    writer_task = loop.create_task(writer_loop())

    message_enqueue(OpCode.Ping, {})  #PING

    payload_args = {}
    payload_args["pid"] = pid
    payload_args["activity"] = activity

    payload = {}
    payload["cmd"] = "SET_ACTIVITY"
    payload["args"] = payload_args

    message_enqueue(OpCode.Frame, payload)

    try:
        loop.run_forever()
    except KeyboardInterrupt as ex:
        print("Closing")
        loop.run_until_complete(disconnect(appid, loop=loop))
        reader_task.cancel()
        writer_task.cancel()



