 .\ffplay tcp://stereocam:8081 -vf "setpts=N/32.4,scale=2592:972" -fflags nobuffer -flags low_delay -framedrop