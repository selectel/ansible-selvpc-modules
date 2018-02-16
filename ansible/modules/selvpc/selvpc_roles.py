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

from ansible.modules.selvpc import custom_user_agent
from ansible.module_utils.selvpc_utils import common as c
from ansible.module_utils.selvpc_utils import roles as r


DOCUMENTATION = '''
---
module: selvpc_roles
short_description: selvpc module for roles management
description:
    - Add roles to project
    - Delete roles
    - Get info about roles
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
  list:
    description:
    - Option for getting list of desired objects (if possible)
    default: false
  project_name:
    description:
    - Selectel VPC project name
  project_id:
    description:
    - Selectel VPC project ID
  roles:
    description:
    - Array of roles [{'project_id': <project_id>, 'user_id': <user_id>}]
  user_id:
    description:
    - User ID
requirements:
  - python-selvpcclient
'''

EXAMPLES = '''
# Add role to project
- selvpc_roles:
    user_id: <user id>
    project_id: <project id>
# Delete role
- selvpc_roles:
    state: absent
    user_id: <user id>
    project_id: <project id>
# Add few users at once
- selvpc_roles:
    roles:
      - project_id: <project id>
        user_id: <user id>
      - project_id: <project id>
        user_id: <user id>
'''


def _system_state_change(module, client):
    state = module.params.get('state')
    project_id = module.params.get('project_id')
    user_id = module.params.get('user_id')
    roles = module.params.get('roles')
    project_name = module.params.get('project_name')
    if state == 'absent':
        if not project_id:
            project = c.get_project_by_name(client, project_name)
            if not project:
                return False
            project_id = project.id
        return c._check_user_role(client, project_id, user_id)
    if state == 'present':
        if (project_id or project_name) and user_id:
            if not project_id:
                project = c.get_project_by_name(client, project_name)
                if not project:
                    return False
                project_id = project.id
            return False if c._check_user_role(
                client, project_id, user_id) else True
        if c._check_project_roles(client, roles):
            return True
    return False


def main():
    module = AnsibleModule(argument_spec=dict(
        state=dict(choices=['present', 'absent'], default='present'),
        token=dict(type='str', no_log=True),
        project_id=dict(type='str'),
        user_id=dict(type='str'),
        roles=dict(type='list'),
        project_name=dict(type='str')
    ), supports_check_mode=True)

    project_id = module.params.get('project_id')
    state = module.params.get('state')
    user_id = module.params.get('user_id')
    roles = module.params.get('roles')
    project_name = module.params.get('project_name')

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

    if state == 'absent' and (project_id or project_name) and user_id:
        r.delete_role(module, client, project_id, project_name, user_id)

    if state == 'present':
        if user_id and (project_id or project_name):
            r.add_role(module, client, project_id, project_name, user_id)

        if roles:
            r.add_bulk_roles(module, client, roles)

        if user_id:
            r.get_user_roles(module, client, user_id)

        if project_id or project_name:
            r.get_project_roles(module, client, project_id, project_name)
    module.fail_json(msg="No params for 'roles' operations.")


if __name__ == '__main__':
    main()
