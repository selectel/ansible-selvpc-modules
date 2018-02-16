from ansible.module_utils.selvpc_utils import common, wrappers


@wrappers.create_object('project')
def create_project(module, client, project_name):
    result = client.projects.create(project_name)
    changed, msg = True, "Project '{}' has been created" \
        .format(project_name)
    return result, changed, msg


@wrappers.get_object('project')
@common.check_project_id
def get_project(module, client, project_id, project_name, show_list=False):
    if not show_list:
        return client.projects.show(project_id)
    return client.projects.list()


@wrappers.update_object
@common.check_project_id
def update_project(module, client, project_id, project_name,
                   new_project_name):
    changed, msg = False, "Nothing to change"
    if not common.get_project_by_name(client, new_project_name):
        client.projects.update(project_id, new_project_name)
        changed, msg = True, "Project updated"
    else:
        msg = "Project with such name already exists"
    return changed, msg


@wrappers.delete_object
@common.check_project_id
def delete_project(module, client, project_id, project_name):
    client.projects.delete(project_id)
