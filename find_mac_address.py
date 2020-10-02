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

macs=macs_input.replace(' ','')
macs=macs.split(',')

macs_to_find=[]
for mac in macs:
    try:
        c_mac = netaddr.EUI(mac, dialect=mac_unix_expanded)
        res_mac = str(c_mac).upper()
        macs_to_find.append(res_mac)
    except:
        print(f'{mac} is not a Valid MAC address\n')
        
for mac in macs_to_find:
    dev_ip = start_ip
    cdp=[]
    macdict={}
    mac_found = False
    previous_dev = {"dev_name":"", "dev_ip":"", "interface":"", "vlan":""}
    while mac_found == False:
        try:
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
                print(f'\n{mac} - {previous_dev["dev_name"]} {previous_dev["dev_ip"]} interface {macdict["interface"]} Vlan{macdict["vlan"]}')
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
                    if dev_name == previous_dev["dev_name"]:
                        mac_found = True
                        print(f'\n{mac} is between two devices:')
                        print(f'     {previous_dev["dev_name"]} {previous_dev["dev_ip"]} interface {previous_dev["interface"]} Vlan{previous_dev["vlan"]}')
                        print(f'     {dev_name} {dev_ip} interface {macdict["interface"]} Vlan{macdict["vlan"]}')
                        break
                    else:
                        with Device(dev_ip, username, password) as device:
                            result = device.neighbors(interface=macdict["interface"])

                        print(f'Parsing cdp output for {dev_ip}')
                        cdp = parse_cdp(result)

                        if cdp:
                            for item in cdp:
                                dev_ip = item["nbr_ip"]
                            break
                        else:
                            mac_found = True
                            print(f'\n{mac} - {dev_name} {dev_ip} interface {macdict["interface"]} Vlan{macdict["vlan"]}')
                            break
        else:
            mac_found = True
            print(f'\n{mac} has not been found')
