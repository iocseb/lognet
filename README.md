# lognet
> Write a log of network activity

This program monitors all processes of a system for network connections and writes logs to /var/log/netlog/. These logs can be helpful as:
- additional forensic information
- base info for configuring firewalls
- troubleshooting info

This project makes use of Giampaolo Rodola's great work on the PSUTIL (https://github.com/giampaolo/psutil) library.

## Installing / Getting started
The only external library that is being used in this project is [PSUTIL](https://github.com/giampaolo/psutil). You can install it with:
```commandline
pip3 install psutil
```
Once you have installed psutil into your (virtual) runtime environment, you can start lognet with:
```commandline
python3 lognet.py
```

TODO: Package and distribute to PyPi

### Requirements
So far the code has only been tested with Python v3.10 on Linux. However, it should also run on Python v3.6+.

## Command Line Arguments
```commandline
usage: lognet.py [-h] [-i I] [-clog CLOG] [-plog PLOG] [-ipv {4,6}] [-p {udp,tcp}] [--omit-self-conns] [--omit-privnet-conns]

options:
  -h, --help            show this help message and exit
  -i I                  interval (in seconds) for connection enumeration (default: 3s)
  -clog CLOG            output file for connections log (default: /var/log/netlog/connections.log)
  -plog PLOG            output file for processes list (default: /var/log/netlog/processes.log)
  -ipv {4,6}            filters by internet protocol version (if omitted, it includes both)
  -p {udp,tcp}          filters by protocol (if omitted, it includes both)
  --omit-self-conns     omits connections without remote address
  --omit-privnet-conns  omits connections to private networks 
```

### Interval for Connection Enumeration
The default interval of 3 seconds has been chosen to save CPU cycles. Most TCP connections survive longer than that and will still be caught. For UDP packages there is a good chance of missing those though. Depending on your host's hardware, you might be able to tighten the interval down to 0.5 or even 0.2 seconds.

### Permissions to write to /var/log/
TODO: Implement check for folder access and add fallback option

At the moment the code expects to have write-access to /var/log/netlog, and it also expects that folder to exist.

### Omitting connections to private networks
Within the use case of this code, RFC1918 (private subnets) really only matters for IPv4 (NAT isn't used in IPv6 environments all that much) networks. Therefore, the "--omit-privnet-conns" switch is implemented for IPv4 only. 

## Licensing
"The code in this project is licensed under MIT license."
