from collections import defaultdict
from operator import itemgetter

from selvpcclient.base import PartialResponse

from ansible.module_utils.selvpc_utils import common, wrappers


def parse_subnets_to_add(subnets):
    """
    Parse subnets from param
    :param list subnets
    :rtype: dict((region, type, prefix_length), (state:quantity))
    """
    result = defaultdict(lambda: 0)
    for sub in subnets:
        result[(sub.get("region"),
                sub.get("type"),
                sub.get("prefix_length"))] += sub.get("quantity")
    return result


def get_project_subnets_quantity(client, project_id):
    """
    Parse subnets from param
    :param 'Client' client
    :param string project_id
    :rtype: dict((region, type, prefix_length), (state:quantity))
    """
    # TODO: change 'type' key
    result = defaultdict(lambda: {"ACTIVE": 0, "DOWN": 0})
    for sub in client.subnets.list(project_id=project_id):
        result[(sub.region, "ipv4", int(sub.cidr[-2:]))][sub.status] += 1
    return result


def delete_useless_subnets(client, to_delete, project_id):
    """
    :param 'Client' client
    :param dict((region, type, prefix_length), (state:quantity)) to_delete
    :rtype: list
    """
    result = []
    subnets = [sub_obj._info
               for sub_obj in client.subnets.list(project_id=project_id)]
    for key in to_delete:
        subs_to_delete = [sub for sub in subnets if (
            sub.get("region"), "ipv4", int(sub.get("cidr")[-2:])) == key]
        subs_to_delete.sort(key=itemgetter("status"), reverse=True)
        for sub in subs_to_delete[:to_delete.get(key)]:
            client.subnets.delete(sub.get("id"))
            result.append(sub.get("id"))
    return result


@wrappers.create_object('subnet')
@common.check_project_id
def add_subnets(module, client, project_id, project_name, subnets, force):
    jsonifed_result, changed, msg = {}, False, []
    if not common._check_valid_quantity(subnets):
        module.fail_json(msg="Wrong 'quantity'")

    parsed_subs = parse_subnets_to_add(subnets)
    actual_subs = get_project_subnets_quantity(client, project_id)
    to_create, to_delete = common.compare_existed_and_needed_objects(
        actual_subs, parsed_subs, force)
    to_create = [{'region': params[0],
                  'type': params[1],
                  'prefix_length': params[2],
                  'quantity': quantity}
                 for params, quantity in to_create.items() if quantity]

    if to_create:
        result = client.subnets.add(project_id, {"subnets": to_create})
        if isinstance(result, PartialResponse):
            common.abort_particle_response_task(module, client, result)
        changed = True
        msg.append("subnets have been added")
        jsonifed_result.update({"added": result})
    if to_delete:
        result = delete_useless_subnets(
            client, to_delete, project_id)
        changed = True
        msg.append("some subnets have been deleted")
        jsonifed_result.update({"deleted": result})
    return jsonifed_result, changed, common.generate_result_msg(msg)


@wrappers.delete_object
def delete_subnet(module, client, subnet_id):
    client.subnets.delete(subnet_id)


@wrappers.get_object('subnet')
def get_subnets(module, client, subnet_id, show_list=False):
    if not show_list:
        return client.subnets.show(subnet_id)
    return client.subnets.list()
