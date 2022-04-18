# this scripts takes a template id and a cedar user uuid, finds the most recently created instance of the template, and shares specified access type with the user

import os, sys
import pandas as pd
from cedar.utils import getter, updater, searcher, storer

def main(permission_type = "write", instance_creator_uuid = None):
    server_address = "https://resource." + os.environ['CEDAR_HOST']
    api_key = "apiKey " + os.environ['CEDAR_API_KEY']

    template_id = sys.argv[1]
    user_uuid = sys.argv[2]
    permission_type = sys.argv[3]
    instance_creator_uuid = sys.argv[4]

    # construct the full user and instance creator ids here
    user_id = user_id_from_uuid(user_uuid)
    
    if instance_creator_uuid is not None:
        instance_creator_id = user_id_from_uuid(instance_creator_uuid)
    else:
        instance_creator_id = None

    # get the instance of the template that was most recently created
    # if instance creator is provided, get the instance of the template that was most recently created by the instance creator
    instance_id = get_latest_instance(server_address, api_key, template_id, instance_creator_id)

    # give the user specified permissions to instance (default permission is write)
    add_single_user_permission_to_instance(server_address, api_key, instance_id, user_id, permission_type)


def user_id_from_uuid(uuid):
    return "https://metadatacenter.org/users/" + uuid
    
def get_latest_instance(server_address, api_key, template_id, instance_creator_id = None):

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

    if len(instances_df.index) < 1:
            raise Exception("There are no instances of the specified template")

    # if provided a instance creator id, filter the template instances by creator == platform
    if instance_creator_id is not None:
        creator_created = instances_df['created_by'] == instance_creator_id
        instances_df = instances_df[creator_created]

        if len(instances_df.index) < 1:
            raise Exception("The specified user has not created any instances of the specified template")

    # sort by time created with latest value first and get the first row (most recently created)    
    instances_df = instances_df.sort_values(by=['created_on'], ascending=False)
    instance_id = instances_df['id'][0]

    return instance_id

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


if __name__ == "__main__":
    main()
