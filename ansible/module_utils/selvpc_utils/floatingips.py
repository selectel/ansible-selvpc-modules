from collections import defaultdict
from operator import itemgetter

from selvpcclient.base import ParticleResponse
from selvpcclient.exceptions.base import ClientException

from ansible.module_utils.selvpc_utils.common import (check_project_id,
                                                      compare_existed_and_needed_objects,
                                                      _check_valid_quantity,
                                                      get_floatingip_by_ip,
                                                      _check_valid_ip,
                                                      generate_result_msg,
                                                      abort_particle_response_task)
from ansible.module_utils.selvpc_utils.wrappers import (create_object_wrapper,
                                                        get_object_wrapper,
                                                        delete_object_wrapper)


def parse_floatingips_to_add(floatingips):
    """
    Parse "floatingips" values
    :param dict floatingips: Floating ips
    :rtype: dict (region, quantity)
    """
    result = defaultdict(lambda: 0)
    for ip in floatingips:
        result[ip.get("region")] += ip.get("quantity")
    return result


def get_project_ips_quantity(client, project_id):
    """
    Get all existing floating ips in projects
    :param 'Client' client
    :param string project_id:
    :rtype: dict (region, dict(state: quantity))
    """
    result = defaultdict(lambda: {"ACTIVE": 0, "DOWN": 0})
    for ip in client.floatingips.list(project_id=project_id):
        result[ip.region][ip.status] += 1
    return result


def delete_useless_ips(client, to_delete, project_id):
    """
    Delete a bulk of floating ips for select project
    :param 'Client' client
    :param dict to_delete: (region, dict(state: quantity))
    :param string project_id:
    :rtype: list
    """
    result = []
    ips = [ip_obj._info for ip_obj in
           client.floatingips.list(project_id=project_id)]
    for region in to_delete:
        ips_to_delete = [ip for ip in ips if ip.get("region") == region]
        ips_to_delete.sort(key=itemgetter("status"), reverse=True)
        for ip in ips_to_delete[:to_delete.get(region)]:
            client.floatingips.delete(ip.get("id"))
            result.append(ip.get("id"))
    return result


@create_object_wrapper('floatingip')
@check_project_id
def add_floatingips(module, client, project_id,
                    project_name, floatingips, force):
    jsonifed_result, changed, msg = {}, False, []
    if not _check_valid_quantity(floatingips):
        module.fail_json(msg="Wrong 'quantity'")

    parsed_ips = parse_floatingips_to_add(floatingips)
    actual_ips = get_project_ips_quantity(client, project_id)
    to_create, to_delete = compare_existed_and_needed_objects(actual_ips,
                                                              parsed_ips,
                                                              force)
    to_create = [{'region': region, 'quantity': quantity}
                 for region, quantity in to_create.items() if quantity]

    if to_create:
        result = client.floatingips.add(
            project_id, {"floatingips": to_create})
        if isinstance(result, ParticleResponse):
            abort_particle_response_task(module, client, result)
        changed = True
        msg.append("floating ips have been added")
        jsonifed_result.update({"added": result})
    if to_delete:
        result = delete_useless_ips(client, to_delete, project_id)
        changed = True
        msg.append("some ips have been deleted")
        jsonifed_result.update({"deleted": result})
    return jsonifed_result, changed, generate_result_msg(msg)


@delete_object_wrapper
def delete_floatingip(module, client, floatingip_id, floatingip):
    if not floatingip_id:
        if not _check_valid_ip(floatingip):
            module.fail_json(msg="IP {} is not valid".format(floatingip))
        floatingip = get_floatingip_by_ip(client, floatingip)
        if not floatingip:
            raise ClientException
        floatingip_id = floatingip.id
    client.floatingips.delete(floatingip_id)


@get_object_wrapper('floatingip')
def get_floatingips(module, client, floatingip_id, show_list=False):
    if not show_list:
        return client.floatingips.show(floatingip_id)
    return client.floatingips.list()
