import pprint

from simple_netfunc import credentials_input, get_hosts_cdp_neighbors
from dataclasses import asdict

dev_ip = input('Enter device ip to start from: ')
username, password, optional_args = credentials_input()
    

hosts_cdp = get_hosts_cdp_neighbors(dev_ip, username, password, optional_args)
print('\n\n')
pprint.pprint([asdict(h) for h in hosts_cdp])

print('\n\nList of added hosts:')
for host in hosts_cdp:
    print(host.name)
