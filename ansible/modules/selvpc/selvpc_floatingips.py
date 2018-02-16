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

from ansible.modules.selvpc import custom_user_agent
from selvpcclient.client import Client, setup_http_client

from ansible.module_utils.selvpc_utils import common as c
from ansible.module_utils.selvpc_utils import floatingips as f

DOCUMENTATION = '''
---
module: selvpc_floatingips
short_description: selvpc module for floating ips management
description:
    - Create floating ips
    - Delete floating ips
    - Get info about floating ips
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
  floatingip:
    description:
    - Floating ip "XXX.XXX.XXX.XXX"
  floatingips:
    description:
    - Array of floating IPs [{'region': <region>, 'quantity': <quantity>}]
  floatingip_id:
    description:
    - Floating IP ID
  force:
    description:
    - if 'true' allows to delete "ACTIVE" floating ips if it's needed
    default: false
requirements:
  - python-selvpcclient
note:
    - For operations where 'project_id' is needed you can use 'project_name'
    instead
'''

EXAMPLES = '''
# Describe state with 2 ips in ru-1 region and 1 in ru-2
- selvpc_floatingips:
      project_id: <project id>
      floatingips:
      - region: ru-1
        quantity: 2
      - region: ru-2
        quantity: 1
# Delete all ips
- selvpc_floatingips:
    project_name: <project name>
    floatingips:
    - region: ru-1
      quantity: 0
    - region: ru-2
      quantity: 0
    force: True
# Delete specific ip
- selvpc_floatingips:
    state: absent
    floatingip_id: <floating ip id>
# Delete floating ip by ip
- selvpc_floatingip:
    state: absent
    floatingip: 79.183.144.19
# Get info about all ips
- selvpc_floatingips:
    list: True
# Get info about specific ip
- selvpc_floatingips:
    floatingip_id: <floating ip id>
'''


def _check_floatingip_exists(client, floatingip_id):
    try:
        client.floatingips.show(floatingip_id)
    except Exception:
        return False
    return True


def _system_state_change(module, client):
    state = module.params.get('state')
    if state == 'absent':
        floatingip_id = module.params.get('floatingip_id')
        floatingip = module.params.get('floatingip')
        if floatingip_id:
            return _check_floatingip_exists(client, floatingip_id)
        if floatingip and c._check_valid_ip(floatingip):
            return True \
                if c.get_floatingip_by_ip(client, floatingip) else False
    if state == 'present':
        floatingips = module.params.get('floatingips')
        project_name = module.params.get('project_name')
        project_id = module.params.get('floatingip_id')
        force = module.params.get('force')
        if not c._check_valid_quantity(floatingips):
            return False
        if (project_name or project_id) and floatingips:
            if not project_id:
                project = c.get_project_by_name(client, project_name)
                if not project:
                    return False
                project_id = project.id
            parsed_ips = f.parse_floatingips_to_add(floatingips)
            actual_ips = f.get_project_ips_quantity(client, project_id)
            to_add, to_del = c.compare_existed_and_needed_objects(
                actual_ips, parsed_ips, force)
            return True if to_add or to_del else False
    return False


def main():
    module = AnsibleModule(argument_spec=dict(
        state=dict(choices=['present', 'absent'], default='present'),
        token=dict(type='str', no_log=True),
        list=dict(type='bool', default=False),
        project_id=dict(type='str'),
        floatingips=dict(type='list'),
        floatingip_id=dict(type='str'),
        project_name=dict(type='str'),
        floatingip=dict(type='str'),
        force=dict(type='bool', default=False)
    ), supports_check_mode=True)

    project_id = module.params.get('project_id')
    state = module.params.get('state')
    show_list = module.params.get('list')
    floatingips = module.params.get('floatingips')
    floatingip_id = module.params.get('floatingip_id')
    project_name = module.params.get('project_name')
    floatingip = module.params.get('floatingip')
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

    if state == 'absent' and (floatingip_id or floatingip):
        f.delete_floatingip(module, client, floatingip_id, floatingip)

    if state == 'present':
        if floatingips and (project_id or project_name):
            f.add_floatingips(module, client, project_id,
                              project_name, floatingips, force)

        if floatingip_id and not show_list or show_list:
            f.get_floatingips(module, client, floatingip_id,
                              show_list=show_list)
    module.fail_json(msg="No params for 'floatingips' operations.")


if __name__ == '__main__':
    main()
