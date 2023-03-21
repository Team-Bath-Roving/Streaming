# find the camera name using v4l2-ctl --list-devices (or specify port with device=/dev/video...)
gst-launch-1.0 -v v4l2src device-name="UVC Camera" ! 'image/jpeg,width=640,height=480' ! tcpserversink host=0.0.0.0 port=8082
# UDP requires recieving IP to be set manually unless multicast used (which requires firewall config)
#gst-launch-1.0 -v v4l2src device-name="UVC Camera" ! 'image/jpeg,width=640,height=480' ! udpsink host=[TARGET] port=8082