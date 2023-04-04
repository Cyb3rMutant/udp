import asyncio
import websockets
import base64
import time
import struct


async def recv_and_decode_packet(websocket: websockets.WebSocketClientProtocol):
    message = await websocket.recv()
    decode_udp_packet(message)


async def send_packet(websocket: websockets.WebSocketClientProtocol, source_port: int, dest_port: int, message: bytes):
    checksum = compute_checksum(source_port, dest_port, message)
    packet = struct.pack('<HHHH', source_port, dest_port,
                         len(message) + 8, checksum) + message
    packet = base64.encodebytes(packet)

    await websocket.send(packet)


def decode_udp_packet(packet: bytes):
    print("\n--- DECODE ---")
    print("Base64:", packet)
    packet = base64.decodebytes(packet)
    header = struct.unpack('<HHHH', packet[:8])
    payload = packet[8:].decode("utf-8")
    print("Server Sent:", packet)
    print("Decoded Packet:")
    print('Source Port:', header[0])
    print('Dest Port:', header[1])
    print('Data Length:', header[2])
    print('Checksum:', header[3])
    print("Payload:", payload)
    print("--- END OF DECODE ---\n")


def compute_checksum(source_port: int, dest_port: int, payload: bytes):
    header = struct.pack('<HHH', source_port, dest_port,
                         len(payload) + 8) + payload

    total_sum = 0
    for i in range(0, len(header), 2):
        total_sum += int.from_bytes(header[i:i+2], byteorder='big')

    ones_comp_sum = ~total_sum & 0xFFFF
    return ones_comp_sum


async def main():
    uri = "ws://localhost:5612"
    async with websockets.connect(uri) as websocket:
        await recv_and_decode_packet(websocket)
        while True:
            await send_packet(websocket, 0, 542, b'1111')
            await recv_and_decode_packet(websocket)
            time.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
