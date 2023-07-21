import subprocess
import cv2
import numpy as np
# import multiprocessing as mp
import threading

NO_CROP=0
LEFT_CROP=1
RIGHT_CROP=2

class StreamClient:
    thread=None
    process=None
    frame=None
    end=False
    crop=None
    options={
        "udp":f"?buffer_size=1000&fifo_size={3*4096}",
        "tcp":"?tcp_nodelay=1",
        "rtsp":"?buffer_size=1000&reorder_queue_size=100",
        "rtp":"",
    }
    def __init__(self,name,host,type,port,width,height,rotate=0,stereo=False,crop=NO_CROP):
        self.crop=crop
        self.rotate=rotate
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
            '-pix_fmt', 'rgb24',   # Set BGR pixel format
            'pipe:']
        try:
            self.process.stdout.close()  # Closing stdout terminates FFmpeg sub-process.
            self.process.kill()
            self.process.terminate()
        except:
            pass
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
    def read(self):
        raw_frame = self.process.stdout.read(self.width*self.height*3)
        # print(len(raw_frame))
        raw_frame = np.frombuffer(raw_frame, np.uint8).reshape((self.height, self.width, 3))
        if self.crop==LEFT_CROP:
            self.frame=raw_frame[:,:self.width//2,:]
        elif self.crop==RIGHT_CROP:
            self.frame=raw_frame[:,self.width//2:,:]
        else:
            self.frame=raw_frame
        self.frame=np.rot90(self.frame,self.rotate)
        # print(len(self.frame))
        return self.frame
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
        if not self.frame is None:
            try:
                cv2.waitKey(1)
                cv2.imshow(self.name, self.frame)
            except Exception as e:
                print(e)
    def stop(self):
        self.end=True
        self.process.stdout.close()  # Closing stdout terminates FFmpeg sub-process.
        self.process.kill()
        self.process.terminate()
        


