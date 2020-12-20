from ansible.module_utils.selvpc_utils.licenses import \
    parse_licenses_to_add
from ansible.module_utils.selvpc_utils.subnets import \
    parse_subnets_to_add
from ansible.module_utils.selvpc_utils.floatingips import \
    parse_floatingips_to_add
from ansible.module_utils.selvpc_utils.vrrp import \
    parse_vrrp_subnets_to_add


FLOATING_IPS_INPUT = [
    {"region": "ru-1", "quantity": 1},
    {"region": "ru-1", "quantity": 1},
    {"region": "ru-2", "quantity": 3},
    {"region": "ru-1", "quantity": 2},
    {"region": "ru-2", "quantity": 1}
]

FLOATING_IP_VALID_OUTPUT = {
    "ru-1": 4, "ru-2": 4
}

SUBNETS_INPUT = [
    {"region": "ru-1", "quantity": 1, "type": "ipv4", "prefix_length": 29},
    {"region": "ru-1", "quantity": 1, "type": "ipv4", "prefix_length": 29},
    {"region": "ru-2", "quantity": 2, "type": "ipv4", "prefix_length": 29},
    {"region": "ru-1", "quantity": 1, "type": "ipv4", "prefix_length": 25}
]

SUBNETS_VALID_OUTPUT = {
    ("ru-1", "ipv4", 29): 2,
    ("ru-1", "ipv4", 25): 1,
    ("ru-2", "ipv4", 29): 2
}

LICENSES_INPUT = [
    {"region": "ru-1", "type": "license_windows_2012_standard", "quantity": 4},
    {"region": "ru-2", "type": "license_windows_2012_standard", "quantity": 2},
    {"region": "ru-1", "type": "license_windows_2012_standard", "quantity": 1},
    {"region": "ru-2", "type": "license_windows_2012_standard", "quantity": 3}
]

LICENSES_VALID_OUTPUT = {
    ("ru-1", "license_windows_2012_standard"): 5,
    ("ru-2", "license_windows_2012_standard"): 5
}

VRRP_INPUT = [
    {"master_region": "ru-1", "slave_region": "ru-7", "type": "ipv4", "prefix_length": 29, "quantity": 1},
    {"master_region": "ru-7", "slave_region": "ru-2", "type": "ipv4", "prefix_length": 29, "quantity": 2},
    {"master_region": "ru-7", "slave_region": "ru-1", "type": "ipv4", "prefix_length": 29, "quantity": 3},
    {"master_region": "ru-1", "slave_region": "ru-7", "type": "ipv4", "prefix_length": 29, "quantity": 1},
]

VRRP_VALID_OUTPUT = {
    (29, "ipv4", "ru-1", "ru-7"): 2,
    (29, "ipv4", "ru-7", "ru-2"): 2,
    (29, "ipv4", "ru-7", "ru-1"): 3,
}


def test_parse_data_floating_ips():
    assert parse_floatingips_to_add(
        FLOATING_IPS_INPUT) == FLOATING_IP_VALID_OUTPUT


def test_parsed_data_subnets():
    assert parse_subnets_to_add(SUBNETS_INPUT) == SUBNETS_VALID_OUTPUT


def test_parsed_data_licenses():
    assert parse_licenses_to_add(LICENSES_INPUT) == LICENSES_VALID_OUTPUT


def test_parsed_vrrp_subnets():
    assert parse_vrrp_subnets_to_add(VRRP_INPUT) == VRRP_VALID_OUTPUT
