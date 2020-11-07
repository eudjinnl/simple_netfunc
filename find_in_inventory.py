"""
Build list of all devices using cdp crawling.
Find items in devices inventory (in show inventory output)
"""

from get_cdp_neighbors import get_hosts_cdp_neighbors 
from devactions import Device, credentials_input

# Asking user for items to find, ip to start cdp crawlig from and user credentials for accessing devices
items_input = input('Enter one or more item to find (comma separated): ')
dev_ip = input('Enter device ip to start from: ')
username, password, optional_args = credentials_input()

items_to_find=items_input.replace(' ','')
items_to_find=items_to_find.split(',')

# Building list of devices by using cdp crawling function
hosts_cdp = get_hosts_cdp_neighbors(dev_ip, username, password)

# Searching for items in inventory
for host in hosts_cdp:
    with Device(host.ip, username, password) as device:
        host_inventory = device.get_inventory()
    for line in host_inventory:
        for item in items_to_find:
            if item in line:
                print(f'\n{line}')
                print(f'{item} - {host.name} {host.ip}')
print('\nEnd of searching')
