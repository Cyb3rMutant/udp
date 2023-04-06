# WebSocket Packet Decoder and Sender

## Introduction

The User Datagram Protocol (UDP) is a useful protocol in networking that is used alongside Transmission Control Protocol (TCP) as core members of the Internet Protocol (IP). Unlike TCP, UDP is a simple protocol that uses connectionless communication to send out requests to a server and can receive one or more responses. It employs a small-sized block, called a checksum, derived from the data being transmitted to track data integrity. Additional port numbers are utilized to address different functions at the server end since there is no explicit socket connection from the client to the server.

Previously, UDP was considered a less powerful alternative to TCP, which is useful for HTTP/2. However, with the development of the QUIC protocol and HTTP/3, which is based on UDP, it has gained renewed popularity. The key observation with QUIC was that modern webpages often have hundreds or thousands of referenced URLs to be loaded concurrently, and the failure-free nature of UDP at the IP layer means that one failing request does not block others.

This is a Python script for decoding and sending WebSocket packets using the `asyncio` and `websockets` libraries. It includes functions for decoding incoming packets and computing checksums for outgoing packets.

---

## Requirements

This script requires Python 3.5 or later, as well as the `asyncio` and `websockets` libraries.

To install these dependencies, run the following command:

```
pip install -r requirements
```

---

## Usage

To use this script, you will need to be connected to the remote development machince at `csctcloud.uwe.ac.u` and have forwarded port number `5612` to localhost where UDP packets are transmitted and received.
After that you can run it from the command line using:

```
python udp_server.py
```

The script will then connect to a WebSocket server on port `5612` and start sending and receiving packets.

---

## Functions

- ### `main() -> None`

  This asynchronous function is the main entry point of the program. It first establishes a WebSocket connection with the server on port `5612` using the `websockets.connect()` method and receives and decodes the welcome message from the server. It then enters an infinite loop where it sends a packet containing the message "1111" to the server every second using the `send_packet` function, and receives and decodes packets from the server using the `recv_and_decode_packet` function that have the current time as the message.

- ### `recv_and_decode_packet(websocket: websockets.WebSocketClientProtocol) -> None`

  This is an asynchronous function that takes a WebSocket connection as an argument and receives a packet from it in the form of a bytes string encoded in base64 then passes it to the `decode_udp_packet` function to be decoded to the user.

  An example of a received packet is the welcome message when the server first starts as follows:

  ```
  b'CgAqACEAyztXZWxjb21lIHRvIElvVCBVRFAgU2VydmVy'
  ```

- ### `decode_udp_packet(packet: bytes) -> None`

  This function takes a Base64-encoded bytes packet as input, decodes it using the `decodebytes` from the `base64` built in python module.

  The decoded bytes string consists of 2 main parts:

  - The header: it is made up of the first 8 bytes, and includes the source and destination ports, the length of the message and the checksum, with each being 2 bytes long
  - The payload: the actual data that was sent in the message.

  An example of a received packet is the welcome message when the server first starts as follows:

  ```
  b'\n\x00*\x00!\x00\xcb;Welcome to IoT UDP Server'
  ```

  The header is `b'\n\x00*\x00!\x00\xcb;'` and the payload is `b'Welcome to IoT UDP Server'`

  The function first extracts the header part using the `unpack` function from the `struct` built in module by passing the format string `'<HHHH'` which specifies little endian using `<` and 4 unsigned shorts with `H` then starts printing out the integer values of the header in order and finally prints the payload in `utf-8` encoding.

- ### `send_packet(websocket: websockets.WebSocketClientProtocol, source_port: int, dest_port: int, message: bytes) -> None`

  This asynchronous function sends a UDP packet over the WebSocket connection. It takes the WebSocket connection, source port, destination port, and message as input. The function first calculates the checksum of the packet using the `compute_checksum` function, then creates the packet by concatenating the header fields using the `pack` function of the `struct` built in module as discussed before and then appends the payload to it. Then it encodes the packet using `base64`. Finally, it sends the encoded packet over the WebSocket connection.

- ### `compute_checksum(source_port: int, dest_port: int, payload: bytes) -> int`

  This function takes in the source port, destination port and payload message as arguments, the purpose of this function is to compute the checksum of a packet.

The checksum is computed by first packing the source port, destination port, length of the payload plus 8 (the size of the header), and the payload into a binary packet using `struct.pack`. This binary packet is then processed by summing up the 16-bit words in the packet using one's complement addition. Specifically, the function iterates over the binary packet in steps of 2 bytes, converts each 2-byte segment to an integer using `int.from_bytes`, and adds the resulting integer to `total_sum`.

After the summing is done, the function takes the one's complement of the total sum and then bitwise ANDs `&` it with `0xFFFF` to keep only the lowest 16 bits of the one's complement sum, discarding any higher bits that may be present because in python an integer could be bigger than 16-bits. This final value is then returned.

The one's complement summing is used to detect errors in the packet transmission. The checksum computed at the sender side is sent along with the packet. The receiver recalculates the checksum using the same algorithm and compares it to the checksum sent with the packet. If the checksums do not match, the receiver knows that an error occurred during the transmission and the packet needs to be resent. 
