from collections import defaultdict
from operator import itemgetter

from ansible.module_utils.selvpc_utils import common, wrappers
from selvpcclient.base import PartialResponse


def parse_vrrp_subnets_to_add(vrrp_subnets):
    """
    Parse vrrp_subnets from param
    :param list vrrp_subnets
    :rtype: dict((prefix_length, type, master_region, slave_region),
                (state:quantity))
    """
    result = defaultdict(lambda: 0)
    for sub in vrrp_subnets:
        result[(sub.get("prefix_length"),
                sub.get("type"),
                sub.get("master_region"),
                sub.get("slave_region"),)] += sub.get("quantity")
    return result


def get_project_vrrp_subnets_quantity(client, project_id):
    """
    Parse vrrp_subnets from param
    :param 'Client' client
    :param string project_id
    :rtype: dict((prefix_length, type, master_region, slave_region),
                (state:quantity))
    """
    # TODO: change 'type' key
    result = defaultdict(lambda: {"ACTIVE": 0, "DOWN": 0})
    for sub in client.vrrp.list(project_id=project_id):
        result[(int(sub.cidr.split('/')[1]), "ipv4",
                sub.master_region, sub.slave_region)][sub.status] += 1
    return result


def delete_useless_vrrp_subnets(client, to_delete, project_id):
    """
    :param 'Client' client
    :param dict((prefix_length, type, master_region, slave_region),
                (state:quantity)) to_delete
    :rtype: list
    """
    result = []
    vrrp_subnets = client.vrrp.list(project_id=project_id)
    for key in to_delete:
        vrrp_to_delete = [vrrp for vrrp in vrrp_subnets if (
            int(vrrp.cidr.split('/')[1]), "ipv4",
            vrrp.master_region, vrrp.slave_region) == key]
        vrrp_to_delete.sort(key=itemgetter("status"), reverse=True)
        for vrrp in vrrp_to_delete[:to_delete.get(key)]:
            client.vrrp.delete(vrrp.id)
            result.append(vrrp.id)
    return result


@wrappers.create_object('vrrp')
@common.check_project_id
def add_vrrp_subnets(module, client, project_id, project_name, vrrp_subnets,
                     force):
    jsonifed_result, changed, msg = {}, False, []
    if not common._check_valid_quantity(vrrp_subnets):
        module.fail_json(msg="Wrong 'quantity'")

    parsed_subs = parse_vrrp_subnets_to_add(vrrp_subnets)
    actual_subs = get_project_vrrp_subnets_quantity(client, project_id)
    to_create, to_delete = common.compare_existed_and_needed_objects(
        actual_subs, parsed_subs, force)
    to_create = [{'prefix_length': params[0],
                  'type': params[1],
                  'quantity': quantity,
                  'regions':
                      {'master': params[2],
                       'slave': params[3],
                       },
                  }
                 for params, quantity in to_create.items() if quantity]
    if to_delete:
        result = delete_useless_vrrp_subnets(
            client, to_delete, project_id)
        changed = True
        msg.append("some subnets have been deleted")
        jsonifed_result.update({"deleted": result})
    if to_create:
        result = client.vrrp.add(project_id, {"vrrp_subnets": to_create})
        if isinstance(result, PartialResponse):
            common.abort_partial_response_task(module, client, result)
        changed = True
        msg.append("vrrp subnets have been added")
        jsonifed_result.update({"added": result})

    return jsonifed_result, changed, common.generate_result_msg(msg)


@wrappers.delete_object
def delete_vrrp_subnet(module, client, vrrp_subnet_id):
    client.vrrp.delete(vrrp_subnet_id)


@wrappers.get_object('vrrp')
def get_vrrp_subnets(module, client, vrrp_subnet_id, show_list):
    if not show_list:
        return client.vrrp.show(vrrp_subnet_id)
    return client.vrrp.list()
