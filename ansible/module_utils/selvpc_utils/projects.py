from ansible.module_utils.selvpc_utils.common import (get_project_by_name,
                                                      check_project_id,
                                                      get_customization_params)
from ansible.module_utils.selvpc_utils.wrappers import (create_object_wrapper,
                                                        get_object_wrapper,
                                                        update_object_wrapper,
                                                        delete_object_wrapper)


@create_object_wrapper('project')
def create_project(module, client, project_name):
    result = client.projects.create(project_name)
    changed, msg = True, "Project '{}' has been created" \
        .format(project_name)
    return result, changed, msg


@get_object_wrapper('project')
@check_project_id
def get_project(module, client, project_id, project_name, show_list=False):
    if not show_list:
        return client.projects.show(project_id)
    return client.projects.list()


@update_object_wrapper
@check_project_id
def update_project(module, client, project_id, project_name,
                   new_project_name, cname, logo, color):
    changed, msg = False, "Nothing to change"
    if get_project_by_name(client, new_project_name):
        changed, msg = True, "Project with such name already exists"
    else:
        custom_params = get_customization_params(client, project_id,
                                                 logo,
                                                 color,
                                                 cname)
        if new_project_name:
            custom_params["name"] = new_project_name
        if custom_params:
            client.projects.update(project_id, new_project_name,
                                   **custom_params)
            changed, msg = True, "Project has been updated"
    return changed, msg


@delete_object_wrapper
@check_project_id
def delete_project(module, client, project_id, project_name):
    client.projects.delete(project_id)
