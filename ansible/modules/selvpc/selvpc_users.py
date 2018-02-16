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
from ansible.module_utils.selvpc_utils.common import (_check_user_exists,
                                                      get_user_by_name)
from ansible.module_utils.selvpc_utils.users import (create_user, delete_user,
                                                     get_users, update_user)
from ansible.modules.selvpc import custom_user_agent
from selvpcclient.client import Client, setup_http_client

DOCUMENTATION = '''
---
module: selvpc_users
short_description: selvpc module for users management
description:
    - Add users
    - Delete users
    - Update username/password
    - Get info about users
version_added: "2.3"
author: Rutskiy Daniil (@rutskiy)
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
  project_name:
    description:
    - Selectel VPC project name
  project_id:
    description:
    - Selectel VPC project ID
  username:
    description:
    - Name for new user in project
  password:
    description:
    - Password for new user in project
  new_username:
    description:
    - Option for username update
  password:
    description:
    - Option for password update
  user_id:
    description:
    - User ID
  enabled:
    description:
    - User state
    default: True
requirements:
  - python-selvpcclient
note:
  - For operations where 'project_id' is needed you can use 'project_name'
  instead
'''

EXAMPLES = '''
# Create user
- selvpc_users:
    username: <username>
    password: <password>
'''


def _system_state_change(module, client):
    state = module.params.get('state')
    if state == 'absent':
        user_id = module.params.get('user_id')
        return _check_user_exists(client, user_id)
    if state == 'present':
        username = module.params.get('username')
        password = module.params.get('password')
        new_username = module.params.get('new_username')
        new_password = module.params.get('new_password')
        user_id = module.params.get('user_id')
        if username and password:
            user = get_user_by_name(client, username)
            if not user:
                return True
        if user_id and (new_username or new_password) or \
                (new_username and new_password):
            return True
    return False


def main():
    module = AnsibleModule(argument_spec=dict(
        state=dict(choices=['present', 'absent'], default='present'),
        token=dict(type='str', no_log=True),
        username=dict(type='str'),
        password=dict(type='str', no_log=True),
        new_username=dict(type='str'),
        new_password=dict(type='str', no_log=True),
        user_id=dict(type='str'),
        enabled=dict(type='bool', default=True)
    ), supports_check_mode=True)

    state = module.params.get('state')
    username = module.params.get('username')
    password = module.params.get('password')
    new_username = module.params.get('new_username')
    new_password = module.params.get('new_password')
    user_id = module.params.get('user_id')
    enabled = module.params.get('enabled')

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

    if state == 'absent' and user_id:
        delete_user(module, client, user_id)

    if state == 'present':
        if username and password:
            create_user(module, client, username, password, enabled)

        if user_id and (new_username or new_password) or (new_username and
                                                          new_password):
            update_user(module, client, user_id,
                        new_username, new_password, enabled)
        get_users(module, client)
    module.fail_json(msg="No params for 'users' operations.")


if __name__ == '__main__':
    main()
