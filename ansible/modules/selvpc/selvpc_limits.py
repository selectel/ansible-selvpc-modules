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

from ansible.module_utils.selvpc_utils.limits import (get_domain_quotas,
                                                      get_free_domain_quotas)
from ansible.modules.selvpc import custom_user_agent
from selvpcclient.client import Client, setup_http_client


DOCUMENTATION = '''
---
module: selvpc_limits
short_description: selvpc module for domain limits info
description:
    - Get info about domain limits
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
  free:
    description:
    - Param for getting info about available resources
    default: false
requirements:
  - python-selvpcclient
'''

EXAMPLES = '''
# Get total amount of resources available to be allocated to projects
- selvpc_limits:
    state: present

# Get amount of resources available to be allocated to projects
- selvpc_limits:
    free: True
'''


def main():
    module = AnsibleModule(argument_spec=dict(
        state=dict(choices=['present', 'absent'], default='present'),
        token=dict(type='str', no_log=True),
        free=dict(type='bool', default=False),
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

    state = module.params.get('state')
    free = module.params.get('free')

    if module.check_mode:
        module.exit_json(changed=False)

    if state == "present":
        if free:
            get_free_domain_quotas(module, client)
        get_domain_quotas(module, client)

    if state == "absent":
        module.fail_json(msg="Wrong state for 'selvpc_limits' operations.")
    module.fail_json(msg="No params for 'selvpc_limits' operations.")


if __name__ == '__main__':
    main()
