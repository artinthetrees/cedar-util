
import os, sys
import pandas as pd
import json
from cedar.utils import getter, updater, searcher, storer
#from cedar.utils import validator

import requests
#import json
from urllib.parse import quote
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


##########################################################
## input params
##########################################################

server_address = "https://resource." + os.environ['CEDAR_HOST']
api_key = "apiKey " + os.environ['CEDAR_API_KEY']

folder_id = None
#folder_id = "https://repo.metadatacenter.org/folders/fa170406-f3e8-4d72-8848-0adcb3be6c63"
instance_skeleton_path = r"C:\Users\tentner-andrea\project_repositories\cedar-util-test-template-instance-skeleton.json"

##########################################################
## open the instance 'skeleton'
##########################################################

with open(instance_skeleton_path, 'r') as myfile:
    data=myfile.read()

# parse file
instance_skeleton = json.loads(data)

##########################################################
## write to the instance 'skeleton' to add metadata
## harvested from nih reporter, clinicaltrials.gov,
## and home data repository
##
## in order to do this correctly, we will need to fill in
## sample instances of the template - this will provide
## platform with the proper format for instance population
##########################################################

instance = instance_skeleton

## this is one example of populating a field in this sample skeleton
instance['pubs']['secondary pubs'] = [{"@value":"doi: 789"},{"@value":"doi: 101112"}]

##########################################################
## create POST request url and header
##########################################################

request_url = server_address + "/template-instances"

headers = {
        'Content-Type': "application/json",
        'Authorization': api_key
    }

##########################################################
## make POST call
##########################################################

response = requests.request("POST", request_url, json=instance, headers=headers, verify=False)

##########################################################
## grab POST call response and save new instance ID
##########################################################

instance_created = json.loads(response.text)
instance_created_id = instance_created["@id"]

#validate_response = validator.validate_instance(server_address, api_key, instance)
#create_response = storer.store_instance(server_address, api_key, instance, folder_id)