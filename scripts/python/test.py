# this scripts takes a template id and a cedar user uuid, finds the most recently created instance of the template, and shares specified access type with the user

import os, sys
import pandas as pd
from cedar.utils import getter, updater, searcher

server_address = "https://resource." + os.environ['CEDAR_HOST']
api_key = "apiKey " + os.environ['CEDAR_API_KEY']

permission_type = "write"
user_id =  # input just the uuid here 
template_id = "https://repo.metadatacenter.org/templates/a5c99619-7235-4a76-9c48-b51e91488a2f"
platform_id = None # input just the uuid here

# construct the full user ids here
if user_id is not None:
    user_full_id = "https://metadatacenter.org/users/" + user_id

if platform_id is not None:
    platform_full_id = "https://metadatacenter.org/users/" + platform_id

instance_ids = searcher.search_instances_of(server_address, api_key, template_id)

createdOn = []
createdBy = []

for instance_id in instance_ids:
    # get "pav:createdOn" and "pav:createdBy" fields for each instance;
    # add to a df with row for each instance; columns for instance id, createdOn, createdBy
    instance_details = getter.get_instance_details(server_address, api_key, instance_id)
    createdOn.append(instance_details['createdOnTS'])
    createdBy.append(instance_details['pav:createdBy'])
                                 
instance_id = None #reset instance_id index used here since instance_id var name will be used later
instances_df = pd.DataFrame({'id':instance_ids,'created_on':createdOn,'created_by':createdBy})

# if provided a platform cedar user id filter the template instances by creator == platform
if platform_id is not None:
    platform_created = instances_df['created_by'] == platform_full_id
    instances_df = instances_df[platform_created]

# sort by time created with latest value first and get the first row (most recently created)    
instances_df = instances_df.sort_values(by=['created_on'], ascending=False)
instance_id = instances_df['id'][0]

def add_single_user_permission_to_instance(server_address, api_key, instance_id, user_id, permission_type):

    # get the permissions on the instance
    instance_permissions = getter.get_instance_permissions(server_address, api_key, instance_id)
    user_permissions = instance_permissions['userPermissions']

    if has_no_user_id(user_permissions, user_id):
        print("Adding a new user permission to " + instance_id + ": " + permission_type)
        instance_permissions['userPermissions'].append(create_user_permission(user_id, permission_type))
        updater.update_instance_permission(server_address, api_key, instance_id, instance_permissions)        


def has_no_user_id(user_permissions, user_id):
    for user_permission in user_permissions:
        current_user_id = user_permission['user']['@id']
        if current_user_id == user_id:
            return False
    return True

def create_user_permission(user_id, permission_type):
    return {
        'user': {
            '@id': user_id
        },
        'permission': permission_type
    }

add_single_user_permission_to_instance(server_address, api_key, instance_id, user_full_id, permission_type)
