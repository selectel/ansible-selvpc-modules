#!/usr/bin/python
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

import os

from ansible.module_utils.basic import AnsibleModule
from selvpcclient.client import Client, setup_http_client

from ansible.module_utils.selvpc_utils import keypairs as k
from ansible.modules.selvpc import custom_user_agent


DOCUMENTATION = '''
---
module: selvpc_keypairs
short_description: selvpc module for keypairs management
description:
    - Create keypairs
    - Delete keypairs
    - Get account keypairs info
version_added: "2.3"
author: Chirkov Artem (@chirkov)
options:
  token:
    description:
     - Selectel VPC API token.
  state:
    description:
     - Indicate desired state
    required: true
    default: present
    choices: ['present', 'absent']
  list:
    description:
    - Option for getting list of desired objects (if possible)
    default: false
  user_id:
    description:
    - User ID
  name:
    description:
    - Key name
  keypair:
    description:
    - Keypair object
requirements:
  - python-selvpclient
'''

EXAMPLES = '''
# Create keypair
- selvpc_keypairs:
      keypair:
        name: <key_name>
        public_key: <openssh_public_key>
        regions:
            - ru-1
            - ru-7
        user_id: <user_id>
# Delete keypair
- selvpc_keypairs:
    state: absent
    user_id: <user_id>
    name: <key_name>
# Get info about all keypairs
- selvpc_keypairs:
    list: True
'''


def _system_state_change(module, client):
    state = module.params.get('state')
    user_id = module.params.get('user_id')
    name = module.params.get('name')
    kp_exists = k.keypair_exists(client, user_id, name)
    if state == 'absent':
        if user_id and name:
            return kp_exists
    if state == 'present':
        return not kp_exists
    return False


def main():
    module = AnsibleModule(argument_spec=dict(
        state=dict(choices=['present', 'absent'], default='present'),
        token=dict(type='str', no_log=True),
        name=dict(type='str'),
        user_id=dict(type='str'),
        list=dict(type='bool', default=False),
        keypair=dict(type='dict'),
    ), supports_check_mode=True)

    if module.params['token']:
        token = module.params['token']
    else:
        token = os.environ.get('SEL_TOKEN')
    url = os.environ.get('SEL_URL')

    # Configure REST client
    try:
        http_client = setup_http_client(url,
                                        api_token=token,
                                        custom_headers=custom_user_agent)
        client = Client(http_client)
    except Exception:
        module.fail_json(msg="No token given")

    if module.check_mode:
        module.exit_json(changed=_system_state_change(module, client))

    state = module.params.get('state')
    name = module.params.get('name')
    user_id = module.params.get('user_id')
    show_list = module.params.get('list')
    keypair = module.params.get('keypair')

    if state == 'absent':
        k.delete_keypair(module, client, user_id, name)
    if state == 'present':
        if keypair and not show_list:
            k.create_keypair(module, client, keypair)
        if show_list:
            k.get_keypairs(module, client)
    msg = "Required params are missing or invalid for " \
          "'selvpc_keypairs' operations."
    module.fail_json(msg=msg)


if __name__ == '__main__':
    main()
