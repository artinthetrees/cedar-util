import os, sys
from cedar.utils import getter, updater, searcher


def main():
    # Program parameters
    server_address = "https://resource." + os.environ['CEDAR_HOST']
    api_key = "apiKey " + os.environ['CEDAR_API_KEY']
    
    template_id = sys.argv[1]
    template_creator_id = 
    user_uuid_id = sys.argv[2]
    permission_type = sys.argv[3]

    instance_ids = searcher.search_instances_of(server_address, api_key, template_id)
    for instance_id in instance_ids:
        add_group_permission_to_instance(server_address, api_key, instance_id, group_id, permission_type)

def user_id_from_uuid(uuid):
    return "https://metadatacenter.org/users/" + uuid
    
def find_latest_instance(server_address, api_key, template_id, creator_id):

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


def add_group_permission_to_instance(server_address, api_key, instance_id, group_id, permission_type):
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
