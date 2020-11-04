import pprint
from collections import deque

from dataclasses import asdict
from devactions import Host, Device, credentials_input
from parseit import parse_dev_name

def parse_cdp(result):
    cdp=[]
    i=0
    for res_str in result:
        if '----------' in res_str:
            neighbor={}
            # parse neighbor name
            n=1
            position = result[i+n].rfind(' ')
            neighbor["nbr_name"] = parse_dev_name(result[i+n][position+1:])


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


def get_hosts_cdp_neighbors(dev_ip, username, password, optional_args=None):
    queue = deque()
    processed = [] 
    known_hosts = set()
    patterns = {'WS-C', 'C9200', 'C9300'}
    try:
        with Device(dev_ip, username, password, optional_args=optional_args) as device:
            facts = device.facts
            
        # queue = deque()
        queue.append(Host(facts['hostname'], dev_ip, 'Cisco ' + facts['model'], {}))
        known_hosts = {queue[0].name}
        # processed = []
    except:
        print('Unable to connect to the first device')
        

    while queue:
        host = queue.pop()
        print(f'\n\nConnecting to {host.name}, ip: {host.ip}')
        try:
            with Device(host.ip, username, password, optional_args=optional_args) as device:
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
            # patterns = ['WS-C', 'C9200', 'C9300']
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
    username, password, optional_args = credentials_input()
        

    hosts_cdp = get_hosts_cdp_neighbors(dev_ip, username, password, optional_args)
    print('\n\n')
    pprint.pprint([asdict(h) for h in hosts_cdp])

    print('\n\nList of added hosts:')
    for host in hosts_cdp:
        print(host.name)
