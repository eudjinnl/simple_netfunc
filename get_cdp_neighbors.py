import getpass
import pprint
from napalm import get_network_driver
from collections import deque
from dataclasses import dataclass, asdict

def parse_cdp(result):
    cdp=[]
    i=0
    for res_str in result:
        if '----------' in res_str:
            neighbor={}
            # parse neighbor name
            n=1
            position = result[i+n].rfind(' ')
            neighbor["nbr_name"] = result[i+n][position+1:]


            # parse neighbor ip
            n=n+2
            position = result[i+n].rfind(' ')
            neighbor["nbr_ip"] = result[i+n][position+1:]

            # parse neighbor platform
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

            cdp.append(neighbor)


        i +=1
    return cdp

@dataclass
class Host:
    name : str
    ip : str
    platform : str
    cdp : dict

class Device:

    def __init__(self, ip, username, password, *,driver_type='ios'):
        klass = get_network_driver(driver_type)
        self._driver = klass(ip, username, password)

    def __enter__(self):
        self._driver.open()
        return self

    def __exit__(self, *exc_details):
        self._driver.close()

    @property
    def facts(self):
        return self._driver.get_facts()

    @property
    def mac_address_table(self):
        return self._driver.get_mac_address_table()

    def neighbors(self, *, interface=None):
        if interface is None:
            command = 'show cdp neighbors detail'
        else:
            command = f'show cdp neighbors {interface} detail'

        self._driver.cli(['terminal length 0'])
        result = self._driver.cli([command])
        return result[command].split('\n')

def get_hosts_cdp_neighbors(dev_ip, username, password): 
    try:
        with Device(dev_ip, username, password) as device:
            facts = device.facts
            
        queue = deque()
        queue.append(Host(facts['fqdn'], dev_ip, 'cisco ' + facts['model'], {}))
        known_hosts = {queue[0].name}
        processed = []
    except:
        print('Unable to connect to the first device')

    while queue:
        host = queue.pop()
        print(f'\n\nConnecting to {host.name}, ip: {host.ip}')
        try:
            with Device(host.ip, username, password) as device:
                result = device.neighbors()
                print(f'   Parsing cdp output for {host.name}')
                host.cdp = parse_cdp(result)

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
            patterns = ['WS-C', 'C9200', 'C9300']
            for item in host.cdp:
                for pattern in patterns:
                    if pattern in item["nbr_platform"] and item["nbr_name"] not in known_hosts:
                        queue.append(Host(item["nbr_name"], item["nbr_ip"], item["nbr_platform"], {}))
                        known_hosts.add(queue[-1].name)
                        print(f'     Neighbor {item["nbr_name"]} has been added to the queue')

            # END OF BLOCK "Filtered devices to the queue"


        except:
            pass

    return processed

if __name__ == "__main__":

    dev_ip = input('Enter device ip to start from: ')
    username = input("Enter Username: ")
    password = getpass.getpass()

    hosts_cdp = get_hosts_cdp_neighbors(dev_ip, username, password)
    print('\n\n')
    pprint.pprint([asdict(h) for h in hosts_cdp])

    print('\n\nList of added hosts:')
    for host in hosts_cdp:
        print(host.name)
