import socket
import time

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Encoder
from picamera2.outputs import FileOutput#, FFMPEGOutput

from libcamera import controls

from Comms.Output import Output

from v4l2 import *

from picamera2.formats import ALL_FORMATS

ALL_FORMATS=ALL_FORMATS | {"MJPEG"}

class durationlimit:
    min=33333

class StreamServer:
    cam_list=None
    active_cams=[]
    def __init__(self,output:Output,model:str,name:str):
        self.output=output
        self.name=name
        self.model=model
        # List available devices
        self.usb=False
        self.cam=None
        self.idx=None
        if StreamServer.cam_list is None: # first instantiation gets list of cameras
            StreamServer.scan()
        for idx,camera in enumerate(StreamServer.cam_list):
            # Find camera with corresponding model name
            # print(camera["Model"])
            if model in camera["Model"]:
                if not StreamServer.active_cams[idx]: # skip this one if it's already been claimed
                    # Determine if CSI or USB (YUV or YUYV/MJPEG)
                    if "usb" in camera["Id"]:
                        self.usb=True
                    # Initialise camera
                    output.write("INFO",f"Found camera {model} at index {idx}",True)
                    self.cam=Picamera2(idx)
                    self.idx=idx
                    StreamServer.active_cams[idx]=True
                    # camera["Active"]=True # add key to show this has been claimed (allows multiple cams with same model)
        if self.cam is None:
            output.write("ERROR",f"Failed to find camera {model}",True)
    def scan():
        StreamServer.cam_list=Picamera2.global_camera_info()
        for cam in StreamServer.cam_list:
            StreamServer.active_cams.append(False)
        print(StreamServer.cam_list)
    def configure(self,width,height,video_format=None):
        if not self.cam is None:
            config={"size":(width,height)}
            if not video_format is None:
                config["format"]=video_format
            # if self.usb:
            #     try:
            #         self.cam.configure(self.cam.create_video_configuration(config,controls={'FrameDurationLimits': (33333, 33333)}))
            #     except:
            #         pass
            # else:
            self.cam.configure(self.cam.create_video_configuration(config))
            self.output.write("INFO",f"Applied config to camera {self.model}",True)
    def start(self,ip,port,multicast=True):
        if not self.cam is None:
            if not self.usb:
                self.encoder=H264Encoder(100000,repeat=True,iperiod=5)
            else:
                self.encoder=Encoder()
                # self.encoder=H264Encoder(100000,repeat=True,iperiod=5)
            if multicast:
                self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
            else:
                self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
            self.sock.connect((ip, port))
            self.stream = self.sock.makefile("wb")
            if self.usb:
                self.cam.camera_ctrl_info["FrameDurationLimits"]=[durationlimit(),durationlimit()]
            self.cam.start_recording(self.encoder, FileOutput(self.stream))
            self.output.write("INFO",f"Started UDP stream \"{self.name}\" from camera {self.model} to {ip}:{port}",True)
    def stop(self):
        self.output.write("INFO", f"Stopping camera {self.model}")
        StreamServer.active_cams[self.idx]=False # set active flag false to unclaim camera
        try:
            self.cam.stop_recording()
            self.cam.close()
            self.sock.close()
        except Exception as e:
            self.output.write("EXCEPT",e,True)
    def set_bitrate(self,bitrate):
        if not self.cam is None:
            self.output.write("INFO",f"Set bitrate to {bitrate} for stream \"{self.name}\"",True)
            self.encoder.bitrate=bitrate
            self.encoder.stop()
            self.encoder.start()
    def set_controls(self,controls_dict):
        if not self.cam is None:
            self.cam.set_controls(controls_dict)
    def set_exposure(self,exposure):
        self.set_controls({"ExposureTime": exposure})
        self.output.write("INFO",f"Set exposure to {exposure} for stream \"{self.name}\"",True)
