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
from ansible.module_utils.selvpc_utils import licenses as lic


DOCUMENTATION = '''
---
module: selvpc_licenses
short_description: selvpc module for licenses management
description:
    - Create licenses
    - Delete licenses
    - Get info about licenses
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
  licenses:
    description:
    - Array of licenses [{'region': <region>, 'quantity': <quantity>,
    'type': <type>}]
  licenses_id:
    description:
    - Licenses ID
  force:
    description:
    - if 'true' allows to delete "ACTIVE" licenses if it's needed
    default: false
requirements:
  - python-selvpcclient
note:
    - For operations where 'project_id' is needed you can use 'project_name'
    instead
'''

EXAMPLES = '''
# Describe state with 2 licenses in ru-1 region and 1 in ru-2
- selvpc_licenses:
      project_id: <project id>
      licenses:
      - region: ru-1
        quantity: 2
        type: <license type>
      - region: ru-2
        quantity: 1
        type: <license type>
# Delete all licenses
- selvpc_licenses:
    project_name: <project name>
    licenses:
    - region: ru-1
      quantity: 0
      type: <license type>
    - region: ru-2
      quantity: 0
      type: <license type>
    force: True
# Delete specific licenses
- selvpc_licenses:
    state: absent
    license_id: <license id>
# Get info about all licenses
- selvpc_licenses:
    list: True
# Get info about specific license
- selvpc_licenses:
    license_id: <licenses id>
'''


def _check_license_exists(client, license_id):
    try:
        client.licenses.show(license_id)
    except Exception:
        return False
    return True


def _system_state_change(module, client):
    state = module.params.get('state')
    if state == 'absent':
        license_id = module.params.get('license_id')
        if license_id:
            return _check_license_exists(client, license_id)
    if state == 'present':
        licenses = module.params.get('licenses')
        project_name = module.params.get('project_name')
        project_id = module.params.get('project_id')
        force = module.params.get('force')
        if not c._check_valid_quantity(licenses):
            return False
        if (project_name or project_id) and licenses:
            if not project_id:
                project = c.get_project_by_name(client, project_name)
                if not project:
                    return False
                project_id = project.id
            parsed_subnets = lic.parse_licenses_to_add(licenses)
            actual_subnets = lic.get_project_licenses_quantity(
                client, project_id)
            to_add, to_del = c.compare_existed_and_needed_objects(
                actual_subnets, parsed_subnets, force)
            return True if to_add or to_del else False
    return False


def main():
    module = AnsibleModule(argument_spec=dict(
        state=dict(choices=['present', 'absent'], default='present'),
        token=dict(type='str', no_log=True),
        list=dict(type='bool', default=False),
        project_name=dict(type='str'),
        project_id=dict(type='str'),
        licenses=dict(type='list'),
        license_id=dict(type='str'),
        detailed=dict(type='bool', default=False),
        force=dict(type='bool', default=False)
    ), supports_check_mode=True)

    project_id = module.params.get('project_id')
    state = module.params.get('state')
    show_list = module.params.get('list')
    licenses = module.params.get('licenses')
    license_id = module.params.get('license_id')
    detailed = module.params.get('detailed')
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

    if state == "absent" and license_id:
        lic.delete_license(module, client, license_id)

    if state == "present":
        if licenses and (project_id or project_name):
            lic.add_licenses(module, client, project_id, project_name,
                             licenses, force)

        if license_id and not show_list or show_list:
            lic.get_licenses(module, client, license_id, detailed,
                             show_list=show_list)
    module.fail_json(msg="No params for 'licenses' operations.")


if __name__ == '__main__':
    main()
