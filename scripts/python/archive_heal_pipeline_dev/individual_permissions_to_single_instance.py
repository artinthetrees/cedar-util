import os, sys
import pandas as pd
from cedar.utils import getter, updater, searcher

def main():
    # Program parameters
    user_id = sys.argv[1] # this will be the uuid of the person registering a study on the heal platform, which we will ask them to provide
    pre_instance_file = sys.argv[2] # the path to the empty instance file the platform has filled partially for the person registering the study

    permission_type = sys.argv[3] # we will generally want to share "write" permissions for this application
    template_id = sys.argv[4] # this will be the template id of the heal study-level core metadata template
    platform_id = sys.argv[5] # this will be the uuid of the heal platform org account on cedar

    server_address = "https://resource." + os.environ['CEDAR_HOST']
    api_key = "apiKey " + os.environ['CEDAR_API_KEY']

    # construct the full user ids here
    if user_id is not None:
        user_full_id = "https://metadatacenter.org/users/" + user_id

    if platform_id is not None:
        platform_full_id = "https://metadatacenter.org/users/" + platform_id
    
    # print("Adding permission " + permission_type + " to user " + user_id + " for template instance " + instance_id)

    # for now assume that instance id is input parameter
    # in real implementation, only input will be uuid
    # platform will create the instance with partially filled values, then will need to POST to create the instance on CEDAR
    # then will need to GET the instance id that CEDAR assigned to the new instance

    # QUESTION:
    # (how do we GET the instance id that CEDAR assigned to the new instance? can we get all instances with a time stamp and
    # select the one with the most recent time stamp?)


    # NOTE:
    # 1) seems like i'm not getting instances listed for a template when i know that instances do exist - why?
    #     RESOLVED: i was using a substring of the template id; when i used the full template id, it returns the
    #               instance ids; number 2) below still would be good to address though not critical
    # 2) if there are zero instances it seems like the search_instances_of function fails unless i set a max_count parameter
    #    if i set a max_count parameter to a positive value, the function finishes and returns an empty array - seems like the function
    #    should not fail but exit with an informative error if there are no instances even if max_count is not specified

    instance_ids = searcher.search_instances_of(server_address, api_key, template_id)
    
    createdOn = []
    createdBy = []

    for instance_id in instance_ids:
        # get "pav:createdOn" and "pav:createdBy" fields for each instance;
        # add to a df with row for each instance; columns for instance id, createdOn, createdBy
        instance_details = getter.get_instance_details(server_address, api_key, instance_id)
        createdOn = createdOn.append(instance_details['createdOnTS'])
        createdBy = createdBy.append(instance_details['pav:createdBy']

    instances_df = pd.DataFrame({'id':instance_ids,'created_on':createdOn,'created_by':createdBy})
                                     
       
        # QUESTION:
        # for a list of instances how do we get "pav:createdOn" and "pav:createdBy" fields for each instance?
        # in the array of instances that are returned by search_instances_of, are the instances sorted in descending order of creation?
        # if so, maybe we can skip actually grabbing these fields and just take the first instance id in the returned array


    # filter df of instance ids on createdBy HEAL Platform (format of field value is "https://metadatacenter.org/users/" + UUID)
    # sort descending by createdOn (this is a datetime with second resolution)
    # grab the instance id of the first df row (most recently created)
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
