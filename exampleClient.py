import subprocess
import cv2
import numpy as np
import threading
import time
import sys
from signal import signal, SIGINT
from StreamClient import StreamClient

running=True

def handler(signal_received, frame):
    # Handle any cleanup here
    stop()

signal(SIGINT, handler)


def stop():
    print("STOPPING")
    for s in clients:
        s.stop()
    cv2.destroyAllWindows()
    sys.exit()


# To recieve non multicast UDP, set IP to 127.0.0.1
# Stereo simply doubles the output width
# Output resolution defined here is independent of what is transmitted
clients=[
        # StreamClient("Stereo","stereocam","tcp",8081,720,640,stereo=True),
        StreamClient("Stereo","127.0.0.1","udp",8081,720,640,stereo=True),
        # StreamClient("USB","stereocam","tcp",8082,640,480),
        # StreamClient("USB","127.0.0.1","udp",8082,640,480),
        # StreamClient("Stereo","stereocam","rtsp","8554/stream1",640,480,stereo=True),
        ]


def displayStreams(clients):
    while (not (cv2.waitKey(1) & 0xFF)==ord('q')) and running:
        for s in clients:
            s.display()
    stop()


displayStreams(clients)