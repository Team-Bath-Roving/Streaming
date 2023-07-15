# Camera-Streaming
Python scripts to send and recieve camera streams with low latency. The best I've got so far is 200ms!

## Client
FFMPEG is used to receive TCP, UDP/Multicast or RTSP streams from the given IP and port. The video encoding is detected and handled automatically by FFMPEG.  
The resulting frames are decoded into an RGB frame buffer using hardware accelleration. This can be read by another process or displayed with OpenCV (see `exampleClient.py`). 
A watchdog thread is spawned upon instantiation which starts the stream and restarts if the connection is lost.  
### TCP
The IP should be set to the server IP
### UDP
THe IP should be set as localhost `127.0.0.1`, or the group number e.g. `239.1.1.1` in Multicast
### Requirements
- FFMPEG must be accessible via the command line, ensure it is added to PATH. On windows, this is done for you if you [install using Chocolatey](https://avpres.net/FFmpeg/install_Windows.html). Make sure to restart after so python can find it.
- OpenCV is required, install using `pip3 install opencv-python`

## Server
Picamera2 is used to access both USB and MIPI/CSI Pi cams and stream using h264 encoding.  
This provides low latency streaming over UDP/Multicast or TCP.  
### TCP
TCP streams tend to accumulate mutiple seconds of lag after a while as it waits for dropped frames, restart the client to reset this lag. 
Set the IP to localhost `127.0.0.1`. 
### UDP
I reccommend using UDP to minimise latency as missed packets are dropped. The IP should be that of the client machine. 
Multicast UDP allows multiple clients without using up bandwidth between the server and router. This also removes the need to know the client IP address. However this may require configuration on the router. In this case, set the IP to the group number, e.g. `239.1.1.1`.

### Requirements
- Picamera2, which should be [installed using apt](https://github.com/raspberrypi/picamera2) rather than pip.
- 
## Receiving on Android 
### TCP
Install [RPi Camera Viewer](https://play.google.com/store/apps/details?id=ca.frozen.rpicameraviewer&hl=en_AU)
Add the stream as TCP/IP, alternatively click the 3 dots and press Scan.
### UDP / Multicast using Gstreamer
Install [RaspberryPi Camera Viewer](https://play.google.com/store/apps/details?id=pl.effisoft.rpicamviewer2&hl=en_AU&pli=1)
Create a stream, check Advanced mode and use `udpsrc uri=udp://IP:PORT ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false`, replacing the IP and port as required. This could be recon
