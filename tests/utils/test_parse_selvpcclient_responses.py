from ansible.module_utils.selvpc_utils.licenses import \
    get_project_licenses_quantity
from ansible.module_utils.selvpc_utils.floatingips import \
    get_project_ips_quantity
from ansible.module_utils.selvpc_utils.subnets import \
    get_project_subnets_quantity
from ansible.module_utils.selvpc_utils.vrrp import \
    get_project_vrrp_subnets_quantity

from tests import params
from tests.mock_objects import get_mocked_client


FLOATING_IPS_PARSED_OUTPUT = {
    "ru-1": {"ACTIVE": 2, "DOWN": 1}, "ru-2": {"ACTIVE": 0, "DOWN": 2}
}

SUBNETS_PARSED_OUTPUT = {('ru-1', 'ipv4', 25): {'ACTIVE': 1, 'DOWN': 1},
                         ('ru-1', 'ipv4', 29): {'ACTIVE': 1, 'DOWN': 0},
                         ('ru-2', 'ipv4', 29): {'ACTIVE': 1, 'DOWN': 1}
                         }

LICENSES_PARSED_OUTPUT = {
    ('ru-1', 'license_windows_2012_standard'): {'ACTIVE': 3, 'DOWN': 1},
    ('ru-2', 'license_windows_2012_standard'): {'ACTIVE': 1, 'DOWN': 1}
}

VRRP_PARSED_OUTPUT = {
    (29, 'ipv4', 'ru-1', 'ru-7'): {'ACTIVE': 1, 'DOWN': 1},
    (29, 'ipv4', 'ru-2', 'ru-7'): {'ACTIVE': 1, 'DOWN': 0},
}


def test_parse_existing_floating_ips():
    client = get_mocked_client()
    assert get_project_ips_quantity(
        client, params.PROJECT_ID) == FLOATING_IPS_PARSED_OUTPUT


def test_parse_existing_subnets():
    client = get_mocked_client()
    assert get_project_subnets_quantity(
        client, params.PROJECT_ID) == SUBNETS_PARSED_OUTPUT


def test_parse_existing_licenses():
    client = get_mocked_client()
    assert get_project_licenses_quantity(
        client, params.PROJECT_ID) == LICENSES_PARSED_OUTPUT


def test_parse_existing_vrrp():
    client = get_mocked_client()
    assert get_project_vrrp_subnets_quantity(
        client, params.PROJECT_ID) == VRRP_PARSED_OUTPUT