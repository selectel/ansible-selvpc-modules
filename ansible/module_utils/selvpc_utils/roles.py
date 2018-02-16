from ansible.module_utils.selvpc_utils import common, wrappers


@wrappers.create_object('role')
@common.check_project_id
def add_role(module, client, project_id, project_name, user_id):
    result, changed, msg = None, False, "User is {} already in {} project" \
        .format(user_id, project_id)
    if not common._check_user_role(client, project_id, user_id):
        client.roles.add_user_role_in_project(project_id, user_id)
        changed, msg = True, "User {} has been added to {} project" \
            .format(user_id, project_id)
    return result, changed, msg


@wrappers.create_object('role')
def add_bulk_roles(module, client, roles):
    result, changed, msg = None, False, "Roles are already in project"
    to_add = common._check_project_roles(client, roles)
    if to_add:
        result = client.roles.add({"roles": to_add})
        changed, msg = True, "Roles have been added successfully"
    return result, changed, msg


@wrappers.delete_object
@common.check_project_id
def delete_role(module, client, project_id, project_name, user_id):
    client.roles.delete_user_role_from_project(project_id, user_id)


@wrappers.get_object('role')
@common.check_project_id
def get_project_roles(module, client, project_id, project_name):
    return client.roles.get_project_roles(project_id)


@wrappers.get_object('role')
def get_user_roles(module, client, user_id):
    return client.roles.get_user_roles(user_id)
