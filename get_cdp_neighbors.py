import getpass
import pprint
from napalm import get_network_driver

def get_cdp_neighbors(napalm_driver, ip, username, password, **kwargs):
    # in **kwargs could be an argument 'interface'
    cli_str=[]
    command='show cdp neighbors detail'
    if 'interface' in kwargs:
        command=f'show cdp neighbors {kwargs["interface"]} detail'
    cli_str.append(command)

    # NAPALM driver initialisation
    driver = get_network_driver(napalm_driver)
    ios = driver(ip, username, password)

    ios.open()
    ios.cli(['terminal length 0'])
    result = ios.cli(cli_str)
    ios.close()

    result=result[command]
    return result.split('\n')



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


if __name__ == "__main__":
    
    dev_ip = input('Enter device ip to start from: ')
    username = input("Enter Username: ")
    password = getpass.getpass()

    driver = get_network_driver('ios')
    ios = driver(dev_ip, username, password)
    ios.open()
    facts=ios.get_facts()
    ios.close()

    dev_name=facts["fqdn"]
    dev_platform='cisco ' + facts['model']
    # put hostname in result list of devices

    
    host = {}
    host['dev_name'] = dev_name
    host['dev_ip'] = dev_ip
    host['dev_platform'] = dev_platform
    host['dev_cdp'] = {}

    hosts=[]
    hosts.append(host)
    # print(hosts)


    i=0
    known_hosts = {hosts[i]["dev_name"]}

    while i < len(hosts):
        print(f'connecting to {hosts[i]["dev_name"]}, ip: {hosts[i]["dev_ip"]}')
        result=get_cdp_neighbors('ios', hosts[i]['dev_ip'], username, password)
        print(f'Parsing cdp output for {hosts[i]["dev_name"]}')
        cdp = parse_cdp(result)
        hosts[i]['dev_cdp'] = cdp
        # print('\n\n\n')
        # pprint.pprint(hosts) 
        # print('\n')
        # print(cdp)


        


        patterns = ['WS-C', 'C9200', 'C9300']
        for item in cdp:
            # print(item)
            for pattern in patterns:
                if pattern in item["nbr_platform"]:
                    if item["nbr_name"] not in known_hosts:
                        host = {}
                        host['dev_name'] = item["nbr_name"]
                        host['dev_ip'] = item["nbr_ip"]
                        host['dev_platform'] = item["nbr_platform"]
                        host['dev_cdp'] = {}
                        hosts.append(host)
                        known_hosts.add(item["nbr_name"])
                        print(f'Host {item["nbr_name"]} has been added\n\n')
        i +=1

    pprint.pprint(hosts)
    for host in hosts:
        print(host['dev_name'])





