import queue
import socket
import time
from _thread import *
import threading
import json

from numpy import number


class PacketType:  # PacketType.PING
    SET_MTR = 0xA0
    ARM_MTR = 0xA1
    DISARM_MTR = 0xA2
    SET_CONTROL_MODE = 0xA3
    SET_ACRO = 0xA4
    SET_STABLE = 0xA5
    SET_PID = 0xA6
    GET_SENS = 0xB0
    GET_DEPTH = 0xB1
    GET_DEPTH_BYTES = 0xB2
    GET_VIDEO_BYTES = 0xB3
    GET_VIDEO = 0xB4
    SET_SIM = 0xC0
    ACK = 0xC1
    SET_ORIEN = 0xC3
    RST_SIM = 0xC4
    PING = 0xC5
    GET_CPS = 0xC6
    HIT_NGZ = 0xC7
    HIT_FZ = 0xC8
    CHK_AP = 0xC9
    ERROR = 0xCA
    REC_STRT = 0xD0
    REC_ST = 0xD1
    REC_RST = 0xD2
    GET_REC = 0xD3
    GET_DETE = 0xDE

    def get(val: int) -> str:  # PacketType.get(0xA5)
        for k, v in vars(PacketType).items():
            if v == val:
                return k


class PacketFlag:  # PacketType.PING
    NONE = 0
    SERVER_ECHO = 1
    DO_NOT_LOG_PACKET = 2
    TEST = 128

    def get(val: int) -> str:  # PacketFlag.get(1|2)
        flags = ""
        if val == 0:
            return "NONE "
        if val & PacketFlag.SERVER_ECHO:
            flags += "SERVER_ECHO "
        if val & PacketFlag.DO_NOT_LOG_PACKET:
            flags += "DO_NOT_LOG_PACKET "
        if val & PacketFlag.TEST:
            flags += "TEST "
        return flags


class Okon:
    def __init__(self, okon_client) -> None:
        self._okon_client = okon_client
        self.sens = {
            "imu": {
                "rot": {"x": 0, "y": 0, "z": 0},
                "rotSpeed": {"x": 0, "y": 0, "z": 0},
                "rotAccel": {"x": 0, "y": 0, "z": 0},
                "accel": {"x": 0, "y": 0, "z": 0},
            },
            "baro": 0,
            "detection": [],
        }
        self.control = {
            "mode": "unknown",
            "stable": {
                "rot": {"x": 0, "y": 0, "z": 0},
                "vel": {"x": 0, "y": 0, "z": 0},
                "depth": 1.3,
            },
            "acro": {
                "rotSpeed": {"x": 0, "y": 0, "z": 0},
                "vel": {"x": 0, "y": 0, "z": 0},
            },
            "manual": {
                "FLH": 0,
                "FLV": 0,
                "BLV": 0,
                "BLH": 0,
                "FRH": 0,
                "FRV": 0,
                "BRV": 0,
                "BRH": 0,
            },
        }
        self.orien = {"pos": {"x": 0, "y": 0, "z": 0}, "rot": {"x": 0, "y": 0, "z": 0}}
        self.pids = None  # pids get from syncing with the server

    def set_depth(self, depth: float, add: bool = False) -> None:
        old_depth = self.control["stable"]["depth"]
        if add:
            self.control["stable"]["depth"] += depth
        else:
            self.control["stable"]["depth"] = depth
        if old_depth != self.control["stable"]["depth"]:
            self._okon_client.send(
                PacketType.SET_STABLE,
                PacketFlag.DO_NOT_LOG_PACKET,
                json.dumps(self.control["stable"]),
            )

    def set_stable_vel(self, x: float = None, y: float = None, z: float = None) -> None:
        if x is not None:
            self.control["stable"]["vel"]["x"] = x
        if y is not None:
            self.control["stable"]["vel"]["y"] = y
        if z is not None:
            self.control["stable"]["vel"]["z"] = z
        self._okon_client.send(
            PacketType.SET_STABLE,
            PacketFlag.DO_NOT_LOG_PACKET,
            json.dumps(self.control["stable"]),
        )

    def arm_motors(self) -> None:
        self._okon_client.send(PacketType.ARM_MTR, PacketFlag.NONE)

    def disarm_motors(self) -> None:
        self._okon_client.send(PacketType.DISARM_MTR, PacketFlag.NONE)

    def setMode(self, mode: str) -> None:
        self.control["mode"] = mode
        self._okon_client.send(PacketType.SET_CONTROL_MODE, PacketFlag.NONE, mode)

    def reachedTargetRotation(self, delta):
        return (
            angle_difference(
                self.control["stable"]["rot"]["x"], self.sens["imu"]["rot"]["x"]
            )
            < delta
            and angle_difference(
                self.control["stable"]["rot"]["y"], self.sens["imu"]["rot"]["y"]
            )
            < delta
            and angle_difference(
                self.control["stable"]["rot"]["z"], self.sens["imu"]["rot"]["z"]
            )
            < delta
        )

    def reachedTargetDepth(self, delta):
        return (
            abs(self.control["stable"]["depth"] - self.sens["baro"] / 1000 / 9.81)
            < delta
        )

    def get_detection(self, className: str):
        return list(
            filter(
                lambda d: d["className"] == className and d["visibleInFrame"],
                self.sens["detection"],
            )
        )

    def set_stable_rot(
        self, x: float = None, y: float = None, z: float = None, add=False
    ) -> None:
        if x is not None:
            if add:
                self.control["stable"]["rot"]["x"] += x
            else:
                self.control["stable"]["rot"]["x"] = x
        if y is not None:
            if add:
                self.control["stable"]["rot"]["y"] += y
            else:
                self.control["stable"]["rot"]["y"] = y
        if z is not None:
            if add:
                self.control["stable"]["rot"]["z"] += z
            else:
                self.control["stable"]["rot"]["z"] = z
        self.control["stable"]["rot"] = angle_norm(self.control["stable"]["rot"])
        self._okon_client.send(
            PacketType.SET_STABLE,
            PacketFlag.DO_NOT_LOG_PACKET,
            json.dumps(self.control["stable"]),
        )


class Simulation:
    def __init__(self, okon_client) -> None:
        self._okon_client = okon_client
        self.checkpoints = None  # got from the server

    def reset(self) -> None:
        self._okon_client.send(PacketType.RST_SIM)

    def sync(self) -> None:
        self._okon_client.send(PacketType.SET_ORIEN, PacketFlag.DO_NOT_LOG_PACKET)
        self._okon_client.send(PacketType.GET_SENS, PacketFlag.DO_NOT_LOG_PACKET)
        self._okon_client.send(PacketType.SET_PID, PacketFlag.DO_NOT_LOG_PACKET)
        self._okon_client.send(
            PacketType.SET_CONTROL_MODE, PacketFlag.DO_NOT_LOG_PACKET
        )
        self._okon_client.send(PacketType.SET_STABLE, PacketFlag.DO_NOT_LOG_PACKET)
        self._okon_client.send(PacketType.GET_DETE, PacketFlag.DO_NOT_LOG_PACKET)


def angle_difference(angle1: float, angle2: float) -> float:
    diff = abs(((angle1 + 360) % 360) - ((angle2 + 360) % 360))
    return min(diff, 360 - diff)


def angle0360(angle: float) -> float:
    return (angle % 360 + 360) % 360


def angle180(angle: float) -> float:
    return angle - 360 if angle > 180 else angle


def angle_norm(a: dict) -> dict:
    x = angle180(angle0360(a["x"]))
    y = angle180(angle0360(a["y"]))
    z = angle180(angle0360(a["z"]))
    if abs(x) > 90:
        y = angle180(180 + y)
        x = angle180(angle0360(180 - x))
        z = angle180(angle0360(180 + z))
    return {"x": x, "y": y, "z": z}


class OkonClient:
    def __init__(self, ip, port, options=None, sync_interval=0.05, debug=True) -> None:
        self.okon = Okon(self)
        self.simulation = Simulation(self)

        self.ip = ip
        self.port = port
        self.debug = debug
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self._events = dict()
        self.syncTime = time.time()
        self.sync_interval = sync_interval
        self._to_send = queue.Queue()

    def connect(self) -> bool:
        if self.debug:
            print(f"Connecting to {self.ip}:{self.port}")
        try:
            self.socket.connect((self.ip, self.port))
            self.connected = True
            start_new_thread(self._comm_thread, ())
            start_new_thread(self._sync_thread, ())
            return True
        except Exception as err:
            print(f"failed to connect {err}")
            return False

    def send(
        self, packet_type: int, packet_flag: int = PacketFlag.NONE, json: str = None
    ) -> None:
        if json == None:
            self._to_send.put((packet_type, packet_flag, 0))
        else:
            json_bytes = json.encode()
            self._to_send.put((packet_type, packet_flag, len(json_bytes), json_bytes))

    def _sync_thread(self) -> None:
        while self.connected:
            while not self._to_send.empty():
                packet = self._to_send.get()
                self._send(packet)

            if time.time() > self.syncTime + self.sync_interval:
                self.syncTime = time.time()
                self.simulation.sync()
            else:
                time.sleep(0.001)  # avg ping ~2.7ms

    def _send(self, packet: tuple) -> None:
        self.socket.sendall(packet[0].to_bytes(1, byteorder="little"))
        self.socket.sendall(packet[1].to_bytes(1, byteorder="little"))
        self.socket.sendall(packet[2].to_bytes(4, byteorder="little"))
        if packet[2] > 0:
            self.socket.sendall(packet[3])
            if self.debug and packet[1] & PacketFlag.DO_NOT_LOG_PACKET == 0:
                print(
                    f'SENT {PacketType.get(packet[0])} {PacketFlag.get(packet[1])} dat:{packet[3].decode("utf-8") }'
                )
        else:
            if self.debug and packet[1] & PacketFlag.DO_NOT_LOG_PACKET == 0:
                print(f"SENT {PacketType.get(packet[0])} {PacketFlag.get(packet[1])}")

    def _receiveAll(self, n: int) -> bytes:
        buffer = b""
        while len(buffer) != n:
            buffer += self.socket.recv(n - len(buffer))
        return buffer

    def _comm_thread(self) -> None:
        while self.connected:
            packet_typeFlag = self._receiveAll(2)
            dataLength = int.from_bytes(self._receiveAll(4), "little")
            data_bytes = self._receiveAll(dataLength)
            self._handle_packet(packet_typeFlag[0], packet_typeFlag[1], data_bytes)

    def _handle_packet(self, packet_type: int, packet_flag: int, data_bytes: bytes):
        if self.debug and packet_flag & PacketFlag.DO_NOT_LOG_PACKET == 0:
            print(
                f'RECV {PacketType.get(packet_type)} {PacketFlag.get(packet_flag)} len:{len(data_bytes)} {data_bytes.decode("utf-8")[:40]}'
            )
        if packet_type == PacketType.SET_MTR:
            manual = json.loads(data_bytes.decode())
            self.okon.control["manual"] = manual
        elif packet_type == PacketType.ARM_MTR:
            pass
        elif packet_type == PacketType.DISARM_MTR:
            pass
        elif packet_type == PacketType.SET_CONTROL_MODE:
            self.okon.control["mode"] = data_bytes.decode()
        elif packet_type == PacketType.SET_ACRO:
            acro = json.loads(data_bytes.decode())
            self.okon.control["acro"] = acro
        elif packet_type == PacketType.SET_STABLE:
            stable = json.loads(data_bytes.decode())
            self.okon.control["stable"] = stable
        elif packet_type == PacketType.SET_PID:
            pids = json.loads(data_bytes.decode())
            self.okon.pids = pids
        elif packet_type == PacketType.GET_SENS:
            sens = json.loads(data_bytes.decode())
            sens["rot "] = angle_norm(sens["rot"])
            self.okon.sens["baro"] = sens["baro"]["pressure"]
            self.okon.sens["imu"] = sens
        elif packet_type == PacketType.GET_DEPTH:
            pass
        elif packet_type == PacketType.GET_DEPTH_BYTES:
            pass
        elif packet_type == PacketType.GET_VIDEO_BYTES:
            pass
        elif packet_type == PacketType.GET_VIDEO:
            pass
        elif packet_type == PacketType.SET_SIM:
            pass
        elif packet_type == PacketType.ACK:
            pass
        elif packet_type == PacketType.SET_ORIEN:
            orien = json.loads(data_bytes.decode())
            self.okon.orien["pos"] = orien["pos"]
            self.okon.orien["rot"] = angle_norm(orien["rot"])
        elif packet_type == PacketType.RST_SIM:
            self._emit_event("simRST")
        elif packet_type == PacketType.PING:
            self._emit_event("ping", data_bytes.decode())
        elif packet_type == PacketType.GET_CPS:
            checkpoints = json.loads(data_bytes.decode())
            self.simulation.checkpoints = checkpoints
        elif packet_type == PacketType.HIT_NGZ:
            ngz = json.loads(data_bytes.decode())
            self._emit_event("hitNGZ", ngz["id"])
        elif packet_type == PacketType.HIT_FZ:
            fz = json.loads(data_bytes.decode())
            self._emit_event("hitFZ", fz["id"])
        elif packet_type == PacketType.CHK_AP:
            pass
        elif packet_type == PacketType.ERROR:
            error = json.loads(data_bytes.decode())
            self._emit_event("error", error)
        elif packet_type == PacketType.REC_STRT:
            pass
        elif packet_type == PacketType.REC_ST:
            pass
        elif packet_type == PacketType.REC_RST:
            pass
        elif packet_type == PacketType.GET_REC:
            pass
        elif packet_type == PacketType.GET_DETE:
            self.okon.sens["detection"] = json.loads(data_bytes.decode())
        else:
            self._emit_event("packet", (packet_type, packet_flag, data_bytes))

    def disconnect(self) -> None:
        self.connected = False
        self.socket.close()
        self._emit_event("disconnect")

    def on_event(self, name: str, func) -> None:
        if name in self._events:
            self._events[name].append(func)
        else:
            self._events[name] = list()
            self._events[name].append(func)

    def _emit_event(self, name: str, args=None) -> None:
        if name in self._events:
            for e in self._events[name]:
                start_new_thread(e, (args,))
