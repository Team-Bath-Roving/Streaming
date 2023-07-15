# Camera-Streaming
Python scripts to send and recieve camera streams with low latency

## Client
FFMPEG is used to receive TCP, UDP/Multicast or RTSP streams from the given IP and port. The video encoding is detected and handled automatically by FFMPEG.  
The resulting frames are decoded into an RGB frame buffer using hardware accelleration. This can be read by another process or displayed with OpenCV (see `exampleClient.py`). 
A watchdog thread is spawned upon instantiation which starts the stream and restarts if the connection is lost.  
### Requirements
- FFMPEG must be accessible via the command line, ensure it is added to PATH. On windows, this is done for you if you [install using Chocolatey](https://avpres.net/FFmpeg/install_Windows.html). Make sure to restart after so python can find it.
- OpenCV is required, install using `pip3 install opencv-python`

## Server
Picamera2 is used to access both USB and MIPI/CSI Pi cams and stream using h264 encoding.  
This provides low latency streaming over UDP/Multicast or TCP.  
I reccommend using UDP to minimise latency as missed packets are dropped. TCP streams tend to accumulate mutiple seconds of lag after a while. 
Multicast UDP allows multiple clients without using up bandwidth between the server and router. This also removes the need to know the client IP address. However this requires configuration on the server end.  

### Requirements
- Picamera2, which should be [installed using apt](https://github.com/raspberrypi/picamera2) rather than pip.
