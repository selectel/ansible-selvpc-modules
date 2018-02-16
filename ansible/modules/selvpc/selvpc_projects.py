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
from ansible.module_utils.selvpc_utils import projects as p

DOCUMENTATION = '''
---
module: selvpc_projects
short_description: selvpc module for projects management
description:
    - Create/delete/update projects
    - Get info about projects
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
  new_name:
    description:
    - Option for project name update
requirements:
  - python-selvpcclient
note:
    - For operations where 'project_id' is needed you can use 'project_name'
    instead
'''

EXAMPLES = '''
# Create project:
- selvpc_projects:
    project_name: <project name>
# Delete project
- selvpc_projects:
    state: absent
    project_name: <project name>
# Update project name
- selvpc_projects:
    project_name: <project name>
    new_name: <new project name>
'''


def _system_state_change(module, client):
    state = module.params.get('state')
    if state == 'absent':
        project_id = module.params.get('project_id')
        if not project_id:
            project_name = module.params.get('project_name')
            project = c.get_project_by_name(client, project_name)
            if not project:
                return False
            project_id = project.id
        return c._check_project_exists(client, project_id)

    if state == 'present':
        project_id = module.params.get('project_id')
        if not project_id:
            project_name = module.params.get('project_name')
            project = c.get_project_by_name(client, project_name)
            new_name = module.params.get('new_name')
            if new_name and project:
                return True
    return False


def main():
    module = AnsibleModule(argument_spec=dict(
        state=dict(choices=['present', 'absent'], default='present'),
        token=dict(type='str', no_log=True),
        list=dict(type='bool', default=False),
        project_name=dict(type='str'),
        project_id=dict(type='str'),
        new_name=dict(type='str'),
        quotas=dict(type='dict'),
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

    project_name = module.params.get('project_name')
    project_id = module.params.get('project_id')
    state = module.params.get('state')
    show_list = module.params.get('list')
    new_name = module.params.get('new_name')

    if state == 'absent' and (project_id or project_name):
        p.delete_project(module, client, project_id, project_name)

    if state == "present":

        if new_name and (project_id or project_name):
            p.update_project(module, client, project_id, project_name,
                             new_name)

        if project_name and not c.get_project_by_name(client, project_name):
            p.create_project(module, client, project_name)

        if ((project_id or project_name) and not show_list) or show_list:
            p.get_project(module, client, project_id, project_name,
                          show_list=show_list)
    module.fail_json(msg="No params for 'selvpc_projects' operations.")


if __name__ == '__main__':
    main()
