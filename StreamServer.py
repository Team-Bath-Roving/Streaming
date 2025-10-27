import socket
import time
import sys
from PIL import Image
from io import BytesIO

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Encoder
from picamera2.outputs import FileOutput  # , FFMPEGOutput

from libcamera import controls

from Comms.Output import Output

from v4l2 import *

from picamera2.formats import ALL_FORMATS

ALL_FORMATS = ALL_FORMATS | {"MJPEG"}


class durationlimit:
    min = 33333


class StreamServer:
    cam_list = None
    active_cams = []

    def __init__(self, output: Output, model: str, name: str, port=None):
        self.output = output
        self.name = name
        self.model = model
        self.stream_port = port
        # List available devices
        self.usb = False
        self.cam = None
        self.idx = None
        if StreamServer.cam_list is None:  # first instantiation gets list of cameras
            StreamServer.scan()
        for idx, camera in enumerate(StreamServer.cam_list):
            # Find camera with corresponding model name
            # print(camera["Model"])
            if model in camera["Model"]:
                if not StreamServer.active_cams[
                    idx
                ]:  # skip this one if it's already been claimed
                    # Determine if CSI or USB (YUV or YUYV/MJPEG)
                    if "usb" in camera["Id"]:
                        self.usb = True
                    # Initialise camera
                    output.write("INFO", f"Found camera {model} at index {idx}", True)
                    self.cam = Picamera2(idx)
                    self.idx = idx
                    StreamServer.active_cams[idx] = True
                    # camera["Active"]=True # add key to show this has been claimed (allows multiple cams with same model)
        if self.cam is None:
            output.write("ERROR", f"Failed to find camera {model}", True)

    def handle_client(self, client_socket, addr):
        self.output.write("INFO", "Requested received.", True)
        pieces = [b""]
        total = 0

        timeout = time.monotonic()
        now = time.monotonic()

        while b"\n" not in pieces[-1] and total < 10_000 and (now - timeout) < 5.0:
            now = time.monotonic()
            pieces.append(client_socket.recv(2000))
            total += len(pieces[-1])
        self.data = b"".join(pieces)

        self.output.write(
            "INFO", "request received: " + self.data.decode("utf-8"), True
        )

        if self.data.decode("utf-8") == "IMG\n" and not self.cam is None:
            # Stop and Still configure
            self.cam.stop_recording()
            array = self.cam.switch_mode_and_capture_array(
                self.capture_config, "main", delay=5
            )

            image = Image.fromarray(array)
            _bytes = BytesIO()
            # Setting quality to 60/95
            image.save(_bytes, "JPEG", quality=60)

            data = _bytes.getvalue() + b"data_end\n"
            self.output.write(
                    "INFO", "Image size in bytes: " + str(sys.getsizeof(data)), True
                    )
            self.cam.start_recording(self.encoder, FileOutput(self.stream))
            
        elif self.cam is None:
            self.output.write("ERROR", "No camera to return image is detected.", True)
            data = b"data_end\n"
    
        # UPDATE IN FUTURE TO REQUEST SPECIFIC PORT?
        elif self.data.decode("utf-8") == "IP\n":
            self.output.write("INFO", "IP received, starting video feed to that IP.", True)
            # Try setting multicast to True and False.
            self.udp_sock.close()
            self.start_stream(addr, False)
            data = b"Starting stream.\n"

        else:
            self.output.write("ERROR", "No valid request was received.", True)
            data = b"data_end\n"

        client_socket.sendall(data)
        client_socket.close()

    def scan():
        StreamServer.cam_list = Picamera2.global_camera_info()
        for cam in StreamServer.cam_list:
            StreamServer.active_cams.append(False)
        print(StreamServer.cam_list)

    def configure(self, width, height, framerate=30, video_format=None):
        if not self.cam is None:
            config = {"size": (width, height)}
            controls = {"FrameRate": framerate}
            if not video_format is None:
                config["format"] = video_format
            # if self.usb:
            #     try:
            #         self.cam.configure(self.cam.create_video_configuration(config,controls={'FrameDurationLimits': (33333, 33333)}))
            #     except:
            #         pass
            # else:

            # for now use default config
            self.capture_config = self.cam.create_still_configuration()
            self.video_config = self.cam.create_video_configuration(config, controls=controls)

            self.cam.configure(self.video_config)
            self.output.write("INFO", f"Applied config to camera {self.model}", True)

    def start_stream(self, connection_ip, stream_port=None, multicast=True):
        if stream_port == None:
            stream_port = self.stream_port

        if not self.cam is None:
            if not self.usb:
                self.encoder = H264Encoder(100000, repeat=True, iperiod=5)
            else:
                self.encoder = Encoder()
                # self.encoder=H264Encoder(100000,repeat=True,iperiod=5)
            if multicast:
                self.udp_sock = socket.socket(
                    socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
                )
                self.udp_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
            else:
                self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_sock.connect((connection_ip, stream_port))
            self.stream = self.udp_sock.makefile("wb")
            if self.usb:
                self.cam.camera_ctrl_info["FrameDurationLimits"] = [
                    durationlimit(),
                    durationlimit(),
                ]
            self.cam.start_recording(self.encoder, FileOutput(self.stream))
            self.output.write(
                "INFO",
                f'Started UDP stream "{self.name}" from camera {self.model} to {connection_ip}:{stream_port}',
                True,
            )

    def start_server(self, server_ip, server_port):
        # Setup TCP server
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.bind((server_ip, server_port))

        # Maximum backlog of connections set to 3
        self.tcp_sock.listen(3)

        self.output.write("INFO", f"[+] Listening on port {server_ip} : {server_port}")

    def start_two(self, ip1, port1, ip2, port2):
        if not self.cam is None:
            if not self.usb:
                self.encoder = H264Encoder(100000, repeat=True, iperiod=5)
            else:
                self.encoder = Encoder()

            self.udp_sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            self.udp_sock1.connect((ip1, port1))
            self.udp_sock2.connect((ip2, port2))

            self.stream1 = self.udp_sock1.makefile("wb")
            self.stream2 = self.udp_sock2.makefile("wb")

            self.encoder.output = [FileOutput(self.stream1), FileOutput(self.stream2)]

            self.cam.start_encoder(self.encoder)
            self.cam.start()

    def stop(self):
        self.output.write("INFO", f"Stopping camera {self.model}")
        StreamServer.active_cams[self.idx] = (
            False  # set active flag false to unclaim camera
        )
        try:
            if self.cam is not None:
                self.cam.stop_recording()
                self.cam.close()
            self.udp_sock.close()
            self.tcp_sock.close()
        except Exception as e:
            self.output.write("EXCEPT", e, True)

    def set_bitrate(self, bitrate):
        if not self.cam is None:
            self.output.write(
                "INFO", f'Set bitrate to {bitrate} for stream "{self.name}"', True
            )
            self.encoder.bitrate = bitrate
            self.encoder.stop()
            self.encoder.start()

    def set_controls(self, controls_dict):
        if not self.cam is None:
            self.cam.set_controls(controls_dict)

    def set_exposure(self, exposure):
        self.set_controls({"ExposureTime": exposure})
        self.output.write(
            "INFO", f'Set exposure to {exposure} for stream "{self.name}"', True
        )

    def run(self):
        # When a client connects we receive the
        # client socket into the client variable, and
        # the remote connection details into the addr variable
        client, addr = self.tcp_sock.accept()
        print(f"[+] Accepted connection from: {addr[0]}:{addr[1]}")
        # spin up our client thread to handle the incoming data
        self.handle_client(client, addr)
