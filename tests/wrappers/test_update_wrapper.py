import pytest

from ansible.module_utils.selvpc_utils.wrappers import update_object_wrapper
from tests.mock_objects import get_mocked_module, get_mocked_client
from tests import params


def test_update_project_name():
    client = get_mocked_client()
    module = get_mocked_module()

    @update_object_wrapper
    def function_that_return_project_params(module, client):
        return True, "Project updated"

    output = function_that_return_project_params(module, client)

    assert module.fail_json.called is False
    assert module.exit_json.called is True
    assert module.exit_json.call_count == 1
    assert output is not None
    assert output == params.PROJECT_UPDATED


def test_update_project_name_existed():
    client = get_mocked_client()
    module = get_mocked_module()

    @update_object_wrapper
    def function_that_return_project_params(module, client):
        return False, "Nothing to change"

    output = function_that_return_project_params(module, client)

    assert module.fail_json.called is False
    assert module.exit_json.called is True
    assert module.exit_json.call_count == 1
    assert output is not None
    assert output == params.PROJECT_EXISTS
