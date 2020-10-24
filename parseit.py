import re

def parse_int_name(string):
    ciscoIntRegex = re.compile(r'(Gi|Te|Fa|Tu|Eth|Po|Port-channel|e|Null|Vlan|Serial|Bundle-Ether)[a-zA-Z*]?[-]?[a-zA-Z*]?\d+(([\/\.:]\d+)+(\.\d+)?)?')
    mo=ciscoIntRegex.search(string)
    if mo: 
        result = mo.group()
        return result
    else:
        return Exception
