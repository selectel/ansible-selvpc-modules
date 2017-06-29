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

DOCUMENTATION = '''
---
module: selvpc_subnets
short_description: selvpc module for subnets management
description:
    - Create subnets
    - Delete subnets
    - Get info about subnets
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
  subnets:
    description:
    - Array of subnets [{'region': <region>, 'quantity': <quantity>, 'type': <type>, 'prefix_length': <prefix length>}]
  subnet_id:
    description:
    - Subnet ID
  force:
    description:
    - if 'true' allows to delete "ACTIVE" subnet if it's needed
    default: false
requirements:
  - python-selvpcclient
note:
    - For operations where 'project_id' is needed you can use 'project_name' instead
'''

EXAMPLES = '''
# Describe state with 2 subnets in ru-1 region and 1 in ru-2
- selvpc_subnets:
      project_id: <project id>
      subnets:
      - region: ru-1
        quantity: 2
        type: <type>
        prefix_length: <prefix length>
      - region: ru-2
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
# Delete specific subnets
- selvpc_licenses:
    state: absent
    subnet_id: <subnet id>
# Get info about all subnets
- selvpc_subnets:
    list: True
# Get info about specific subnet
- selvpc_subnets:
    subnet_id: <subnet id>
'''

import os

from selvpcclient.client import setup_http_client, Client

from ansible.module_utils.selvpc_utils.subnets import (delete_subnet,
                                                       add_subnets,
                                                       get_subnets,
                                                       get_project_subnets_quantity,
                                                       parse_subnets_to_add)
from ansible.module_utils.selvpc_utils.common import (get_project_by_name,
                                                      compare_existed_and_needed_objects,
                                                      _check_valid_quantity)


def _check_subnet_exists(client, subnet_id):
    try:
        client.subnets.show(subnet_id)
    except Exception:
        return False
    return True


def _system_state_change(module, client):
    state = module.params.get('state')
    if state == 'absent':
        subnet_id = module.params.get('subnet_id')
        if subnet_id:
            return _check_subnet_exists(client, subnet_id)
    if state == 'present':
        subnets = module.params.get('subnets')
        project_name = module.params.get('project_name')
        project_id = module.params.get('project_id')
        force = module.params.get('force')
        if not _check_valid_quantity(subnets):
            return False
        if (project_name or project_id) and subnets:
            if not project_id:
                project = get_project_by_name(client, project_name)
                if not project:
                    return False
                project_id = project.id
            parsed_subnets = parse_subnets_to_add(subnets)
            actual_subnets = get_project_subnets_quantity(client, project_id)
            to_add, to_del = compare_existed_and_needed_objects(
                actual_subnets, parsed_subnets, force)
            return True if to_add or to_del else False
    return False


def main():
    module = AnsibleModule(argument_spec=dict(
        state=dict(choices=['present', 'absent'], default='present'),
        token=dict(type='str', no_log=True),
        list=dict(type='bool', default=False),
        project_id=dict(type='str'),
        subnets=dict(type='list'),
        subnet_id=dict(type='str'),
        project_name=dict(type='str'),
        force=dict(type='bool', default=False)
    ), supports_check_mode=True)

    project_id = module.params.get('project_id')
    state = module.params.get('state')
    show_list = module.params.get('list')
    subnet_id = module.params.get('subnet_id')
    subnets = module.params.get('subnets')
    project_name = module.params.get('project_name')
    force = module.params.get('force')

    if module.params['token']:
        token = module.params['token']
    else:
        token = os.environ.get('SEL_TOKEN')
    url = os.environ.get('SEL_URL')

    # Configure REST client
    try:
        http_client = setup_http_client(url, api_token=token)
        client = Client(http_client)
    except Exception as exp:
        module.fail_json(msg="No token given")

    if module.check_mode:
        module.exit_json(changed=_system_state_change(module, client))

    if state == 'absent' and subnet_id:
        delete_subnet(module, client, subnet_id)

    if state == 'present':
        if subnets and (project_id or project_name):
            add_subnets(module, client, project_id, project_name, subnets,
                        force)
        if subnet_id and not show_list or show_list:
            get_subnets(module, client, subnet_id, show_list=show_list)
    module.fail_json(msg="No params for 'subnets' operations.")


from ansible.module_utils.basic import AnsibleModule
if __name__ == '__main__':
    main()
