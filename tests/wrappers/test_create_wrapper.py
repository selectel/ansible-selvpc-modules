import pytest

from ansible.module_utils.selvpc_utils.wrappers import create_object_wrapper
from tests.mock_objects import get_mocked_module, get_mocked_client
from tests import params


def test_create_project():
    client = get_mocked_client()
    module = get_mocked_module()

    @create_object_wrapper('project')
    def function_that_return_project_params(module, client):
        return params.PROJECT_OBJECT, True, params.PROJECT_CREATED_MSG

    output = function_that_return_project_params(module, client)

    assert module.fail_json.called is False
    assert module.exit_json.called is True
    assert module.exit_json.call_count == 1
    assert output is not None
    assert output == params.PROJECT_CREATED


def test_create_floatinips():
    client = get_mocked_client()
    module = get_mocked_module()

    @create_object_wrapper('floatingip')
    def function_that_return_fips_params(module, client):
        return params.FLOATING_IPS_RESP, True, params.FLOATING_IP_CREATED_MSG

    output = function_that_return_fips_params(module, client)

    assert module.fail_json.called is False
    assert module.exit_json.called is True
    assert module.exit_json.call_count == 1
    assert output is not None
    assert output == params.FLOATING_IP_CREATED


def test_create_floatingips_state_is_actual():
    client = get_mocked_client()
    module = get_mocked_module()

    @create_object_wrapper('floatingip')
    def function_that_return_fips_params(module, client):
        return [], False, "Desirable state already in project"

    output = function_that_return_fips_params(module, client)

    assert module.fail_json.called is False
    assert module.exit_json.called is True
    assert module.exit_json.call_count == 1
    assert output is not None
    assert output == params.ACTUAL_STATE
