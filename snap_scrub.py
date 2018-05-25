#! python
# Cluster IP Address and Credentials

import time,datetime
import base64
import pprint
import asyncio
from aiohttp import ClientSession
import requests
from urllib.parse import urlencode, quote
import json
import sys
import random
import argparse
import os


pp = pprint.PrettyPrinter(indent=4)

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(__location__, '.creds')) as f:
    creds = json.load(f)


parser = argparse.ArgumentParser()
parser.add_argument('-c', '--cluster', choices=creds, required='True', help='Choose a cluster in .creds')
parser.add_argument('-v', '--vm',  required='True', help='VM Name')
parser.add_argument('-f', '--filename',  required='True', help='File Name to Scrub')
args = parser.parse_args()

creds=creds[args.cluster]

NODE_IP_LIST = creds['servers']
USERNAME = creds['username']
PASSWORD = creds['password']

# ignore certificate verification messages
requests.packages.urllib3.disable_warnings()

# Generic Rubrik API Functions
def basic_auth_header():
    credentials = '{}:{}'.format(USERNAME, PASSWORD)
    # Encode the Username:Password as base64
    authorization = base64.b64encode(credentials.encode())
    # Convert to String for API Call
    authorization = authorization.decode()
    return authorization

def rubrik_delete(api_version, api_endpoint):
    AUTHORIZATION_HEADER = {'Content-Type': 'application/json',
                            'Accept': 'application/json',
                            'Authorization': 'Basic ' + basic_auth_header()
                            }
    request_url = "https://{}/api/{}{}".format(random.choice(NODE_IP_LIST), api_version, api_endpoint)
    try:
        response = requests.delete(request_url, verify=False, headers=AUTHORIZATION_HEADER)
        response.raise_for_status()
    except requests.exceptions.RequestException as error_message:
        print(error_message)
        sys.exit(1)

def rubrik_patch(api_version, api_endpoint, data):
    AUTHORIZATION_HEADER = {'Content-Type': 'application/json',
                            'Accept': 'application/json',
                            'Authorization': 'Basic ' + basic_auth_header()
                            }

    data = json.dumps(data)                        
    request_url = "https://{}/api/{}{}".format(random.choice(NODE_IP_LIST), api_version, api_endpoint)
    try:
        response = requests.patch(request_url, data=data, verify=False, headers=AUTHORIZATION_HEADER)
        response.raise_for_status()
    except requests.exceptions.RequestException as error_message:
        print(error_message)
        sys.exit(1)
    response_body = response.json()
    return response_body

def rubrik_get(api_version, api_endpoint):
    AUTHORIZATION_HEADER = {'Content-Type': 'application/json',
                            'Accept': 'application/json',
                            'Authorization': 'Basic ' + basic_auth_header()
                            }
    request_url = "https://{}/api/{}{}".format(random.choice(NODE_IP_LIST), api_version, api_endpoint)
    try:
        response = requests.get(request_url, verify=False, headers=AUTHORIZATION_HEADER)
        response.raise_for_status()
    except requests.exceptions.RequestException as error_message:
        print(error_message)
        sys.exit(1)
    response_body = response.json()
    return response_body

print("VM Details")
q_vm = rubrik_get("v1","/vmware/vm?primary_cluster_id=local&name={}".format(args.vm))
for r_vm in q_vm['data']:
    if r_vm['name'] == args.vm:
        vm_id = r_vm['id']
        sla_id = r_vm['configuredSlaDomainId']
        sla_name = r_vm['configuredSlaDomainName']
print("\tVM Name : {}\n\tVM ID : {}\n\tSLA : {} ({})".format(args.vm,vm_id,sla_name,sla_id))

t_snaps = len(rubrik_get("v1","/vmware/vm/{}/snapshot".format(quote(vm_id)))['data'])

f_snaps = []
q_file = rubrik_get("v1","/vmware/vm/{}/search?path={}".format(quote(vm_id),args.filename))
for r_version in q_file['data'][0]['fileVersions']:
    f_snaps.append(r_version['snapshotId'])
print("Snapshot Details")
print("\tSnaps for {} : {}".format(args.vm,t_snaps))
print("\tSnaps with {} : {}".format(args.filename,len(f_snaps)))
    
c = 0
while True:
    q = input("\n*** Remove {} snapshot(s) for Virtual Machine {} ? (Type YES) : ".format(len(f_snaps),args.vm))
    if q == 'YES':
        break
    else:
        c += 1
        if c == 3:
            print("Exiting")
            sys.exit()
        else:
            print("Must enter YES")

#unprotect
data = {}
data['configuredSlaDomainId'] = 'UNPROTECTED'
u_vm = rubrik_patch("v1","/vmware/vm/{}".format(quote(vm_id),args.filename),data)
print("\nSLA Domain reassigned for snapshot removal : {} ({})\n".format(u_vm['effectiveSlaDomainName'],u_vm['effectiveSlaDomainId']))

for snap in f_snaps:
    print("\tMarking Snapshot for deletion : {}".format(snap))
    rubrik_delete("v1","/vmware/vm/snapshot/{}?location=all".format(quote(snap)))
     
#protect
data = {}
data['configuredSlaDomainId'] = sla_id
u_vm = rubrik_patch("v1","/vmware/vm/{}".format(quote(vm_id),args.filename),data)
print("\nSLA Domain reassigned to resume protection : {} ({})".format(u_vm['effectiveSlaDomainName'],u_vm['effectiveSlaDomainId']))
print("Complete")