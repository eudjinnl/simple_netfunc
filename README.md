# simple_netfunc

It's my first try to do some automation stuff using python which I've started to learn recently.

These modules are used in scripts:
dataclasses
NAPALM
netmiko
getpass
netaddr

It's considered that all network devices are Cisco.
It's also considered that you are able to get access to any device with the same credentials.

Main functions:
1. Collecting information about network devices using cdp crawling.
2. Finding mac addresses across the network using cdp
3. Finding specified information in device inventory.
4. Configure devices with sending commands with saving/no saving config after that, backaping config (needs improvements).

scripts:

devactions.py
find_int_in_vlan.py
find_in_inventory.py
find_mac_address.py
get_cdp_neighbors.py
nmk_send_command.py
parseit.py