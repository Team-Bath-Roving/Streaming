import subprocess
import cv2
import numpy as np
import threading
import time
import sys
import ffpyplayer
from ffpyplayer import 

class camera:
    thread=None
    frame=None
    player=None
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
    def start(self):
        options=""
        if self.type=="udp":
            options="?buffer_size=10000"
        elif self.type=="tcp":
            options="?tcp_nodelay=1"
        out_opts={
            'codec':'rawvideo',
            'width_out':self.width,
            'height_out':self.height,
        }
        url=f'{self.type}://{self.host}:{self.port}{options}'
        lib_opts = {'video_size':'320x240'}
        self.player=MediaPlayer(url,lib_opts)
        self.thread=threading.Thread(target=self.run,daemon=True)
    def run(self):
        self.frame=self.player.get_frame()
    def display(self):
        cv2.imshow(self.name, self.frame)



def stop():
    cv2.destroyAllWindows()
    sys.exit()

def runcamera(cam):
    cam.start()
    while True:
        if cv2.waitKey(16) & 0xFF == ord('q'):
            break
        cam.display()


cameras=[
        camera("Stereo","stereocam","tcp",8081,640,480,stereo=True),
        # camera("Stereo","127.0.0.1","udp",8081,640,480,stereo=True),
        # camera("USB","stereocam","tcp",8082,640,480),
        # camera("USB","127.0.0.1","udp",8082,640,480),
        # camera("self","127.0.0.1","rtsp",8554,640,480),
        # camera("self","127.0.0.1","udp",1234,640,480),
        # camera("self","127.0.0.1","rtp",5004,640,480),
        ]


def startCams():
    

    camthreads=[]
    for cam in cameras:
        camthreads.append(threading.Thread(target=runcamera,args=(cam,),daemon=True))

    for thread in camthreads:
        thread.start()
    while True:
        try:
            running=0
            for thread in camthreads:
                if thread.is_alive():
                    running+=1
            if running<1:
                stop()
            time.sleep(.3)
        except KeyboardInterrupt:
            stop()

startCams()