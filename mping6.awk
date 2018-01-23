#!/usr/bin/awk -f

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

# Quickly report alive IPv6 addresses on the network

# Usage:
#	mping6.awk [count=n] [interval=m] interface
#
# Options:
#	interface	Network interface to serach for IPv6 hosts on
#	[count=n]	Send count only pings. Default is 2
#	[interval=m]	Interval between pings. Default is 10

# 2018.01.23	v1.0	Mikhail Zakharov	Initial


function usage(ecode, emessage)	{
	print(emessage)
	print("Usage:\n"\
			"\tmping6.awk [count=n] [interval=m] interface\n"\
		"Options:\n"\
			"\tinterface\tNetwork interface to serach for IPv6 hosts on\n"\
			"\t[count=n]\tSend count only pings. Default is 2\n"\
			"\t[interval=m]\tInterval between pings. Default is 10")
	exit(ecode)
}

BEGIN {
	# Default options
	interface = ""		# Specified via command-line
	count = 2		# At least two requests are needed for interval to work
	interval = 10		# 10+ seconds should be enough to collect all answers

	# Command-line arguments processing
	for (opt = 1; opt < ARGC; opt++) {
		split(ARGV[opt], optvar, "=")
		if (!interface && !optvar[2]) interface = optvar[1]
		else if (optvar[1] == "count" && optvar[2]) count = optvar[2]
		else if (optvar[1] == "interval" && optvar[2]) interval = optvar[2]
		else usage(1, "Fatal: Wrong option was specified:" ARGV[opt])
	}
	if (!interface) usage(1, "You must specify an interface to scan network!\n")

	# Form the command to request multicast address ff02::1 on the interface
	cmd_ping = "ping6 ff02::1 -n -c "count" -i "interval" -I "interface
	# Actually execute the command and collect replies
 	while ((cmd_ping | getline ) > 0)
		if ($5 == "icmp_seq=0") {
			# 1-st only reply from each address is collected, stripped, printed
			split($4, address, "%")
			print(address[1])
		}

	close(cmd_ping)
	exit(0)
}
