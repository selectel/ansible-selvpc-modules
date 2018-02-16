from ansible.module_utils.selvpc_utils import common, wrappers


@wrappers.create_object('user')
def create_user(module, client, username, password, enabled):
    changed, msg = False, "User {} has already been created" \
        .format(username)
    user = common.get_user_by_name(client, username)
    if not user:
        result = client.users.create(username, password, enabled=enabled)
        changed, msg = True, "User {} has been created".format(result.id)
        return result, changed, msg
    return user, changed, msg


@wrappers.get_object('user')
def get_users(module, client):
    return client.users.list()


@wrappers.update_object
def update_user(module, client, user_id, new_username, new_password, enabled):
    client.users.update(user_id, new_username, new_password, enabled=enabled)
    return True, "User has been updated"


@wrappers.delete_object
def delete_user(module, client, user_id):
    client.users.delete(user_id)
