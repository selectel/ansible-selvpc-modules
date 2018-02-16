from ansible.module_utils.selvpc_utils import common as c

HAVE_IPS_STATE = {
    "ru-1": {"DOWN": 2, "ACTIVE": 3},
    "ru-2": {"DOWN": 3, "ACTIVE": 0}
}

NEED_IPS_IMPOSSIBLE_STATE_WITHOUT_FORCE = {
    "ru-1": 2, "ru-2": 5
}

OUTPUT_IMPOSSIBLE_TASK = ({}, {})

OUTPUT_IMPOSSIBLE_WITH_FORCE = ({"ru-2": 2}, {"ru-1": 3})


def test_floating_ips_compare_data():
    to_add, to_delete = \
        c.compare_existed_and_needed_objects(
            HAVE_IPS_STATE,
            NEED_IPS_IMPOSSIBLE_STATE_WITHOUT_FORCE,
            force=False)
    assert (to_add, to_delete) == OUTPUT_IMPOSSIBLE_TASK


def test_floating_ips_compare_data_force():
    to_add, to_delete = \
        c.compare_existed_and_needed_objects(
            HAVE_IPS_STATE,
            NEED_IPS_IMPOSSIBLE_STATE_WITHOUT_FORCE,
            force=True)
    assert (to_add, to_delete) == OUTPUT_IMPOSSIBLE_WITH_FORCE
