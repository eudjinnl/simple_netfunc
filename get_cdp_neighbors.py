"""
Build list of all devices with their cdp neighbors using cdp crawling.
Host with it's cdp neighbors will be added to result list if it's model matches patterns in patterns variable
and script was able to connect to device
"""
import json
from pathlib import Path
import pprint
from collections import deque

from dataclasses import asdict
from devactions import Host, Device, credentials_input
from parseit import parse_dev_name

def parse_cdp(result):
    """
    Parsing output of "show cdp neighbor detail" command
    Input (variable result) - list of splitted to lines output of "show cdp neighbors" command
    Returns list of dictionaries. Each dictionary - information of the neighbor behind the interface
    """
    cdp=[]
    i=0
    for res_str in result:
        if '----------' in res_str:
            neighbor={}
            # parse neighbor name
            n=1
            position = result[i+n].rfind(' ')
            # parsing neighbor name by position in output and dropping domain name in it
            neighbor["nbr_name"] = parse_dev_name(result[i+n][position+1:])
            
            # parse neighbor ip
            n=n+2
            position = result[i+n].rfind(' ')
            neighbor["nbr_ip"] = result[i+n][position+1:]

            # parse neighbor platform (model)
            n=n+1
            if 'Platform: ' not in result[i+n]:
                n=n+1
            position = result[i+n].find(' ')
            position_end = result[i+n].find(',')
            neighbor["nbr_platform"] = result[i+n][position+1:position_end]

            # parse  local interface name
            n=n+1
            position = result[i+n].find(' ')
            position_end = result[i+n].find(',')
            neighbor["local_int"] = result[i+n][position+1:position_end]
            # parse neighbor interface

            position = result[i+n].rfind(' ')
            neighbor["nbr_int"]=result[i+n][position+1:]

            # Appending neighbor information to result list of dictionaries.
            cdp.append(neighbor)

        i +=1
    return cdp


def get_hosts_cdp_neighbors(dev_ip, username, password, optional_args=None):
    queue = deque()
    processed = [] 
    known_hosts = set()
    # Defining patterns for device models. 
    # Device will be added to crawling queue if device model fits pattern 
    patterns = {'WS-C', 'C9200', 'C9300'}
    try:
        # Trying to connect to the first device
        with Device(dev_ip, username, password, optional_args=optional_args) as device:
            # on success getting device facts that include hostname
            facts = device.facts
        # Adding device to queue for crawling
        queue.append(Host(facts['hostname'], dev_ip, '', facts['model'], '', {}))
        # Adding host name to set of known hosts
        known_hosts = {queue[0].name}
    except:
        # of failure to connect print message
        print('Unable to connect to the first device')
        

    while queue:
        # get device from the queue
        host = queue.pop()
        print(f'\n\nConnecting to {host.name}, ip: {host.ip}')
        try:
            # Trying to connect to the first device
            with Device(host.ip, username, password, optional_args=optional_args) as device:
                # on success getting device facts, cdp neigbours and parsing it
                facts = device.facts
                result = device.neighbors()
            host.vendor = facts['vendor']
            host.platform = facts['model']
            host.serial_number = facts['serial_number']
            print(f'   Parsing cdp output for {host.name}')
            host.cdp = parse_cdp(result)

            # Adding host to resulting list of processed hosts
            processed.append(host)
            print(f'    Host {host.name} has been added')

            # # START OF BLOCK "All devices to the queue"
            # # All cdp neighbors will be added to the queue 
            # for item in host.cdp:
            #     if item["nbr_name"] not in known_hosts:
            #         queue.append(Host(item["nbr_name"], item["nbr_ip"], item["nbr_platform"], {}))
            #         known_hosts.add(queue[-1].name)
            #         print(f'     Neighbor {item["nbr_name"]} has been added to the queue')
            # # END OF BLOCK "All devices to the queue" 

            # START OF BLOCK "Filtered devices to the queue"
            # Filtered with patetrns cdp neighbors will be added to the queue
            # 
            # patterns = ['WS-C', 'C9200', 'C9300']

            # Analysing host cdp neighbors
            for item in host.cdp:
                for pattern in patterns:
                    if pattern in item["nbr_platform"] and item["nbr_name"] not in known_hosts:
                        # If model matches to patterns and host is not in the known_host set add host to the queue 
                        queue.append(Host(item["nbr_name"], item["nbr_ip"], '', item["nbr_platform"], '', {}))
                        # Add host name to the end of known_host set
                        known_hosts.add(queue[-1].name)
                        print(f'     Neighbor {item["nbr_name"]} has been added to the queue')

            # END OF BLOCK "Filtered devices to the queue"


        except:
            pass

    return processed


if __name__ == "__main__":

    data_path = Path("data")

    dev_ip = input('Enter device ip to start from: ')
    username, password, optional_args = credentials_input()
        

    hosts_cdp = get_hosts_cdp_neighbors(dev_ip, username, password, optional_args)

    if hosts_cdp:
        with open (Path(data_path, 'Hosts.json'), 'w') as f:
            json.dump([asdict(h) for h in hosts_cdp], f, indent=4)

        print('\n\n')
        pprint.pprint([asdict(h) for h in hosts_cdp])

        print('\n\nList of added hosts:')
        for host in hosts_cdp:
            print(host.name)
