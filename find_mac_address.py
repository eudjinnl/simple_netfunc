import getpass
import pprint
from napalm import get_network_driver
from get_cdp_neighbors import parse_cdp, Host, Device, credentials_input
import netaddr
from netaddr import *

macs_input = input('Enter one or more MAC addresses (comma separated): ')
start_ip = input('Enter device ip to start from: ')
username, password, optional_args = credentials_input()
# username = input("Enter Username: ")
# password = getpass.getpass()

driver = get_network_driver('ios')

macs=macs_input.replace(' ','')
macs=macs.split(',')

macs_to_find=[]

find_mac_result=[]
for mac in macs:
    try:
        c_mac = netaddr.EUI(mac, dialect=mac_unix_expanded)
        res_mac = str(c_mac).upper()
        macs_to_find.append(res_mac)
    except:
        print(f'{mac} is not a Valid MAC address\n')
        find_mac_result.append(f'{mac} is not a Valid MAC address\n')

for mac in macs_to_find:
    dev = {}
    cdp=[]
    macdict={}
    mac_found = False
    dev['dev_ip'] = start_ip
    previous_dev = {"dev_name":"", "dev_ip":"", "interface":"", "vlan":""}
    while mac_found == False:
        try:
            with Device(dev['dev_ip'], username, password, optional_args=optional_args) as device:
                mac_table = device.mac_address_table
                #  print(mac_table)
                facts = device.facts
            dev['dev_name']=facts["fqdn"]
        except:    
            if previous_dev["dev_name"]:
                print(f'\n{mac} - {previous_dev["dev_name"]} {previous_dev["dev_ip"]} interface {previous_dev["interface"]} Vlan{previous_dev["vlan"]}')
                find_mac_result.append(f'\n{mac} - {previous_dev["dev_name"]} {previous_dev["dev_ip"]} interface {previous_dev["interface"]} Vlan{previous_dev["vlan"]}')
                break
            else:
                print('Unable to connect to the first device')
                break
        
        known_macs = {}
        known_macs = {macdict["mac"] for macdict in mac_table}
        cdp={}

        if mac in  known_macs:
            for macdict in mac_table:
                if macdict["mac"] == mac:
                    dev["interface"] = macdict["interface"]
                    dev["vlan"] = macdict["vlan"]
                    
                    with Device(dev["dev_ip"], username, password, optional_args=optional_args) as device:
                        result = device.neighbors(interface=dev['interface'])

                    print(f'Parsing cdp output for {dev["dev_name"]} {dev["dev_ip"]}')
                    cdp = parse_cdp(result)

                    if cdp:
                        if cdp[0]["nbr_name"] == previous_dev["dev_name"]:
                            mac_found = True
                            print(f'\n{mac} is between two devices:')
                            print(f'     {previous_dev["dev_name"]} {previous_dev["dev_ip"]} interface {previous_dev["interface"]} Vlan{previous_dev["vlan"]}')
                            print(f'     {dev["dev_name"]} {dev["dev_ip"]} interface {dev["interface"]} Vlan{dev["vlan"]}')
                            find_mac_result.append(f'\n{mac} is between two devices:\n     {previous_dev["dev_name"]} {previous_dev["dev_ip"]} interface {previous_dev["interface"]} Vlan{previous_dev["vlan"]}\n     {dev["dev_name"]} {dev["dev_ip"]} interface {dev["interface"]} Vlan{dev["vlan"]}')
                            break
                        else:
                            previous_dev["dev_name"] = dev["dev_name"]
                            previous_dev["dev_ip"] = dev["dev_ip"]
                            previous_dev["interface"] = dev["interface"]
                            previous_dev["vlan"] = dev["vlan"]
                            
                            dev["dev_name"] = cdp[0]["nbr_name"]
                            dev["dev_ip"] = cdp[0]["nbr_ip"]
                            dev["interface"] = ''
                            dev["vlan"] = ''
                            break
                    else:
                        mac_found = True
                        print(f'\n{mac} - {dev["dev_name"]} {dev["dev_ip"]} interface {dev["interface"]} Vlan{dev["vlan"]}')
                        find_mac_result.append(f'\n{mac} - {dev["dev_name"]} {dev["dev_ip"]} interface {dev["interface"]} Vlan{dev["vlan"]}')
                        break
        else:
            mac_found = True
            print(f'\n{mac} has not been found')
            find_mac_result.append(f'\n{mac} has not been found')   

for item in find_mac_result:
    print(item) 
