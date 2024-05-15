#!/usr/bin/python3
import sys
import requests
import urllib3
import xml.etree.ElementTree as ET
import json
import xmltodict
import getpass

URL = "https://panorama.example.com/api/"
FWDIC = {}


def writeListTOFile(listOfData, filename):
    print('\033[92m' + f'started: writeListTOFile' + '\033[0m')
    with open (filename, 'w') as file:
        for line in listOfData:
            file.write(line + '\n')

    print('\033[92m' + f'completed: writeListTOFile' + '\033[0m')


def getKey():
    print('\033[92m' + f'started: getKey' + '\033[0m')

    try:
        username = getpass.getpass("Username:")
        password = getpass.getpass()
        #username = getpass.getuser()
    except Exception as error:
        print('ERROR', error)

    results =''
    params = {'type': 'keygen', 'user':username,'password': password}

    response = requests.get(URL, params=params,verify=False)

    if response.status_code == 403:
        raise Exception("\033[91mError: 403, Account is not Authorized. Username,Password,permissions\033[0m")

    root = ET.fromstring(response.content)

    for child in root.iter('*'):
        if child.tag == 'key':
            results = child.text
            if results:
                print('\033[92m' + f'successfully retrieved API key for {username}' + '\033[0m')

    return(results)


def getConnectedFirewalls(apiKey):
    print('\033[92m' + f'started: getConnectedFirewalls' + '\033[0m')
    command ="<show><devices><connected></connected></devices></show>"
    params = { "key":apiKey, "type":"op", "cmd":command}
    response = requests.get(URL, params=params, verify=False)

    root = ET.fromstring(response.content)

    for child in root[0][0]:
        hostname = child.find('hostname').text
        serialnum = child.find('serial').text
        FWDIC[hostname] = serialnum
    
    print('\033[92m' + f'completed: getConnectedFirewalls' + '\033[0m')


def getAllFirewallInterfaces(apiKey):
    print('\033[92m' + f'started: getAllFirewallInterfaces(' + '\033[0m')

    command ="<show><interface>all</interface></show>"
    
    resultsList = []
    csvHeaders = "Device,Interface,IP,Zone,Vsys"
    resultsList.append(csvHeaders)


    for device in FWDIC:
        target = FWDIC[device]
        params = { "key":apiKey, "type":"op", "cmd":command, "target":target }
        response = requests.get(URL, params=params, verify=False)

        data_dict = xmltodict.parse(response.content)
        listOfInterfaces = data_dict['response']["result"]["ifnet"]["entry"]

        for interface in listOfInterfaces:
            interfaceName = interface['name']
            interfaceIp = interface['ip']
            interfaceZone = interface['zone']
            interfaceVsys = interface['vsys']
            resultsList.append(f'{device},{interfaceName},{interfaceIp},{interfaceZone},{interfaceVsys}')

    writeListTOFile(resultsList, 'firewallInterfaces.csv')
    print('\033[92m' + f'completed: getConnectedFirewalls' + '\033[0m')

        

def main():
    print('\033[92m' + f'----- START -----' + '\033[0m')

    urllib3.disable_warnings()
    apiKey = getKey()
    getConnectedFirewalls(apiKey)
    getAllFirewallInterfaces(apiKey)

    print('\033[92m' + f'----- END -----' + '\033[0m')


if __name__ == "__main__":
    main()
