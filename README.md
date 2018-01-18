# sp_ping.py
Send ICMP ECHO_REQUEST packets to network hosts. Simple ping implementation in Python

```
Usage:
  sp_ping.py -h host [-c count][-i interval][-m ttl][-t timeout][-ov]

Options:
  -h host           Target host to ping
  [-c count]        Send count only packets. Default is 0xffffff
  [-i interval]     Interval between two requests in seconds. Default is 1
  [-m ttl]          TTL of outgoing packets. Default is 64
  [-t timeout]      Timeout on socket. Default is 5
  [-o]              Send one packet only (conditional ping) to get host Up/Down status
  [-v]              Be verbose (show debug info of packets)
  
  Note! You must be root to run this program.
  ```
