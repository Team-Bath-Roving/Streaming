import cv2
import sys
from StreamClient import StreamClient, ServerClient

def stop():
    print("STOPPING")
    for s in clients:
        s.stop()
    cv2.destroyAllWindows()
    sys.exit()


SERVER_IP = '192.168.1.103'

PORT_MAIN_SERVER=5020
PORT_SECONDARY_SERVER=5031

PORT_MAIN_STREAM=5021
PORT_SECONDARY_STREAM=5030

WIDTH=1200
HEIGHT=800

server_client_main = ServerClient(SERVER_IP, PORT_MAIN_SERVER)
server_client_secondary = ServerClient(SERVER_IP, PORT_SECONDARY_SERVER)
server_client_main.start_stream()
server_client_secondary.start_stream()

# To recieve non multicast UDP, set IP to 127.0.0.1
# Stereo simply doubles the output width
# Output resolution defined here is independent of what is transmitted
clients=[
        # StreamClient("Stereo","stereocam","tcp",8081,720,640,stereo=True),
        StreamClient("Stereo",SERVER_IP,"udp",PORT_MAIN_STREAM,WIDTH,HEIGHT,stereo=True),
        StreamClient("Stereo",SERVER_IP,"udp",PORT_SECONDARY_STREAM,WIDTH,HEIGHT,stereo=True)
        # StreamClient("USB","stereocam","tcp",8082,640,480),
        # StreamClient("USB","127.0.0.1","udp",8082,640,480),
        # StreamClient("Stereo","stereocam","rtsp","8554/stream1",640,480,stereo=True),
        ]

running = True

def displayStreams(clients):
    while (not (cv2.waitKey(1) & 0xFF)==ord('q')) and running:
        for s in clients:
            s.display()
    stop()

## IMAGE REQUEST EXAMPLES: returns numpy array, can be converted to Python Image
main_pic = server_client_main.get_picture()
secondary_pic = server_client_secondary.get_picture()

displayStreams(clients)
