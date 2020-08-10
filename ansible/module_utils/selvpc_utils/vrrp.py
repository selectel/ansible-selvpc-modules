from collections import defaultdict
from operator import itemgetter

from selvpcclient.base import ParticleResponse

from ansible.module_utils.selvpc_utils import common,wrappers


def parse_vrrp_to_add(vrrps):
    result = defaultdict(lambda: 0)
    for vrrp in vrrps:
        result[(vrrp.get("master"),
                vrrp.get("slave"),
                vrrp.get("type"),
                vrrp.get("prefix_length"))] += vrrp.get("quantity")
    return result

def get_project_vrrp_quantity(client, project_id):
    result = defaultdict(lambda: {"ACTIVE": 0, "DOWN": 0})
    for vrrp in client.vrrp.list(project_id=project_id):
        result[(vrrp.master_region,
                vrrp.slave_region,
                "ipv4",
                int(vrrp.cidr[-1:]))][vrrp.status] += 1
    return result

def delete_useless_vrrp(client, to_delete, project_id):
    """
    :param 'Client' client
    :param dict((master_region, slave_region, type, prefix_length), (state:quantity)) to_delete
    :rtype: list
    """
    result = []
    vrrps = [vrrp_obj._info
               for vrrp_obj in client.vrrp.list(project_id=project_id)]
    for key in to_delete:
        vrrp_to_delete = [vrrp for vrrp in vrrps if (
            vrrp.get("master_region"),
            vrrp.get("slave_region"),
            "ipv4",
            int(vrrp.get("cidr")[-2:])) == key]
        vrrp_to_delete.sort(key=itemgetter("status"), reverse=True)
        for sub in vrrp_to_delete[:to_delete.get(key)]:
            client.vrrp.delete(sub.get("id"))
            result.append(sub.get("id"))
    return result


@wrappers.create_object('vrrp')
@common.check_project_id
def add_vrrp(module, client, project_id, project_name, vrrps, force):
    jsonifed_result, changed, msg = {}, False, []
    if not common._check_valid_quantity(vrrps):
        module.fail_json(msg="Wrong 'quantity'")

    parsed_vrrp = parse_vrrp_to_add(vrrps)
    actual_vrrp = get_project_vrrp_quantity(client,project_id)
    to_create, to_delete = common.compare_existed_and_needed_objects(
        actual_vrrp, parsed_vrrp, force)
    to_create = [{'regions':{
                            'master_region': params[0],
                            'slave_region': params[1]},
                  'type': params[2],
                  'prefix_length': params[3],
                  'quantity': quantity}
                 for params, quantity in to_create.items() if quantity]
    if to_create:
        result = client.vrrp.add(project_id, {"vrrp_subnets": to_create})
        if isinstance(result, ParticleResponse):
            common.abort_particle_response_task(module, client, result)
        changed = True
        msg.append("vrrp have been added")
        jsonifed_result.update({"added": result})
    if to_delete:
        result = delete_useless_vrrp(
            client, to_delete, project_id)
        changed = True
        msg.append("some vrrp have been deleted")
        jsonifed_result.update({"deleted": result})
    return jsonifed_result, changed, common.generate_result_msg(msg)

@wrappers.delete_object
def delete_vrrp(module, client, vrrp_id):
    client.vrrp.delete(vrrp_id)

@wrappers.get_object('vrrp')
def get_vrrp(module, client, vrrp_id, show_list=False):
    if not show_list:
        return client.vrrp.show(vrrp_id)
    return client.vrrp.list()
