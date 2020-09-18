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

            # print(dev_name)
            # print(ip)
            # print(platform)
            # print(local_int)
            # print(remote_int)

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

    def neighbors(self, *, interface=None):
        if interface is None:
            command = 'show cdp neighbors detail'
        else:
            command = f'show cdp neighbors {interface} detail'

        self._driver.cli(['terminal length 0'])
        result = self._driver.cli([command])
        return result[command].split('\n')


if __name__ == "__main__":

    dev_ip = input('Enter device ip to start from: ')
    username = input("Enter Username: ")
    password = getpass.getpass()

    with Device(dev_ip, username, password) as device:
        facts = device.facts

    queue = deque()
    queue.append(Host(facts['fqdn'], dev_ip, 'cisco ' + facts['model'], {}))
    known_hosts = {queue[0].name}
    processed = []

    while queue:
        host = queue.pop()
        print(f'connecting to {host.name}, ip: {host.ip}')
        with Device(host.ip, username, password) as device:
            result = device.neighbors()
            print(f'Parsing cdp output for {host.name}')
            host.cdp = parse_cdp(result)
            # print('\n\n\n')
            # pprint.pprint(hosts)
            # print('\n')
            # print(cdp)

        processed.append(host)

        patterns = ['WS-C', 'C9200', 'C9300']
        for item in host.cdp:
            # print(item)
            for pattern in patterns:
                if pattern in item["nbr_platform"] and item["nbr_name"] not in known_hosts:
                    queue.append(Host(item["nbr_name"], item["nbr_ip"], item["nbr_platform"], {}))
                    known_hosts.add(queue[-1].name)
                    print(f'Host {item["nbr_name"]} has been added\n\n')

    pprint.pprint([asdict(h) for h in processed])

    for host in processed:
        print(host.name)





