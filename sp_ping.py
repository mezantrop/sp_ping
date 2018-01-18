#!/usr/bin/env python3

# Copyright (c) 2018 Mikhail Zakharov <zmey20000@yahoo.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
 
# Usage:
#   sp_ping.py -h host [-c count][-i interval][-m ttl][-t timeout][-ov]
#
# Options:
#   [-c count]        Send count only packets. Default is 0xffffff
#   [-i interval]     Interval between two requests in seconds. Default is 1
#   [-m ttl]          TTL of outgoing packets. Default is 64
#   [-t timeout]      Timeout on socket. Default is 5
#   [-o]              Send one packet only (conditional ping) to get host Up/Down status
#   [-v]              Be verbose (show debug info of packets)
#  
# Note! You must be root to run this program.

# 2018.01.18	v1.0	Mikhail Zakharov <zmey20000@yahoo.com>	Initial

import socket
import struct
import time
import os
import sys
import getopt
 
 
# Defaults can be overridden by getopt() below
count = 0xffffff                            # Number of pings to send
timeout = 5                                 # Socket timeout in seconds
ttl = 64                                    # TTL
interval = 1                                # Interval between pings
verbose = False                             # Make less noise
 
 
def usage(ecode=1, etext=''):
    if etext:
        print(etext, file=sys.stderr)
 
    print('Send ICMP ECHO_REQUEST packets to network hosts, simple implementation in Python\n'
          '\n'
          'Usage:\n'
          '\tspping.py -h host [-c count][-i interval][-m ttl][-t timeout][-ov]\n'
          '\n'
          'Options:\n'
          '\t[-c count]\tSend count only packets. Default is 0xffffff\n'
          '\t[-i interval]\tInterval between two requests in seconds. Default is 1\n'
          '\t[-m ttl]\tTTL of outgoing packets. Default is 64\n'
          '\t[-t timeout]\tTimeout on socket. Default is 5\n'
          '\t[-o]\t\tSend one packet only (conditional ping) to get host Up/Down status\n'
          '\t[-v]\t\tBe verbose (show debug info of packets)\n'
          '\n'
          'Note! You must be root to run this program.\n'
          )
 
    exit(ecode)
 
 
def clk_chksum(icmp_packet):
    """Calculate ICMP packet checksum"""
 
    packet_len = len(icmp_packet)
    summ = 0
    for i in range(0, packet_len, 2):
        if i + 1 < packet_len:
            # Fold 2 neighbour bytes into a number and add it to the summ
            summ += icmp_packet[i] + (icmp_packet[i + 1] << 8)
        else:
            # If there is an odd number of bytes, fake the second byte
            summ += icmp_packet[i] + 0
    # Add carry bit to the sum
    summ = (summ >> 16) + (summ & 0xffff)
    # Truncate to 16 bits and return the checksum
    return ~summ & 0xffff
 
 
def ping(target_host, sock, sequence=0, ttl=64, pings=0xffffff):
    """Ping target: send ECHO_REQUEST and get ECHO_RESPONSE"""
 
    # Packet header definition
    iphdr_len = 60                  # Max is 60, but in our case it should be 20 bytes. Adjust it after recv()
    icmphdr_len = 8                 # ICMP header length is 8 bytes
    icmp_type = 8
    icmp_code = 0
    icmp_checksum = 0
    icmp_id = os.getpid() & 0xffff  # Generate ID field using PID converted to 16 bit
    # Some ICMP payload examples. Do not make them too long:
    icmp_data = b'\x50\x49\x4E\x47\x2D\x50\x4F\x4E\x47\x20\x46\x52\x4F\x4D' \
                b'\x20\x5A\x4D\x45\x59\x32\x30\x30\x30\x30\x40\x59\x41\x48' \
                b'\x4F\x4F\x2E\x43\x4F\x4D'
    # icmp_data = b'12345678' + b'1234567890' * 4
 
    data_len = len(icmp_data)
 
    send_timestamp = time.time()                                                    # Packet creation time
    out_packet = struct.pack('BBHHHQ{}s'.format(data_len), icmp_type, icmp_code,
                             icmp_checksum, icmp_id, sequence, int(send_timestamp), icmp_data)
    icmp_checksum = clk_chksum(out_packet)
    out_packet = struct.pack('BBHHHQ{}s'.format(data_len), icmp_type, icmp_code,
                             icmp_checksum, icmp_id, sequence, int(send_timestamp), icmp_data)
 
    # Send ICMP packet to the target_host; Specify any portnumber just to make sendto() happy
    sock.sendto(out_packet, (target_host, 1))
 
    if verbose:
        print('Ping: {pkt}, {host}'.format(pkt=struct.unpack('BBHHHQ', out_packet[:-data_len]), host=target_host))
 
    while True:
        # Let the buffer_size be the packet maximum size we expect
        buffer_size = iphdr_len + icmphdr_len + struct.calcsize('Q') + data_len     # calcsize('Q'): timestamp size
 
        try:
            reply, host = sock.recvfrom(buffer_size)
        except socket.timeout:
            print('Host is down')
            return 1
        except:
            print('Fatal: General error in recvfrom()')
            exit(1)
 
        recv_timestamp = time.time()
 
        vihl = struct.unpack('B', reply[:1])[0]             # First byte consists of 4 bit IP Version and 4 bit IHL
        ihl = ((vihl << 4) & 0xff) >> 4                     # Cut out the IHL (Internet Header Length) value
        iphdr_len = 4 * ihl                                 # and recalculate IP header length
 
        # Actual IP packet size of the reply
        packet_size = iphdr_len + icmphdr_len + struct.calcsize("Q") + data_len
        in_packet = struct.unpack('BBHHHQ{}s'.format(data_len), reply[iphdr_len:iphdr_len + packet_size])
 
        if not in_packet[0] and in_packet[3]:
            # This is Echo Reply packet (zero in in_packet[0]) to our request with ID (in_packet[3])
 
            if verbose:
                print('Pong: {pkt}, {host}, {size}, {time:0.4f}'.format(
                    pkt=in_packet[:-1], host=host[0], size=packet_size,
                    time=(recv_timestamp - send_timestamp) * 1000))
            else:
                if pings == 1:
                    print('Host is up')
                else:
                    print('{size} bytes from {host}: seq={seq} ttl={ttl} time={time:0.4f} ms'.format(
                        size=packet_size, host=host[0], seq=sequence, ttl=ttl,
                        time=(recv_timestamp - send_timestamp) * 1000))
 
            return 0
 
 
# ----------------------------------------------------------------------------------------------------------------------
try:
    opts, args = getopt.getopt(sys.argv[1:], 'h:c:i:m:ot:v')
except getopt.GetoptError as err:
    usage(1, str(err))
 
if not opts:
    usage(1, 'Fatal: You must specify all mandatory arguments to run the program')
 
for opt, arg in opts:
    try:
        if opt == '-h':                                 # Target host to ping
            target = arg
        elif opt == '-c':                               # -c count
            count = int(arg)
        elif opt == '-i':                               # -i interval
            interval = int(arg)
        elif opt == '-m':                               # -m ttl
            ttl = int(arg)
        elif opt == '-o':                               # -o one packet only
            count = 1
        elif opt == '-t':                               # -t timeout
            timeout = int(arg)
        elif opt == '-v':                               # -v verbose
            verbose = True
        else:
            pass                                        # Unknown options are detected by getopt() exception above
    except ValueError:
        usage(1, 'Fatal: Wrong argument: "{}" to: "{}" option is specified'.format(arg, opt))
 
 
icmp = socket.getprotobyname('icmp')
try:
    # Sorry guys, non-privileged ICMP does not work on most of OS:
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, icmp)
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
except PermissionError:
    print('Fatal: You must be root to send ICMP packets')
    exit(1)
except:
    print('Fatal: General error in socket()')
    exit(1)
 
s.settimeout(timeout)
s.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
 
# Main ping-pong loop
for seq in range(count):
    result = ping(target, s, sequence=seq, ttl=ttl, pings=count)
    if count == 1:
        # Condition ping: Host up or down
        exit(result)
 
    time.sleep(interval)
 
s.close()
