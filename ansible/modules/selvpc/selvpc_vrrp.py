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
from ansible.module_utils.selvpc_utils import vrrp as v

DOCUMENTATION = '''
---
module: selvpc_vrrp
short_description: selvpc module for vrrp management
description:
    - Create vrrp
    - Delete vrrp
    - Get info about vrrp
version_added: "0.1"
author: Bokov Ivan
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
  vrrp:
    description:
    - Array of vrrp [{'master_region': <region>, 'slave_region': <region>, 'quantity': <quantity>,
    'type': <type>, 'prefix_length': <prefix length>}]
  vrrp_id:
    description:
    - Vrrp ID
  force:
    description:
    - if 'true' allows to delete "ACTIVE" subnet if it's needed
    default: false
requirements:
  - python-selvpcclient
note:
    - For operations where 'project_id' is needed you can use 'project_name'
    instead
'''

EXAMPLES = '''
# Describe state with 2 vrrp subnet in ru-1 region and 1 in ru-2
- selvpc_vrrp:
      project_id: <project id>
      vrrp:
      - master: ru-1
        slave: ru-2
        quantity: 1
        type: <type>
        prefix_length: <prefix length>
# Delete all subnets
- selvpc_subnets:
    project_name: <project name>
    licenses:
    - region: ru-1
      quantity: 0
      type: <type>
      prefix_length: <prefix length>
    - region: ru-2
      quantity: 0
      type: <type>
      prefix_length: <prefix length>
    force: True
# Delete specific vrrp subnet
- selvpc_licenses:
    state: absent
    subnet_id: <subnet id>
# Get info about all subnets
- selvpc_vrrp:
    list: True
# Get info about specific subnet
- selvpc_vrrp:
    subnet_id: <subnet id>
'''
def _check_vrrp_exists(client, vrrp_id):
    try:
        client.subnets.show(vrrp_id)
    except Exception:
        return False
    return True

def _system_state_change(module, client):
    state = module.params.get('state')
    if state == 'absent':
        vrrp_id = module.params.get('vrrp_id')
        if vrrp_id:
            return _check_vrrp_exists(client, vrrp_id)
    if state == 'present':
        vrrp = module.params.get('vrrp')
        project_name = module.params.get('project_name')
        project_id = module.params.get('project_id')
        force = module.params.get('force')
        if not c._check_valid_quantity(vrrp):
            return False
        if (project_name or project_id) and vrrp:
            if not project_id:
                project = c.get_project_by_name(client, project_name)
                if not project:
                    return False
                project_id = project.id
            parsed_subnets = v.parse_vrrp_to_add(vrrp)
            actual_subnets = v.get_project_vrrp_quantity(client, project_id)
            to_add, to_del = c.compare_existed_and_needed_objects(
                actual_subnets, parsed_subnets, force)
            return True if to_add or to_del else False
    return False

def main():
    module = AnsibleModule(argument_spec=dict(
        state=dict(choices=['present', 'absent'], default='present'),
        token=dict(type='str', no_log=True),
        list=dict(type='bool', default=False),
        project_id=dict(type='str'),
        vrrp=dict(type='list'),
        vrrp_id=dict(type='str'),
        project_name=dict(type='str'),
        force=dict(type='bool', default=False)
    ), supports_check_mode=True)

    project_id = module.params.get('project_id')
    state = module.params.get('state')
    show_list = module.params.get('list')
    vrrp_id = module.params.get('vrrp_id')
    vrrp = module.params.get('vrrp')
    project_name = module.params.get('project_name')
    force = module.params.get('force')

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

    if state == 'absent' and vrrp_id:
        v.delete_vrrp(module, client, vrrp_id)

    if state == 'present':
        if vrrp and (project_id or project_name):
            v.add_vrrp(module, client, project_id, project_name, vrrp)
        if vrrp_id and not show_list or show_list:
            v.get_vrrp(module, client, vrrp_id, show_list=show_list)
    module.fail_json(msg="No params for 'vrrp_subnets' operations.")


if __name__ == '__main__':
    main()
