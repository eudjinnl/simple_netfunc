import re

# Parsing of some standart things

def parse_int_name(string):
    # Interface name parsing
    ciscoIntRegex = re.compile(r'(Gi|Te|Fa|Tu|Eth|Po|Port-channel|e|Null|Vlan|Serial|Bundle-Ether)[a-zA-Z*]?[-]?[a-zA-Z*]?\d+(([\/\.:]\d+)+(\.\d+)?)?')
    mo=ciscoIntRegex.search(string)
    if mo: 
        result = mo.group()
        return result
    else:
        return Exception


def parse_dev_name(string):
    # Device name parsing
    ciscoIntRegex = re.compile(r'\w{4,}[a-zA-Z0-9_\.]*\d\d')
    mo=ciscoIntRegex.search(string)
    if mo: 
        result = mo.group()
        return result
    else:
        return Exception
