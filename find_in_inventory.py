import getpass
import pprint
from napalm import get_network_driver
from get_cdp_neighbors import get_hosts_cdp_neighbors, Device, Host

items_input = input('Enter one or more item to find (comma separated): ')
items_to_find=items_input.replace(' ','')
items_to_find=items_to_find.split(',')

# items_to_find = {''}


dev_ip = input('Enter device ip to start from: ')
username = input("Enter Username: ")
password = getpass.getpass()

hosts_cdp = get_hosts_cdp_neighbors(dev_ip, username, password)

for host in hosts_cdp:
    with Device(host.ip, username, password) as device:
        host_inventory = device.get_inventory()
    for line in host_inventory:
        for item in items_to_find:
            if item in line:
                print(f'\n{line}')
                print(f'{item} - {host.name} {host.ip}')
print('\nEnd of searching')
