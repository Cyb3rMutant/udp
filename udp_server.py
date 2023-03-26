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


def text_to_binary_array(text):
    binary_string = ""
    for char in text:
        # get decimal code of character from ASCII table
        decimal_code = ord(char)
        binary_byte = bin(decimal_code)[2:].zfill(
            8)  # convert decimal to binary byte
        binary_string += binary_byte

    # split binary string into 2-byte chunks
    binary_array = [binary_string[i:i+16]
                    for i in range(0, len(binary_string), 16)]
    if len(text) % 2:
        binary_array[-1] = binary_array[-1].ljust(16, '0')

    return binary_array


def sum_binary_strings(binary_strings):
    # convert each binary string to an integer and sum them up
    total = sum(int(b, 2) for b in binary_strings)

    # convert the total to a binary string and return it
    return bin(total)[2:].zfill(16)


def compute_checksum(source_port: int, dest_port: int, payload: str) -> int:
    source_port = bin(source_port)[2:].zfill(16)
    dest_port = bin(dest_port)[2:].zfill(16)
    length = bin(len(payload) + 8)[2:].zfill(16)
    payload = text_to_binary_array(payload)
    total = sum_binary_strings([source_port, dest_port, length]+payload)
    complement = "".join(["1" if bit == "0" else "0" for bit in total])
    print(complement)
    print(int(complement, 2))


compute_checksum(10, 42, "Welcome to IoT UDP Server")


async def main():
    uri = "ws://localhost:5612"
    async with websockets.connect(uri) as websocket:
        # After joining server will send client unique id.
        message = await websocket.recv()
        decode_udp_packet(message)
        return 0


if __name__ == "__main__":
    asyncio.run(main())
