from mock import Mock, PropertyMock

PROJECT_ID = '1503a33cfa5a466081d4ef3aa661749e'

FLOATING_IPS_LIST = [
    Mock(id='1',
         region='ru-1',
         status='DOWN'),
    Mock(id='2',
         region='ru-2',
         status='DOWN'),
    Mock(id='3',
         region='ru-1',
         status='ACTIVE'),
    Mock(id='4',
         region='ru-1',
         status='ACTIVE'),
    Mock(id='5',
         region='ru-2',
         status='DOWN')
]

SUBNETS_LIST = [
    Mock(cidr='77.214.217.160/29',
         region='ru-1',
         status='ACTIVE'),
    Mock(cidr='78.244.217.160/29',
         region='ru-2',
         status='DOWN'),
    Mock(cidr='67.244.217.160/25',
         region='ru-1',
         status='ACTIVE'),
    Mock(cidr='77.244.217.160/29',
         region='ru-2',
         status='ACTIVE'),
    Mock(cidr='77.244.217.160/25',
         region='ru-1',
         status='DOWN')
]

LICENSES_LIST = [
    Mock(region="ru-1",
         type='license_windows_2012_standard',
         status="ACTIVE"),
    Mock(region="ru-1",
         type='license_windows_2012_standard',
         status="ACTIVE"),
    Mock(region="ru-1",
         type='license_windows_2012_standard',
         status="ACTIVE"),
    Mock(region="ru-1",
         type='license_windows_2012_standard',
         status="DOWN"),
    Mock(region="ru-2",
         type='license_windows_2012_standard',
         status="DOWN"),
    Mock(region="ru-2",
         type='license_windows_2012_standard',
         status="ACTIVE")
]

PROJECT_NAMES = ["Project1", "Project2", "Project3"]

PROJECT_LIST = [
    Mock(id="lk0ddb40acdf41a8b58599a8bbd678f1",
         url="https://11546.selvpc.ru",
         enabled=True
         ),
    Mock(id="jt0ddb40acdf41a8b58599a8bbd678f2",
         url="https://11546.selvpc.ru",
         enabled=True
         ),
    Mock(id="vd0ddb40acdf41a8b58599a8bbd678f4",
         url="https://11546.selvpc.ru",
         enabled=True
         ),
]


def return_floating_list(project_id):
    return FLOATING_IPS_LIST


def return_subnets_list(project_id):
    return SUBNETS_LIST


def return_licenses_list(project_id):
    return LICENSES_LIST


def return_projects_list():
    for project, name in zip(PROJECT_LIST, PROJECT_NAMES):
        name = PropertyMock(return_value=name)
        type(project).name = name
    return PROJECT_LIST


def get_mocked_client():
    client = Mock()
    client.floatingips = Mock()
    client.subnets = Mock()
    client.licenses = Mock()
    client.projects = Mock()
    client.floatingips.list.side_effect = return_floating_list
    client.subnets.list.side_effect = return_subnets_list
    client.licenses.list.side_effect = return_licenses_list
    client.projects.list.side_effect = return_projects_list
    return client

