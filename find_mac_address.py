"""
Build list of all Cisco devices using cdp crawling.
Find mac address in mac table. Get cdp cdp neigbor of interface where mac address is found.
If there isn't switch there - mac address is found.
If there is switch behind the interface connect to the switch.
Repeat until mac address not found.
If cdp shows that mac is on the neighbor with the name we already checked 
     that mac address is on non Cisco switch which is in between two Cisco switches

Returns list of dictionaries:
find_mac_result = [{"mac":"mac address"
                    "dev_name":"device name"
                    "dev_ip":"device ip address"
                    "interface":"name of devices interface where mac address was found"
                    "vlan":"vlan number"
                    "comments":"comments"}]

"comments" can be:
    - NOT FOUND
    - INVALID mac address
    - informatin about the second switch in case of mac address is on non Cisco device connected
      between two Cisco switches

mac address can be entered in any form
"""

import netaddr
from netaddr import mac_unix_expanded
from devactions import Device, credentials_input
from get_cdp_neighbors import parse_cdp
from parseit import parse_int_name

# Asking user for macs to find, ip to start cdp crawlig from and user credentials for accessing devices
macs_input = input('Enter one or more MAC addresses (comma separated): ')
start_ip = input('Enter device ip to start from: ')
username, password, optional_args = credentials_input()

macs = macs_input.replace(' ', '')
macs = macs.split(',')

macs_to_find = []
find_mac_result = []

for source_mac in macs:
    try:
        # Convertation form of mac address to form like AA:AA:AA:AA:AA:AA 
        # in which NAPALM is getting mac address table from device
        # Checking whether mac address was entered based on it's form
        c_mac = netaddr.EUI(source_mac, dialect=mac_unix_expanded)
        mac = str(c_mac).upper()
        print(f'Searching for mac address {source_mac}')
        dev = {} # results for device we connected to will be stored here
        cdp = []
        macdict = {}
        mac_found = False
        dev['dev_ip'] = start_ip
        previous_dev = {"mac":"", "dev_name":"", "dev_ip":"", "interface":"", "vlan":"", "comments":""} # results for previous device
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
                    # ########## RESULT: MAC FOUND CASE 1/3 ##########
                    # If results from previous device exist they are results of searching this mac address
                    find_mac_result.append({'mac':source_mac, **previous_dev, 'comments':''})
                    break
                else:
                    # If results from previous device don't exist we can't connect to the first switch.
                    print('Unable to connect to the first device')
                    break

            known_macs = {}
            # Filling in set of mac addresses from current switch mac table
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

                        # Store data to current device dictionary
                        dev["interface"] = macdict["interface"]
                        dev["vlan"] = macdict["vlan"]
                        
                        # Getting cdp neighbors for the interface of current device
                        with Device(dev["dev_ip"], username, password, optional_args=optional_args) as device:
                            result = device.neighbors(interface=dev['interface'])

                        # Parsing cdp output
                        print(f'    Parsing cdp output for {dev["dev_name"]} {dev["dev_ip"]}')
                        cdp = parse_cdp(result)

                        if cdp:
                            # if there 
                            if cdp[0]["nbr_name"] == previous_dev["dev_name"]:
                                # ########## RESULT: MAC FOUND CASE 2/3 ##########
                                # If cdp neighbor's name == name of the previous device mac adderess is connected
                                # to some device connected inbetween current and previous device 
                                mac_found = True
                                comment = f'\n     and on {dev["dev_name"]} {dev["dev_ip"]} interface {dev["interface"]} Vlan{dev["vlan"]}'
                                find_mac_result.append({'mac':source_mac, **previous_dev, 'comments':comment})
                                break
                            else:
                                # Setting data of current device to previos device dictionary
                                previous_dev["dev_name"] = dev["dev_name"]
                                previous_dev["dev_ip"] = dev["dev_ip"]
                                previous_dev["interface"] = dev["interface"]
                                previous_dev["vlan"] = dev["vlan"]
                                
                                # Setting data of neighbor device as current device
                                dev["dev_name"] = cdp[0]["nbr_name"]
                                dev["dev_ip"] = cdp[0]["nbr_ip"]
                                dev["interface"] = ''
                                dev["vlan"] = ''
                                break
                        else:
                            # # ########## RESULT: MAC FOUND CASE 3/3 ##########
                            # if there is no cdp information - mac address is found on the interface of current device
                            mac_found = True
                            find_mac_result.append({'mac':source_mac, **dev, 'comments':''})
                            break
            else:
                # ########## RESULT MAC NOT FOUND ##########
                # If there isn't mac address in mac table of current switch - mac address has not been found
                mac_found = True
                find_mac_result.append({'mac':source_mac, 'dev_name':'', 'dev_ip':'', 'interface':'', 'vlan':'', 'comments':'NOT found'})
    except:
        # Not correct mac adress was entered
        print(f'\n{source_mac} is not a valid MAC address\n')
        find_mac_result.append({'mac':source_mac, 'dev_name':'', 'dev_ip':'', 'interface':'', 'vlan':'', 'comments':'INVALID MAC address'})

print('\nRESULTS')

for item in find_mac_result:
    if item["dev_name"]:
        print(f'{item["mac"]} - {item["dev_name"]} {item["dev_ip"]} interface {item["interface"]} Vlan{item["vlan"]} {item["comments"]}')
    else:
        print(f'{item["mac"]} - {item["comments"]}')
