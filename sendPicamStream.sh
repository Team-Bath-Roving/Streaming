# find available resolutions and framerates with libcamera-vid --list-cameras
libcamera-vid -t 0 --inline --width 1296 --height 972 -o - | nc -k -l 8081
# Alternatively, using gst (could change sink to RTSP or RTC to use udp)
libcamera-vid -t 0 --inline --width 1296 --height 972 -o - | gst-launch-1.0 fdsrc ! tcpsink host=0.0.0.0 port=8081