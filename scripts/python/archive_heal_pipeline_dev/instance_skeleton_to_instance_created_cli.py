import os, sys
import pandas as pd
import json
from cedar.utils import getter, updater, searcher, storer

def main(folder_id = None, permission_type = "write"):
    server_address = "https://resource." + os.environ['CEDAR_HOST']
    api_key = "apiKey " + os.environ['CEDAR_API_KEY']

    user_uuid = sys.argv[1]
    instance_skeleton_path = sys.argv[2]
    metadata_path = sys.argv[3]
    metadata_to_instance_map_path = sys.argv[4]
    folder_id = sys.argv[5]
    permission_type = sys.argv[6]

    # construct the full user id from raw uuid input here
    user_id = user_id_from_uuid(user_uuid)
    # load the empty template instance skeleton
    instance_skeleton = load_instance_skeleton(instance_skeleton_path)
    # create a new empty template instance from the skeleton, add locally available metadata to the instance 
    instance = add_metadata_to_instance(instance_skeleton, metadata_path, metadata_to_instance_map_path)
    # create the instance on cedar, grab the cedar-assigned instance id
    instance_text, instance_id = create_instance_on_cedar(server_address, api_key, instance)
    # give the user specified permissions to instance (default permission is write)
    add_single_user_permission_to_instance(server_address, api_key, instance_id, user_id, permission_type)

def load_instance_skeleton(instance_skeleton_path):
    with open(instance_skeleton_path, 'r') as myfile:
    data=myfile.read()

    # parse file
    instance_skeleton = json.loads(data)

    return instance_skeleton

def add_metadata_to_instance(instance_skeleton, metadata_path, metadata_to_instance_map_path):
    instance = instance_skeleton

    # this is a placeholder for some population activities
    instance['pubs']['secondary pubs'] = [{"@value":"doi: 789"},{"@value":"doi: 101112"}]

    return instance

def create_instance_on_cedar(server_address, api_key, instance):
    
    ## create POST request url and header
    request_url = server_address + "/template-instances"

    headers = {
            'Content-Type': "application/json",
            'Authorization': api_key
        }

    ## make POST call
    response = requests.request("POST", request_url, json=instance, headers=headers, verify=False)

    ## grab POST call response and save new instance ID
    instance_created_text = json.loads(response.text)
    instance_created_id = instance_created["@id"]

    return instance_created_text, instance_created_id
