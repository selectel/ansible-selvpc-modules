# ansible-selvpc-modules

[![Build Status](https://travis-ci.org/selectel/ansible-selvpc-modules.svg?branch=master)](https://travis-ci.org/selectel/ansible-selvpc-modules)

Modules implement VPC project management via VPC Resell API. 'python-selvpcclient' is used to work with the API.
Modules cover all methods of 'python-selvpcclient'.

## Installation: 
```sh
$ virtualenv --no-site-packages env
$ source env/bin/activate

(env)$ pip install ansible-selvpc-modules
``` 
- Before you start be sure that you have **SEL_URL** и **SEL_TOKEN** variables in your environment.  
(You can get API token here: https://my.selectel.ru/profile/apikeys)

## Usage:
- Ad-hoc commands: 
```sh
(env)$ ansible localhost -m <selvpc_*> -a "<key-valueparams>"
```
- Playbooks:
```sh
(env)$ ansible-playbook someplaybook.yaml
```

## Included modules:
- **selvpc_projects**:
  - description:
    - create/delete/update projects
    - get info about project(s)
  - options:
    - token:
      - description: selectel VPC API token
    - state:
      - description: indicates desired state
      - required: true
      - default: present
      - choices: ['present', 'absent']
    - list:
      - description: option for getting list of desired objects (if possible)
      - default: false
    - project_name:
      - description: selectel VPC project name
    - project_id:
      - description: selectel VPC project ID
    - new_name:
      - description: option for project name update
  - note: for operations where 'project_id' is needed you can use 'project_name' instead
  - examples: 
  ```yaml
  # create project if not exists:
  - selvpc_projects:
      project_name: <project name>
  # if exists than get project info
  - selvpc_projects:
      project_name: <existing project name>
  # update project name
  - selvpc_projects:
      project_name: <proejct name>
      new_name: <new proejct name>
  # delete project
  - selvpc_projects:
      state: absent
      project_name: <project name>
  ```
- **selvpc_quotas**:
  - description:
      - set/update project quotas
      - get info about project(s) quotas
  - options:
    - token:
      - description: selectel VPC API token
    - state:
      - description: indicates desired state
      - required: true
      - default: present
      - choices: ['present', 'absent']
    - list:
      - description: option for getting list of desired objects (if possible)
      - default: false
    - project_name:
      - description: selectel VPC project name
    - project_id:
      - description: selectel VPC project ID
    - quotas:
      - description: dict with project quotas
  - note: for operations where 'project_id' is needed you can use 'project_name' instead
  - examples: 
  ```yaml
  # set quotas on project
  - selvpc_quotas:
      project_name: <project name>
      quotas:
          compute_cores:
           - region: ru-1
             zone: ru-1a
             value: 10
          compute_ram:
           - region: ru-1
             zone: ru-1a
             value: 1024
          volume_gigabytes_fast:
           - region: ru-1
             zone: ru-1a
           value: 100
  # get quotas info of specified project
  - selvpc_quotas:
      project_name: <project name>
  # get quotas info of all domain projects
  - selvpc_quotas:
      list: True 
  ```
- **selvpc_limits**:
  - description:
      - get info about domain limits
  - options:
    - token:
      - description: selectel VPC API token
    - state:
      - description: indicates desired state
      - required: true
      - default: present
      - choices: ['present', 'absent']
    - free:
      - description: param for getting info about available resources
      - default: false
  - examples: 
  ```yaml
  # get total amount of resources available to be allocated to projects
  - selvpc_limits:
        state: present
  # get amount of resources available to be allocated to projects
  - selvpc_limits:
        free: True
  ```
- **selvpc_users**:
  - description:
      - add/delete/update users
      - get info about users
  - options:
    - token:
      - description: selectel VPC API token.
    - state:
      - description: indicate desired state
      - required: true
      - default: present
      - choices: ['present', 'absent']
    - project_name:
      - description: selectel VPC project name
    - project_id:
      - description: selectel VPC project ID
    - username:
      - description: name for new user in project
    - password:
      - description: password for new user in project
    - new_username:
      - description: option for username update
    - password:
      - description: option for password update
    - user_id:
      - description: user ID
    - enabled:
      - description: user state
      - default: true
  - note: for operations where 'project_id' is needed you can use 'project_name' instead
  - examples:
```yaml
  # create user
  - selvpc_users:
      username: <username>
      password: <password>
  # delete user
  - selvpc_users:
    user_id: <user ID>
    state: absent
```
- **selvpc_roles**:
  - description:
      - add roles to project
      - delete roles
      - get info about roles
  - options:
    - token:
      - description: selectel VPC API token.
    - state:
      - description: indicate desired state
      - required: true
      - default: present
      - choices: ['present', 'absent']
    - list:
      - description: option for getting list of desired objects (if possible)
      - default: false
    - project_name:
      - description: selectel VPC project name
    - project_id:
      - description: selectel VPC project ID
    - roles:
      - description: array of roles [{'project_id': <project_id>, 'user_id': <user_id>}]
    - user_id:
      - description: user ID
  - examples:
```yaml
# add role to project
- selvpc_roles:
    user_id: <user id>
    project_id: <project id>
# delete role
- selvpc_roles:
    state: absent
    user_id: <user id>
    project_id: <project id>
# add few users at once
- selvpc_roles:
    roles:
      - project_id: <project id>
        user_id: <user id>
      - project_id: <project id>
        user_id: <user id>
```
- **selvpc_subnets**:
  - description:
      - create/delete subnets
      - get info about subnets
  - options:
    - token:
      - description: selectel VPC API token.
    - state:
      - description: indicate desired state
      - required: true
      - default: present
      - choices: ['present', 'absent']
    - list:
      - description: option for getting list of desired objects (if possible)
      - default: false
    - project_name:
      - description: selectel VPC project name
    - project_id:
      - description: selectel VPC project ID
    - subnets:
      - description: array of subnets [{'region': <region>, 'quantity': <quantity>, 'type': <type>, 'prefix_length': <prefix length>}]
    - subnet_id:
      - description: subnet ID
    - force:
      - description: if 'true' allows to delete "ACTIVE" subnet if it's needed
      - default: false
  - examples:
```yaml
# describe state with 2 subnets in ru-1 region and 1 in ru-2
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
# delete all subnets
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
# delete specific subnets
- selvpc_licenses:
    state: absent
    subnet_id: <subnet id>
# get info about all subnets
- selvpc_subnets:
    list: True
# get info about specific subnet
- selvpc_subnets:
    subnet_id: <subnet id>
```
- **selvpc_floatingips**:
  - description:
      - create/delete floating ips
      - get info about floating ips
  - options:
    - token:
      - description: selectel VPC API token.
    - state:
      - description: indicate desired state
      - required: true
      - default: present
      - choices: ['present', 'absent']
    - list:
      - description: option for getting list of desired objects (if possible)
      - default: false
    - project_name:
      - description: selectel VPC project name
    - project_id:
      - description: selectel VPC project ID
    - floatingip:
      - description: specific floating ip "XXX.XXX.XXX.XXX"
    - floatingips:
      - description: array of floating IPs [{'region': <region>, 'quantity': <quantity>}]
    - floatingip_id:
      - description: floating IP ID
    - force:
      - description: if 'true' allows to delete "ACTIVE" floating ips if it's needed
      - default: false
  - examples:
```yaml
# describe state with 2 ips in ru-1 region and 1 in ru-2
- selvpc_floatingips:
      project_id: <project id>
      floatingips:
      - region: ru-1
        quantity: 2
      - region: ru-2
        quantity: 1
# delete all ips
- selvpc_floatingips:
    project_name: <project name>
    floatingips:
    - region: ru-1
      quantity: 0
    - region: ru-2
      quantity: 0
    force: True
# delete specific ip
- selvpc_floatingips:
    state: absent
    floatingip_id: <floating ip id>
# delete floating ip by ip
- selvpc_floatingip:
    state: absent
    floatingip: <floating ip>
# get info about all ips
- selvpc_floatingips:
    list: True
# get info about specific ip
- selvpc_floatingips:
    floatingip_id: <floating ip id>
```
- **selvpc_licenses**:
  - description:
      - create/delete licenses
      - get info about licenses
  - options:
    - token:
      - description: selectel VPC API token.
    - state:
      - description: indicate desired state
      - required: true
      - default: present
      - choices: ['present', 'absent']
    - list:
      - description: option for getting list of desired objects (if possible)
      - default: false
    - project_name:
      - description: selectel VPC project name
    - project_id:
      - description: selectel VPC project ID
    - licenses:
      - description: array of licenses [{'region': <region>, 'quantity': <quantity>, 'type': <type>}]
    - licenses_id:
      - description: licenses ID
    - force:
      - description: if 'true' allows to delete "ACTIVE" licenses if it's needed
      - default: false
  - examples:
```yaml
# describe state with 2 licenses in ru-1 region and 1 in ru-2
- selvpc_licenses:
      project_id: <project id>
      licenses:
      - region: ru-1
        quantity: 2
        type: <license type>
      - region: ru-2
        quantity: 1
        type: <license type>
# delete all licenses
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
# delete specific licenses
- selvpc_licenses:
    state: absent
    license_id: <license id>
# get info about all licenses
- selvpc_licenses:
    list: True
# get info about specific license
- selvpc_licenses:
    license_id: <licenses id>
```
- **selvpc_tokens**:
  - description:
      - add tokens
  - options:
    - token:
      - description: selectel VPC API token.
    - state:
      - description: indicate desired state
      - required: true
      - default: present
      - choices: ['present', 'absent']
    - project_name:
      - description: selectel VPC project name
    - project_id:
      - description: selectel VPC project ID
  - examples:
```yaml
# Create reseller token for project
- selvpc_tokens:
    project_id: <Project ID>
```
- **selvpc_capabilities**:
  - description:
      - get info about possible values
  - options:
    - token:
      - description: selectel VPC API token.
    - state:
      - description: indicate desired state
      - required: true
      - default: present
      - choices: ['present', 'absent']
  - examples:
```yaml
# get info about capabilities
- selvpc_capabilities:
    state: present
```

## Playbook example:  
- https://github.com/selectel/ansible-selvpc-modules/blob/master/examples/example.yaml
- https://github.com/selectel/ansible-selvpc-modules/blob/master/examples/example_vars.yaml


Before running the example make sure that these packages are already installed:
```sh
shade
jmespath
``` 
Also these environment variables have to be in your env:
```sh
OS_PROJECT_DOMAIN_NAME=<YOUR-DOMAIN-NAME>
OS_USER_DOMAIN_NAME=<YOUR-DOMAIN-NAME>
ANSIBLE_HOST_KEY_CHECKING=False
``` 

License
-------

Apache 2.0

