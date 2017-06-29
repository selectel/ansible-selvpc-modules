from ansible.module_utils.selvpc_utils.common import get_user_by_name
from ansible.module_utils.selvpc_utils.wrappers import (create_object_wrapper,
                                                        get_object_wrapper,
                                                        update_object_wrapper,
                                                        delete_object_wrapper)


@create_object_wrapper('user')
def create_user(module, client, username, password, enabled):
    changed, msg = False, "User {} has already been created" \
        .format(username)
    user = get_user_by_name(client, username)
    if not user:
        result = client.users.create(username, password, enabled=enabled)
        changed, msg = True, "User {} has been created".format(result.id)
        return result, changed, msg
    return user, changed, msg


@get_object_wrapper('user')
def get_users(module, client):
    return client.users.list()


@update_object_wrapper
def update_user(module, client, user_id, new_username, new_password, enabled):
    client.users.update(user_id, new_username, new_password, enabled=enabled)
    return True, "User has been updated"


@delete_object_wrapper
def delete_user(module, client, user_id):
    client.users.delete(user_id)
