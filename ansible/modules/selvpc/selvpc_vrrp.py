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
    - Create vrrp subnets
    - Delete vrrp subnets
    - Get info about subnets
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
  project_name:
    description:
    - Selectel VPC project name
  project_id:
    description:
    - Selectel VPC project ID
  vrrp_subnets:
    description:
    - Array of vrrp subnets [{'master_region': <master_region>,
                            'slave_region': <slave_region>,
                            'quantity': <quantity>,'type': <type>,
                            'prefix_length': <prefix length>}]
  vrrp_subnet_id:
    description:
    - VRRP Subnet ID
  force:
    description:
    - if 'true' allows to delete "ACTIVE" vrrp subnet if it's needed
    default: false
requirements:
  - python-selvpcclient
note:
    - For operations where 'project_id' is needed you can use 'project_name'
    instead
'''

EXAMPLES = '''
# Create VRRP subnet
- selvpc_vrrp:
      project_id: <project id>
      vrrp_subnets:
      - master_region: ru-1
        slave_region: ru-7
        quantity: 2
        type: ipv4
        prefix_length: 29
# Delete specific vrrp subnet
- selvpc_vrrp:
    state: absent
    vrrp_subnet_id: <vrrp subnet id>
# Get info about all vrrp subnets
- selvpc_vrrp:
    list: True
# Get info about specific vrrp subnet
- selvpc_vrp:
    vrrp_subnet_id: <subnet id>
# Delete all several vrrp subnets
- selvpc_vrrp:
    project_id: <project id>
    vrrp_subnets:
    - master_region: ru-1
      slave_region: ru-7
      quantity: 0
      type: ipv4
      prefix_length: 29
      force: True
'''


def _check_vrrp_subnet_exists(client, vrrp_subnet_id):
    try:
        client.vrrp.show(vrrp_subnet_id)
    except Exception:
        return False
    return True


def _system_state_change(module, client):
    state = module.params.get('state')
    if state == 'absent':
        vrrp_subnet_id = module.params.get('vrrp_subnet_id')
        if vrrp_subnet_id:
            return _check_vrrp_subnet_exists(client, vrrp_subnet_id)
    if state == 'present':
        vrrp_subnets = module.params.get('vrrp_subnets')
        project_name = module.params.get('project_name')
        project_id = module.params.get('project_id')
        force = module.params.get('force')
        if not c._check_valid_quantity(vrrp_subnets):
            return False
        if (project_name or project_id) and vrrp_subnets:
            if not project_id:
                project = c.get_project_by_name(client, project_name)
                if not project:
                    return False
                project_id = project.id
            parsed_subnets = v.parse_vrrp_subnets_to_add(vrrp_subnets)
            actual_subnets = v.get_project_vrrp_subnets_quantity(client,
                                                                 project_id)
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
        project_name=dict(type='str'),
        vrrp_subnets=dict(type='list'),
        vrrp_subnet_id=dict(type='str'),
        force=dict(type='bool', default=False),
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
    project_id = module.params.get('project_id')
    project_name = module.params.get('project_name')
    vrrp_subnets = module.params.get('vrrp_subnets')
    vrrp_subnet_id = module.params.get('vrrp_subnet_id')
    show_list = module.params.get('list')
    force = module.params.get('force')

    if state == 'absent' and vrrp_subnet_id:
        v.delete_vrrp_subnet(module, client, vrrp_subnet_id)

    if state == "present":
        if state == 'present':
            if vrrp_subnets and (project_id or project_name):
                v.add_vrrp_subnets(module, client, project_id, project_name,
                                   vrrp_subnets, force)
            if vrrp_subnet_id and not show_list or show_list:
                v.get_vrrp_subnets(module, client, vrrp_subnet_id,
                                   show_list=show_list)
    module.fail_json(msg="No params for 'selvpc_vrrp' operations.")


if __name__ == '__main__':
    main()
