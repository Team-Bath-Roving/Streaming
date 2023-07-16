
import time

from StreamServer import StreamServer

from signal import signal, SIGINT
running=True

MCAST_GRP = '239.1.1.1'

stereo=StreamServer("ov5647") # system finds the camera based upon the model number (assumes no duplicates)
stereo.configure(1296,972)
#stereo.configure(640,480)
stereo.start(MCAST_GRP,5008,True) # using a multicast address 224.1.1.1:5008
stereo.set_bitrate(5000000)
i=10
while(running):
    time.sleep(0.01)
    i+=10
    stereo.set_exposure(i)



def handler(signal_received,frame):
    stereo.stop()
    running=False

signal(SIGINT, handler)
