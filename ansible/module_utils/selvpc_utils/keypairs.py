from ansible.module_utils.selvpc_utils import wrappers, common


def keypair_exists(client, user_id, name):
    keypairs = client.keypairs.list()
    for k in keypairs:
        if k.user_id == user_id and k.name == name:
            return True
    return False


@wrappers.create_object('keypair')
def create_keypair(module, client, keypair):
    result, changed = None, False
    user_id = keypair.get('user_id')
    name = keypair.get('name')
    public_key = keypair.get('public_key')
    regions = keypair.get('regions')

    user_exists = common._check_user_exists(client, user_id)
    if not user_exists:
        msg = 'user_id {} does not exist'.format(user_id)
        return result, changed, msg
    key_exists = keypair_exists(client, user_id, name)
    if key_exists:
        msg = 'Key \'{}\' already exists for user {}'.format(name, user_id)
        return result, changed, msg
    else:
        kp = {
            'keypair':
                {'user_id': user_id,
                 'name': name,
                 'public_key': public_key,
                 'regions': regions
                 }
        }
        # Because of @process_pair_params in selvpcclient
        # here must be used keypair as kwarg, not positional
        result = client.keypairs.add(keypair=kp)  # kwarg be
        changed = True
        msg = 'Keypair {} has been created'.format(result[0].name)
        return result, changed, msg


@wrappers.get_object('keypair')
def get_keypairs(module, client):
    return client.keypairs.list()


@wrappers.delete_object
def delete_keypair(module, client, user_id, name):
    client.keypairs.delete(user_id, name)
