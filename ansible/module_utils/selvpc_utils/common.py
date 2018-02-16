import ipaddress
from functools import wraps

from selvpcclient.exceptions.base import ClientException


def _check_project_exists(client, project_id):
    try:
        client.projects.show(project_id)
    except ClientException:
        return False
    return True


def _check_user_exists(client, user_id):
    for user in client.users.list():
        if user == user_id:
            return True
    return False


def _check_user_role(client, project_id, user_id):
    roles = client.roles.get_project_roles(project_id)
    for role in roles:
        if role.user_id == user_id:
            return True
    return False


def _check_quotas_changes(client, after_quotas, project_id):
    before_quotas = client.quotas.get_project_quotas(project_id)
    before_quotas_json = before_quotas._info
    for key in after_quotas:
        for quota in after_quotas[key]:
            item = [
                item for item in before_quotas_json[key]
                if (item["region"] == quota["region"] and
                    item["zone"] == quota["zone"] and
                    item["value"] == quota["value"])
            ]
            if not item:
                return True
    return False


def _check_project_roles(client, roles):
    to_add = []
    try:
        for role in roles:
            if role not in [
                r._info for r in
                client.roles.get_project_roles(role["project_id"])
            ]:
                to_add.append(role)
    except ClientException:
        raise ClientException(message="No such project")
    return to_add


def _check_valid_quantity(objects):
    for obj in objects:
        if obj["quantity"] < 0:
            return False
    return True


def _check_valid_ip(floatingip):
    # Python 3 compatibility hack
    try:
        unicode('')
    except NameError:
        unicode = str
    try:
        ipaddress.ip_address(unicode(floatingip))
    except Exception:
        return False
    return True


def generate_result_msg(msg):
    default = "Desirable state already in project"
    return " ".join(msg).capitalize() if msg else default


def get_project_by_name(client, project_name):
    projects = client.projects.list()
    for project in projects:
        if project.name == project_name:
            return project


def get_user_by_name(client, username):
    users = client.users.list()
    for user in users:
        if user.name == username:
            return user


def get_floatingip_by_ip(client, floatingip):
    for fip in client.floatingips.list():
        if fip.floating_ip_address == floatingip:
            return fip


def compare_existed_and_needed_objects(before, after, force):
    """
    Compares two dicts
    :param boolean force: param for deleting "ACTIVE" status objects
    (if needed)
    :param dict before: objects that we have in project
    :param dict after: objects that need to create
    :return: objects that need to create and dict with quantity objects that
    have to be deleted
    :rtype: tuple(dict, dict)
    """
    possible_task = True
    to_create = dict((key, before.get(key))
                     for key in before if key in after)
    to_delete = {}
    for n_key in after:
        if possible_task:
            if n_key not in before:
                to_create.update({n_key: after.get(n_key)})
            else:
                active = before.get(n_key)["ACTIVE"]
                down = before.get(n_key)["DOWN"]
                before_quantity = active + down
                after_quantity = after.get(n_key)
                if after_quantity == before_quantity:
                    to_create.pop(n_key)
                elif after_quantity < before_quantity:
                    to_create.pop(n_key)
                    if not force:
                        if (down >= after_quantity - active and
                                after_quantity >= active):
                            to_delete.update(
                                {n_key: down - (after_quantity - active)})
                        else:
                            possible_task = False
                    else:
                        to_delete.update(
                            {n_key: before_quantity - after_quantity})
                else:
                    to_create[n_key] = after_quantity - before_quantity

    if possible_task:
        return to_create, to_delete
    return {}, {}


def check_project_id(func):
    """
    Decorator checks 'project_id' param and if it's None than tries to find
    specific project by 'project_name'. If it's not found than raises
    an exception.
    :param func: function
    :return: decorated func
    """

    @wraps(func)
    def inner(*args, **kwargs):
        module, cli, project_id, project_name = args[:4]
        show_list = kwargs.get("show_list")
        if show_list:
            return func(module, cli, project_id, project_name, *args[4:],
                        show_list=show_list)
        if not project_id:
            project = get_project_by_name(cli, project_name)
            try:
                if not project:
                    raise ClientException(message="No such project")
                project_id = project.id
            except ClientException as exp:
                module.fail_json(msg=str(exp))
        return func(module, cli, project_id, project_name, *args[4:])

    return inner


def make_plural(word):
    if not word.endswith('s'):
        return word + 's'
    return word


def clear_quotas(quotas):
    to_clear = {"quotas": {}}
    for item in quotas:
        to_clear["quotas"].update(
            {
                item["resource"]: {"region": item["region"], "value": 0}
            }
        )
    return to_clear


def abort_particle_response_task(module, client, resp, project_id=None,
                                 is_quotas=False):
    """Delete all created objects and generate message."""

    if not is_quotas:
        for obj in resp:
            obj.delete()
    else:
        client.quotas.update(project_id, clear_quotas(resp.resources))
    res_json = {
        "error": "207 Multi-status",
        "details": resp.get_fail_info()
    }
    module.fail_json(result=res_json, changed=False, msg="Task aborted")
