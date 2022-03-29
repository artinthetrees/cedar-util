import os, sys
from cedar.utils import getter, updater, searcher



def main():
    # Program parameters
    server_address = "https://resource." + os.environ['CEDAR_HOST']

    user_id = sys.argv[1]
    instance_id = sys.argv[2]
    permission_type = sys.argv[3]
    template_id = sys.argv[4]
    api_key = "apiKey " + os.environ['CEDAR_API_KEY']
    
    # print("Adding permission " + permission_type + " to user " + user_id + " for template instance " + instance_id)

    # for now assume that instance id is input parameter
    # in real implementation, only input will be uuid
    # platform will create the instance with partially filled values, then will need to POST to create the instance on CEDAR
    # then will need to GET the instance id that CEDAR assigned to the new instance

    # QUESTION:
    # (how do we GET the instance id that CEDAR assigned to the new instance? can we get all instances with a time stamp and
    # select the one with the most recent time stamp?)

    instance_ids = searcher.search_instances_of(server_address, api_key, template_id)
    for instance_id in instance_ids:
        add_group_permission_to_instance(server_address, api_key, instance_id, group_id, permission_type)




def add_group_permission_to_instance(server_address, api_key, instance_id, group_id, permission_type):
    instance_permissions = getter.get_instance_permissions(server_address, api_key, instance_id)
    group_permissions = instance_permissions['groupPermissions']
    if has_no_group_id(group_permissions, group_id):
        print("Adding a new group permission to " + instance_id)
        instance_permissions['groupPermissions'].append(create_group_permission(group_id, permission_type))
        updater.update_instance_permission(server_address, api_key, instance_id, instance_permissions)

def add_single_user_permission_to_instance(server_address, api_key, instance_id, user_id, permission_type):

    # get the permissions on the instance
    instance_permissions = getter.get_instance_permissions(server_address, api_key, instance_id)
    group_permissions = instance_permissions['groupPermissions']
    if has_no_group_id(group_permissions, group_id):
        print("Adding a new group permission to " + instance_id)
        instance_permissions['groupPermissions'].append(create_group_permission(group_id, permission_type))
        updater.update_instance_permission(server_address, api_key, instance_id, instance_permissions)        


def has_no_group_id(group_permissions, group_id):
    for group_permission in group_permissions:
        current_group_id = group_permission['group']['@id']
        if current_group_id == group_id:
            return False
    return True


def create_group_permission(group_id, permission_type):
    return {
        'group': {
            '@id': group_id
        },
        'permission': permission_type
    }


if __name__ == "__main__":
    main()
