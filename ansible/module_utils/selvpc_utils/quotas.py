from selvpcclient.base import PartialResponse

from ansible.module_utils.selvpc_utils import common, wrappers


@wrappers.create_object('quotas')
@common.check_project_id
def set_quotas(module, client, project_id, project_name, quotas):
    result, changed, msg = None, False, "Project has already had such quotas"
    if common._check_quotas_changes(client, quotas, project_id):
        result = client.quotas.update(project_id, {"quotas": quotas})
        if isinstance(result, PartialResponse):
            common.abort_particle_response_task(
                module, client, result, project_id,
                is_quotas=True)
        changed, msg = True, "Quotas are set successfully"
    return result, changed, msg


@wrappers.get_object('quotas')
@common.check_project_id
def get_project_quotas(module, client, project_id, project_name,
                       show_list=False):
    if not show_list:
        return client.quotas.get_project_quotas(project_id)
    return client.quotas.get_projects_quotas()
