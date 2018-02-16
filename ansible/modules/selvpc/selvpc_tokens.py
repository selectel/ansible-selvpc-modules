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
from ansible.module_utils.selvpc_utils.common import (_check_project_exists,
                                                      get_project_by_name)
from ansible.modules.selvpc import custom_user_agent
from selvpcclient.client import Client, setup_http_client
from selvpcclient.exceptions.base import ClientException


DOCUMENTATION = '''
---
module: selvpc_tokens
short_description: selvpc module for tokens management
description:
    - Add tokens
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
requirements:
  - python-selvpcclient
note:
  - For operations where 'project_id' is needed you can use 'project_name'
  instead
'''

EXAMPLES = '''
# Create reseller token for project
- selvpc_tokens:
    project_id: <Project ID>
'''


def _system_state_change(module, client):
    state = module.params.get('state')
    if state == 'present':
        project_id = module.params.get('project_id')
        if not project_id:
            project_name = module.params.get('project_name')
            project = get_project_by_name(client, project_name)
            if not project:
                return False
        return _check_project_exists(client, project_id)
    return False


def main():
    module = AnsibleModule(argument_spec=dict(
        state=dict(choices=['present', 'absent'], default='present'),
        token=dict(type='str', no_log=True),
        project_id=dict(type='str'),
        project_name=dict(type='str')
    ), supports_check_mode=True)

    project_id = module.params.get('project_id')
    state = module.params.get('state')
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

    if state == 'present' and (project_id or project_name):
        try:
            if not project_id:
                project = get_project_by_name(client, project_name)
                if not project:
                    raise ClientException(message="No such project")
                project_id = project.id
            client.tokens.create(project_id)
        except ClientException as exp:
            module.fail_json(msg=str(exp))
        module.exit_json(changed=True, result="Token has been created")
    elif state == 'absent' and project_id:
        module.fail_json(msg="Wrong 'state' for 'tokens' operations.")
    module.fail_json(msg="No params for 'tokens' operations.")


if __name__ == '__main__':
    main()
