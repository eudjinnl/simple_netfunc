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

    # dev_name = 'KLGAASW02.transmark.ru'
    # dev_ip = '10.122.100.12'
    # dev_platform = "WS-C2960X-48TS-L"

    host = {}
    host['dev_name'] = dev_name
    host['dev_ip'] = dev_ip
    host['dev_platform'] = dev_platform
    host['dev_cdp'] = {}

    hosts=[]
    hosts.append(host)
    # print(hosts)


    # result = ['-------------------------', 'Device ID: KLGAAP22', 'Entry address(es): ', '  IP address: 10.122.40.39', 'Platform: cisco AIR-LAP1141N-A-K9   ,  Capabilities: Trans-Bridge ', 'Interface: GigabitEthernet1/0/11,  Port ID (outgoing port): GigabitEthernet0', 'Holdtime : 172 sec', '', 'Version :', 'Cisco IOS Software, C1140 Software (C1140-K9W8-M), Version 12.4(23c)JA10, RELEASE SOFTWARE (fc1)', 'Technical Support: http://www.cisco.com/techsupport', 'Copyright (c) 1986-2015 by Cisco Systems, Inc.', 'Compiled Fri 20-Mar-15 12:27 by prod_rel_team', '', 'advertisement version: 2', 'Duplex: full', 'Power drawn: 15.000 Watts', 'Power request id: 60218, Power management id: 1', 'Power request levels are:0 0 0 0 0 ', '', '-------------------------', 'Device ID: KLGASW_WiFi02.transmark.ru', 'Entry address(es): ', '  IP address: 10.122.100.47', 'Platform: cisco WS-C2960-24LC-S,  Capabilities: Switch IGMP ', 'Interface: GigabitEthernet1/0/51,  Port ID (outgoing port): GigabitEthernet0/1', 'Holdtime : 169 sec', '', 'Version :', 'Cisco IOS Software, C2960 Software (C2960-LANLITEK9-M), Version 12.2(50)SE5, RELEASE SOFTWARE (fc1)', 'Technical Support: http://www.cisco.com/techsupport', 'Copyright (c) 1986-2010 by Cisco Systems, Inc.', 'Compiled Tue 28-Sep-10 13:44 by prod_rel_team', '', 'advertisement version: 2', 'Protocol Hello:  OUI=0x00000C, Protocol ID=0x0112; payload len=27, value=00000000FFFFFFFF010221FF000000000000A0CF5B667F00FF0000', "VTP Management Domain: 'kaluga'", 'Native VLAN: 1', 'Duplex: full', 'Management address(es): ', '  IP address: 10.122.100.47', '', '-------------------------', 'Device ID: KLGACSW01.transmark.ru', 'Entry address(es): ', '  IP address: 10.122.6.254', 'Platform: cisco WS-C3750G-48TS,  Capabilities: Router Switch IGMP ', 'Interface: GigabitEthernet1/0/49,  Port ID (outgoing port): GigabitEthernet1/0/51', 'Holdtime : 144 sec', '', 'Version :', 'Cisco IOS Software, C3750 Software (C3750-IPSERVICESK9-M), Version 12.2(55)SE7, RELEASE SOFTWARE (fc1)', 'Technical Support: http://www.cisco.com/techsupport', 'Copyright (c) 1986-2013 by Cisco Systems, Inc.', 'Compiled Mon 28-Jan-13 10:16 by prod_rel_team', '', 'advertisement version: 2', 'Protocol Hello:  OUI=0x00000C, Protocol ID=0x0112; payload len=27, value=00000000FFFFFFFF010221FF0000000000000017E0BBDE00FF0000', "VTP Management Domain: 'kaluga'", 'Native VLAN: 1', 'Duplex: full', 'Management address(es): ', '  IP address: 10.122.6.254', '', '', 'Total cdp entries displayed : 3']


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


        # host={'KLGAASW02.transmark.ru': {'cdp': {'GigabitEthernet1/0/11': ['KLGAAP22',
        #                                                               '10.122.40.39',
        #                                                               'cisco '
        #                                                               'AIR-LAP1141N-A-K9   ',
        #                                                               'GigabitEthernet0'],
        #                                     'GigabitEthernet1/0/49': ['KLGACSW01.transmark.ru',
        #                                                               '10.122.6.254',
        #                                                               'cisco '
        #                                                               'WS-C3750G-48TS',
        #                                                               'GigabitEthernet1/0/51'],
        #                                     'GigabitEthernet1/0/51': ['KLGASW_WiFi02.transmark.ru',
        #                                                               '10.122.100.47',
        #                                                               'cisco '
        #                                                               'WS-C2960-24LC-S',
        #                                                               'GigabitEthernet0/1']},
        #                             'ip': '10.122.100.12',
        #                             'platform': 'cisco WS-C2960X-48TS-L'}}

        # cdp={'GigabitEthernet1/0/11': ['KLGAAP22', '10.122.40.39', 'cisco AIR-LAP1141N-A-K9   ', 'GigabitEthernet0'], 'GigabitEthernet1/0/51': ['KLGASW_WiFi02.transmark.ru', '10.122.100.47', 'cisco C9200-24LC-S', 'GigabitEthernet0/1'], 'GigabitEthernet1/0/49': ['KLGACSW01.transmark.ru', '10.122.6.254', 'cisco C9300-48TS', 'GigabitEthernet1/0/51']}



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





