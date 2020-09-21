import getpass
import pprint
from napalm import get_network_driver
from get_cdp_neighbors import get_hosts_cdp_neighbors

dev_ip = input('Enter device ip to start from: ')
username = input("Enter Username: ")
password = getpass.getpass()

hosts_cdp = get_hosts_cdp_neighbors(dev_ip, username, password)

for host in hosts_cdp:
        print(host.name)