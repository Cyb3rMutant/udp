import unittest
import websockets
import udp_server
from datetime import datetime


class TestSum(unittest.TestCase):
    def test_001_checksum_1_2_AB(self):
        udp_server.compute_checksum(1, 2, b"AB")

    def test_002_checksum_0_0_(self):
        udp_server.compute_checksum(0, 0, b"")

    def test_003_checksum_0_542_1111(self):
        udp_server.compute_checksum(0, 542, b"1111")


class TestAsync(unittest.IsolatedAsyncioTestCase):
    async def test_004_morse_server_echo(self):
        async with websockets.connect("ws://localhost:5612") as websocket:
            payload = udp_server.recv_and_decode_packet(websocket)

            self.assertEqual(payload, "Welcome to IoT UDP Server")

    async def test_005_morse_server_time(self):
        async with websockets.connect("ws://localhost:5612") as websocket:
            websocket.recv()
            udp_server.send_packet(websocket, 0, 542, b'1111')
            payload = udp_server.recv_and_decode_packet(websocket)

            self.assertEqual(payload, datetime.now().strftime("%H:%M:%S"))


unittest.main()
