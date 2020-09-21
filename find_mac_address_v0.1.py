import getpass
import pprint
from napalm import get_network_driver
from get_cdp_neighbors import parse_cdp, Host, Device
import netaddr
from netaddr import *

macs_input = input('Enter one or more MAC addresses (comma separated): ')
start_ip = input('Enter device ip to start from: ')
username = input("Enter Username: ")
password = getpass.getpass()

driver = get_network_driver('ios')
# ios = driver(dev_ip, username, password)
# ios.open()
# facts=ios.get_facts()
# ios.close()
# dev_name=facts["fqdn"]
# pprint.pprint(mac_table)



macs=macs_input.replace(' ','')
macs=macs.split(',')

macs_to_find=[]
for mac in macs:
    try:
        c_mac = netaddr.EUI(mac, dialect=mac_unix_expanded)
        res_mac = str(c_mac).upper()
        macs_to_find.append(res_mac)
        # print(res_mac)
    except:
        print(f'{mac} is not a Valid MAC address\n')
        
# print(macs_to_find)

for mac in macs_to_find:
    dev_ip = start_ip
    cdp=[]
    macdict={}
    mac_found = False
    previous_dev = {"dev_name":"", "dev_ip":"", "interface":"", "vlan":""}
    while mac_found == False:
        
        # ios = driver(dev_ip, username, password)
        # print(f'while {macdict}')
        try:
            # ios.open()
            # mac_table=ios.get_mac_address_table()
            # facts = ios.get_facts()
            # ios.close()
            with Device(dev_ip, username, password) as device:
                mac_table = device.mac_address_table
                facts = device.facts
            dev_name=facts["hostname"]
            if cdp:
                for item in cdp:
                    previous_dev["dev_name"] = item["nbr_name"]
                    previous_dev["dev_ip"] = item["nbr_ip"]
                    previous_dev["interface"] = macdict["interface"]
                    previous_dev["vlan"] = macdict["vlan"]
                    
                       
        except:
            if previous_dev["dev_name"]:
                print(f'{mac} - {previous_dev["dev_name"]} {previous_dev["dev_ip"]} interface {macdict["interface"]} Vlan{macdict["vlan"]}')
                break
            else:
                print('Unable to connect to the first device')
                break
        
        # create list from dev_to_create which is already in netbox
        known_macs = {}
        known_macs = {macdict["mac"] for macdict in mac_table}
        cdp={}

        if mac in  known_macs:
            for macdict in mac_table:
                if macdict["mac"] == mac:
                    if dev_name == previous_dev["dev_name"]:
                        mac_found = True
                        print(f'{mac} is between two devices:')
                        print(f'     {previous_dev["dev_name"]} {previous_dev["dev_ip"]} interface {previous_dev["interface"]} Vlan{previous_dev["vlan"]}')
                        print(f'     {dev_name} {dev_ip} interface {macdict["interface"]} Vlan{macdict["vlan"]}')
                        break
                    else:
                        with Device(dev_ip, username, password) as device:
                            result = device.neighbors(interface=macdict["interface"])
                        # result=get_cdp_neighbors('ios', dev_ip, username, password, interface=macdict["interface"])
                        print(f'Parsing cdp output for {dev_ip}')
                        print(macdict)
                        cdp = parse_cdp(result)
                        if cdp:
                            for item in cdp:
                                print(item)
                                dev_ip = item["nbr_ip"]
                                # previous_dev["dev_name"] = item["nbr_name"]
                                # previous_dev["dev_ip"] = item["nbr_ip"]
                                # previous_dev["interface"] = macdict["interface"]
                                # previous_dev["vlan"] = macdict["vlan"]
                            break
                        else:
                            mac_found = True
                            print(f'{mac} - {dev_name} {dev_ip} interface {macdict["interface"]} Vlan{macdict["vlan"]}')
                            break
        else:
            mac_found = True
            print(f'{mac} has not been found')
