import asyncio
import websockets
import base64


def decode_udp_packet(packet):
    print("Base64:", packet)
    packet = base64.decodebytes(packet)
    print("Server Sent:", packet)
    print("Decoded Packet:")
    for start, finish, seg in [(0, 1, 'Source Port'), (2, 3, 'Dest Port'), (4, 5, 'Data Length'), (6, 7, 'Checksum')]:
        print('%s:' % seg, int.from_bytes(packet[start:finish+1], 'little'))
    print("PayLoad:", packet[8:].decode("utf-8"))


async def main():
    uri = "ws://localhost:5612"
    async with websockets.connect(uri) as websocket:
        # After joining server will send client unique id.
        message = await websocket.recv()
        decode_udp_packet(message)
        return 0


if __name__ == "__main__":
    asyncio.run(main())
