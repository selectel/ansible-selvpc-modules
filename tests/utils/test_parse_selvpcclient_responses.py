import pytest

from tests.mock_objects import PROJECT_ID, get_mocked_client

from ansible.module_utils.selvpc_utils.licenses import get_project_licenses_quantity
from ansible.module_utils.selvpc_utils.floatingips import get_project_ips_quantity
from ansible.module_utils.selvpc_utils.subnets import get_project_subnets_quantity


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


def test_parse_existing_floating_ips():
    client = get_mocked_client()
    assert get_project_ips_quantity(
        client, PROJECT_ID) == FLOATING_IPS_PARSED_OUTPUT


def test_parse_existing_subnets():
    client = get_mocked_client()
    assert get_project_subnets_quantity(
        client, PROJECT_ID) == SUBNETS_PARSED_OUTPUT


def test_parse_existing_licenses():
    client = get_mocked_client()
    assert get_project_licenses_quantity(
        client, PROJECT_ID) == LICENSES_PARSED_OUTPUT
