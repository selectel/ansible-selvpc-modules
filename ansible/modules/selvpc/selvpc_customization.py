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

from selvpcclient.client import setup_http_client, Client
from selvpcclient.exceptions.base import ClientException

from ansible.modules.selvpc import custom_user_agent
from ansible.module_utils.selvpc_utils import wrappers


@wrappers.update_object_wrapper
def update_domain_theme(module, client, logo, color):
    client.customization.update(logo=logo, color=color)
    return True, "Theme updated"


@wrappers.get_object_wrapper('domain')
def show_domain_theme(module, client):
    return client.customization.show()


@wrappers.delete_object_wrapper
def delete_domain_theme(module, client):
    client.customization.delete()


def main():
    module = AnsibleModule(argument_spec=dict(
        state=dict(choices=['present', 'absent'], default='present'),
        token=dict(type='str', no_log=True),
        logo=dict(type='str'),
        color=dict(type='str')
    ), supports_check_mode=True)

    state = module.params.get('state')
    logo = module.params.get('logo')
    color = module.params.get('color')

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
    except ClientException:
        module.fail_json(msg="No token given")

    if state == 'present' and (logo or color):
        update_domain_theme(module, client, logo, color)
    elif state == "present":
        show_domain_theme(module, client)

    if state == 'absent':
        delete_domain_theme(module, client)


from ansible.module_utils.basic import AnsibleModule
if __name__ == '__main__':
    main()
