from ansible.module_utils.selvpc_utils.common import (_check_user_role,
                                                      _check_project_roles,
                                                      check_project_id)

from ansible.module_utils.selvpc_utils.wrappers import (create_object_wrapper,
                                                        get_object_wrapper,
                                                        delete_object_wrapper)


@create_object_wrapper('role')
@check_project_id
def add_role(module, client, project_id, project_name, user_id):
    result, changed, msg = None, False, "User is {} already in {} project" \
        .format(user_id, project_id)
    if not _check_user_role(client, project_id, user_id):
        client.roles.add_user_role_in_project(project_id, user_id)
        changed, msg = True, "User {} has been added to {} project" \
            .format(user_id, project_id)
    return result, changed, msg


@create_object_wrapper('role')
def add_bulk_roles(module, client, roles):
    result, changed, msg = None, False, "Roles are already in project"
    to_add = _check_project_roles(client, roles)
    if to_add:
        result = client.roles.add({"roles": to_add})
        changed, msg = True, "Roles have been added successfully"
    return result, changed, msg


@delete_object_wrapper
@check_project_id
def delete_role(module, client, project_id, project_name, user_id):
    client.roles.delete_user_role_from_project(project_id, user_id)


@get_object_wrapper('role')
@check_project_id
def get_project_roles(module, client, project_id, project_name):
    return client.roles.get_project_roles(project_id)


@get_object_wrapper('role')
def get_user_roles(module, client, user_id):
    return client.roles.get_user_roles(user_id)
