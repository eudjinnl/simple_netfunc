"""
Build list of all devices using cdp crawling.
Find mac address in mac address table
Find mac address in mac table. Get cdp cdp neigbor of interface where mac address is.
If there isn't switch there - mac address is found.
If there is switch behind the interface connect to the switch.
Repeat until mac address not found.
If cdp shows that mac is on the neighbor with name we already checked 
     that mac address is on non cisco switch which in between two cisco switches

Returns mac - device name, interface, vlan or some comments
mac address can be entered in any form
"""

import time
import netaddr
from netaddr import mac_unix_expanded
from devactions import Device, credentials_input
from get_cdp_neighbors import parse_cdp
from parseit import parse_int_name

# Asking user for macs to find, ip to start cdp crawlig from and user credentials for accessing devices
macs_input = input('Enter one or more MAC addresses (comma separated): ')
start_ip = input('Enter device ip to start from: ')
username, password, optional_args = credentials_input()

start_time = time.clock()

macs = macs_input.replace(' ', '')
macs = macs.split(',')

macs_to_find = []
find_mac_result = []

# Convertation form of mac address to form like AA:AA:AA:AA:AA:AA 
# in which NAPALM is getting mac address table from device
# Checking whether mac address was entered or not based on it's form
for mac in macs:
    try:
        c_mac = netaddr.EUI(mac, dialect=mac_unix_expanded)
        res_mac = str(c_mac).upper()
        macs_to_find.append(res_mac)
    except:
        print(f'{mac} is not a Valid MAC address\n')
        find_mac_result.append(f'{mac} is not a Valid MAC address\n')

for mac in macs_to_find:
    dev = {} # results for device we connected to will be stored here
    cdp = []
    macdict = {}
    mac_found = False
    dev['dev_ip'] = start_ip
    previous_dev = {"dev_name":"", "dev_ip":"", "interface":"", "vlan":""} # results for previous device
    while mac_found == False:
        try:
            # Trying to connect to current device. On success getting device facts and mac table
            with Device(dev['dev_ip'], username, password, optional_args=optional_args) as device:
                mac_table = device.mac_address_table
                facts = device.facts
            dev['dev_name'] = facts["hostname"]
        except:
            # On failure    
            if previous_dev["dev_name"]:
                # If results from previous device exist they are results of finding this mac address
                find_mac_result.append(f'\n{mac} - {previous_dev["dev_name"]} {previous_dev["dev_ip"]} interface {previous_dev["interface"]} Vlan{previous_dev["vlan"]}')
                break
            else:
                # If results from previous device don't exist we can't connect to the first switch.
                print('Unable to connect to the first device')
                break
        
        known_macs = {}
        # Getting set of mac addresses from current switch mac table
        known_macs = {macdict["mac"] for macdict in mac_table}
        cdp = {}

        if mac in  known_macs:
            # If mac address is in mac table of current switch
            # find dictionary from mac_table with mac address we are looking for 
            for macdict in mac_table:
                if macdict["mac"] == mac:
                    # When the dictionary was found check interface in it.
                    # If dictionary refers to interface PortChannel 
                    #    find out physical interface in the PortChannel interface
                    if 'Po' in macdict["interface"]:
                        with Device(dev["dev_ip"], username, password, optional_args=optional_args) as device:
                            command = [f'show interface {macdict["interface"]} etherchannel']
                            result = device.send_command(command=command)
                            result = result[command[0]].split('\n') 
                            for res_str in result:
                                try:
                                    interface = parse_int_name(res_str)
                                    if 'Port-channel' not in interface:
                                        # rewrite PortChannel interface with found physical interface in macdict
                                        macdict["interface"] = interface
                                        break
                                except:
                                    pass


                    dev["interface"] = macdict["interface"]
                    dev["vlan"] = macdict["vlan"]
                    
                    with Device(dev["dev_ip"], username, password, optional_args=optional_args) as device:
                        result = device.neighbors(interface=dev['interface'])

                    print(f'Parsing cdp output for {dev["dev_name"]} {dev["dev_ip"]}')
                    cdp = parse_cdp(result)

                    if cdp:
                        if cdp[0]["nbr_name"] == previous_dev["dev_name"]:
                            mac_found = True
                            # print(f'\n{mac} is between two devices:')
                            # print(f'     {previous_dev["dev_name"]} {previous_dev["dev_ip"]} interface {previous_dev["interface"]} Vlan{previous_dev["vlan"]}')
                            # print(f'     {dev["dev_name"]} {dev["dev_ip"]} interface {dev["interface"]} Vlan{dev["vlan"]}')
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
                        # print(f'\n{mac} - {dev["dev_name"]} {dev["dev_ip"]} interface {dev["interface"]} Vlan{dev["vlan"]}')
                        find_mac_result.append(f'\n{mac} - {dev["dev_name"]} {dev["dev_ip"]} interface {dev["interface"]} Vlan{dev["vlan"]}')
                        break
        else:
            # If there isn't mac address in mac table of current switch - end of search of this mac address.
            mac_found = True
            # print(f'\n{mac} has not been found')
            find_mac_result.append(f'\n{mac} has not been found')   

time_end = time.clock()

print('RESULTS')
for item in find_mac_result:
    print(item) 

print(time_end - start_time, "seconds")
