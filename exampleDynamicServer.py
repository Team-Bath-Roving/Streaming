import sys

from StreamServer import StreamServer
from Comms.Output import Output

from signal import signal, SIGINT
 
from threading import Thread

SERVER_IP = '192.168.1.103'
# config
MULTICAST=False
PORT_MAIN_SERVER=5020
PORT_MAIN_STREAM=5021

MODEL="imx708_noir" # camera model name (find using libcamera-vid --list-cameras)
WIDTH=1200
HEIGHT=800
NAME="main_camera" # stream name for display in console

MODEL2="imx219"
PORT_SECONDARY_STREAM = 5030
PORT_SECONDARY_SERVER = 5031
NAME2="secondary_camera"

out=Output("None") # console output, with optional TCP forwarding

# Initialise stream
stream=StreamServer(out,MODEL,NAME,PORT_MAIN_STREAM) # system finds the camera based upon the model number (assumes no duplicates)
stream.configure(WIDTH,HEIGHT, framerate=30)
stream.start_server(SERVER_IP, PORT_MAIN_SERVER)
stream.set_bitrate(5000000)

stream2=StreamServer(out,MODEL2,NAME2,PORT_SECONDARY_STREAM)
stream2.configure(WIDTH, HEIGHT, framerate=30)
stream2.start_server(SERVER_IP, PORT_SECONDARY_SERVER)
stream2.set_bitrate(5000000)

#stream.set_controls({"AfMode": controls.AfModeEnum.Continuous}) # set a libcamera control

# exit handler
def handler(signal_received,frame):
    global run
    run = False

    stream.stop()
    stream2.stop()
    sys.exit()

def secondary_cam_run():
    stream2.run()

signal(SIGINT, handler)

secondary_cam_thread = Thread(target=secondary_cam_run)
secondary_cam_thread.start()

stream.run()
