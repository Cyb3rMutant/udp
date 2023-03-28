import asyncio
import websockets
import base64
import time

async def recv_and_decode_packet(websocket):
    message = await websocket.recv()
    decode_udp_packet(message)


def decode_udp_packet(packet):
    packet = base64.decodebytes(packet)

    print("PayLoad:", packet[8:].decode("utf-8"))


async def send_packet(websocket, source_port, dest_port, message):
    checksum = compute_checksum(source_port, dest_port, message)
    final = source_port.to_bytes(2, 'little') + dest_port.to_bytes(2, 'little') + (8).to_bytes(2, 'little') + checksum.to_bytes(2, 'little') + message

    await websocket.send(base64.encodebytes(final))


def text_to_binary_array(text):
    binary_string = ""
    for char in text:
        # get decimal code of character from ASCII table
        binary_byte = bin(char)[2:].zfill(8)  # convert decimal to binary byte
        binary_string += binary_byte

    # split binary string into 2-byte chunks
    binary_array = [binary_string[i:i+16] for i in range(0, len(binary_string), 16)]

    if len(text) % 2:
        binary_array[-1] = binary_array[-1].ljust(16, '0')

    return binary_array


def sum_binary_strings(binary_strings):
    # convert each binary string to an integer and sum them up
    total = sum(int(b, 2) for b in binary_strings)

    # convert the total to a binary string and return it
    return bin(total)[2:].zfill(16)


def compute_checksum(source_port: int, dest_port: int, payload: bytes) -> int:
    source_port = bin(source_port)[2:].zfill(16)
    dest_port = bin(dest_port)[2:].zfill(16)
    length = bin(len(payload) + 8)[2:].zfill(16)
    payload = text_to_binary_array(payload)
    total = sum_binary_strings([source_port, dest_port, length]+payload)
    return int("".join(["1" if bit == "0" else "0" for bit in total]), 2)


compute_checksum(10, 42, b"Welcome to IoT UDP Server")

async def main():
    uri = "ws://localhost:5612"
    async with websockets.connect(uri) as websocket:
        # After joining server will send client unique id.
        await recv_and_decode_packet(websocket)
        while True:
            await send_packet(websocket, 0, 542, b'1111')
            await recv_and_decode_packet(websocket)
            time.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
