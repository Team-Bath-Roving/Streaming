import subprocess
import cv2
import numpy as np
import threading
import time
import sys
from signal import signal, SIGINT


running=True

def handler(signal_received, frame):
    # Handle any cleanup here
    stop()

signal(SIGINT, handler)

class StreamClient:
    thread=None
    process=None
    frame=None
    end=False
    options={
        "udp":f"?buffer_size=1000&fifo_size={3*4096}",
        "tcp":"?tcp_nodelay=1",
        "rtsp":"?buffer_size=1000&reorder_queue_size=100",
        "rtc":"",
    }
    def __init__(self,name,host,type,port,width,height,stereo=False):
        self.name=name
        self.host=host
        self.port=port
        self.type=type
        self.width=width
        self.height=height
        self.stereo=stereo
        if stereo:
            self.width*=2
        self.thread=threading.Thread(target=self.run,daemon=True)
        self.thread.start()
    def running(self):
        if not self.process.poll() is None:
            return False
        else:
            return True
    def start(self):
        if self.type in self.options:
            options=self.options[self.type]
        else:
            options=""
        command = ['ffmpeg',
            '-hide_banner',
            '-probesize','500000',
            '-analyzeduration','0',
            '-flags', 'low_delay',
            '-strict','experimental',
            '-hwaccel','auto',
            '-i', f'{self.type}://{self.host}:{self.port}{options}',
            '-vf',f"scale={self.width}:{self.height}",
            '-fflags', "nobuffer",
            '-f', 'rawvideo',      # Get rawvideo output format.
            '-pix_fmt', 'bgr24',   # Set BGR pixel format
            'pipe:']
        try:
            self.process.stdout.close()  # Closing stdout terminates FFmpeg sub-process.
            self.process.kill()
        except:
            pass
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    def read(self):
        raw_frame = self.process.stdout.read(self.width*self.height*3)
        self.frame= np.frombuffer(raw_frame, np.uint8).reshape((self.height, self.width, 3))
    def run(self):
        self.start()
        while(True):
            if self.end:
                break
            if not self.running():
                self.start()
            else:
                try:
                    self.read()
                except:
                    pass
    def display(self):
        try:
            cv2.imshow(self.name, self.frame)
        except Exception as e:
            pass
    def stop(self):
        self.end=True
        self.process.kill()
        self.process.terminate()
        self.process.stdout.close()  # Closing stdout terminates FFmpeg sub-process.
        
        



def stop():
    for s in clients:
        s.stop()
    cv2.destroyAllWindows()
    sys.exit()

clients=[
        StreamClient("Stereo","stereocam","tcp",8081,640,480,stereo=True),
        # StreamClient("Stereo","127.0.0.1","udp",8081,720,640,stereo=True),
        # StreamClient("USB","stereocam","tcp",8082,640,480),
        StreamClient("USB","127.0.0.1","udp",8082,640,480),
        # StreamClient("Stereo","stereocam","rtsp","8554/stream1",640,480,stereo=True),
        ]


def displayStreams(clients):
    k=''
    while (not k==ord('q')) and running:
        try:
            k=cv2.waitKey(0) & 0xFF
            for s in clients:
                if s.running:
                    s.display()
        except KeyboardInterrupt:
            stop()

displayStreams(clients)