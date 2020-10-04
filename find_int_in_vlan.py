import getpass
import pprint
from napalm import get_network_driver
from get_cdp_neighbors import get_hosts_cdp_neighbors, Device, credentials_input

dev_ip = input('Enter device ip to start from: ')
username, password, optional_args = credentials_input()
# username = input("Enter Username: ")
# password = getpass.getpass()

skip = False
while not skip:
    try:
        with Device(dev_ip, username, password, optional_args=optional_args) as device:
            print('connected to switch')
        skip=True
              
    except:
        print('Unable connect to the switch')
        print('1 - for enter new credentials')
        print('2 - any key to skip the switch')
        decision = input('Enter 1 or 2: ')
        if decision == '1':
            username = input("Enter Username: ")
            password = getpass.getpass()
        else:
            skip=True

print ('end of script')