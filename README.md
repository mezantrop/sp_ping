# sp_ping.py
Send ICMP ECHO_REQUEST packets to network hosts. Simple ping implementation in Python

```
Usage:
  tspping.py -h host [-c count][-i interval][-m ttl][-t timeout][-ov]

Options:
  [-c count]\tSend count only packets. Default is 0xffffff
  [-i interval]\tInterval between two requests in seconds. Default is 1
  [-m ttl]\tTTL of outgoing packets. Default is 64
  [-t timeout]\tTimeout on socket. Default is 5
  [-o]\t\tSend one packet only (conditional ping) to get host Up/Down status
  [-v]\t\tBe verbose (show debug info of packets)
  
  Note! You must be root to run this program.
  ```
