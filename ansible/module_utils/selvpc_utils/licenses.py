from collections import defaultdict
from operator import itemgetter

from selvpcclient.base import ParticleResponse

from ansible.module_utils.selvpc_utils import common, wrappers


def parse_licenses_to_add(licenses):
    """
    Parse "licenses" values
    :param dict licenses
    :rtype: dict ((region, type), quantity)
    """
    result = defaultdict(lambda: 0)
    for lic in licenses:
        result[(lic.get("region"), lic.get("type"))] += lic.get("quantity")
    return result


def get_project_licenses_quantity(client, project_id):
    """
    :param 'Client' client
    :param string project_id
    :rtype: dict
    """
    result = defaultdict(lambda: {"ACTIVE": 0, "DOWN": 0})
    for lic in client.licenses.list(project_id=project_id):
        result[(lic.region, lic.type)][lic.status] += 1
    return result


def delete_useless_licenses(client, to_delete, project_id):
    """
    :param 'Client' client
    :param dict to_delete: licenses quantity
    :param string project_id
    :rtype: list
    """
    result = []
    licenses = [
        lic_obj._info
        for lic_obj in client.licenses.list(project_id=project_id)
    ]
    for key in to_delete:
        lics_to_delete = [lic for lic in licenses if (
            lic.get("region"),
            lic.get("type")) == key]
        lics_to_delete.sort(key=itemgetter("status"), reverse=True)
        for lic in lics_to_delete[:to_delete.get(key)]:
            client.licenses.delete(lic.get("id"))
            result.append(lic.get("id"))
    return result


@wrappers.create_object('license')
@common.check_project_id
def add_licenses(module, client, project_id, project_name, licenses, force):
    jsonifed_result, changed, msg = {}, False, []
    if not common._check_valid_quantity(licenses):
        module.fail_json(msg="Wrong 'quantity'")

    parsed_lics = parse_licenses_to_add(licenses)
    actual_lics = get_project_licenses_quantity(client, project_id)
    to_create, to_delete = common.compare_existed_and_needed_objects(
        actual_lics, parsed_lics, force)
    to_create = [{'region': params[0],
                  'type': params[1],
                  'quantity': quantity}
                 for params, quantity in to_create.items() if quantity]

    if to_create:
        result = client.licenses.add(project_id,
                                     {"licenses": to_create})
        if isinstance(result, ParticleResponse):
            common.abort_particle_response_task(module, client, result)
        changed = True
        msg.append("licenses have been added")
        jsonifed_result.update({"added": result})
    if to_delete:
        result = delete_useless_licenses(client, to_delete, project_id)
        changed = True
        msg.append("some licenses have been deleted")
        jsonifed_result.update({"deleted": result})
    return jsonifed_result, changed, common.generate_result_msg(msg)


@wrappers.delete_object
def delete_license(module, client, license_id):
    client.licenses.delete(license_id)


@wrappers.get_object('license')
def get_licenses(module, client, license_id, detailed, show_list=False):
    if not show_list:
        return client.licenses.show(license_id)
    return client.licenses.list(detailed)
