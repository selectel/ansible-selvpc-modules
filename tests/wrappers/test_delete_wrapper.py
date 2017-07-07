import pytest

from selvpcclient.exceptions.base import ClientException

from ansible.module_utils.selvpc_utils.wrappers import delete_object_wrapper
from tests.mock_objects import get_mocked_module, get_mocked_client
from tests import params


def test_delete_object():
    client = get_mocked_client()
    module = get_mocked_module()

    @delete_object_wrapper
    def function_that_delete_object(module, client):
        pass

    output = function_that_delete_object(module, client)

    assert module.fail_json.called is False
    assert module.exit_json.called is True
    assert module.exit_json.call_count == 1
    assert output is not None
    assert output == params.DELETED


def test_delete_no_object():
    client = get_mocked_client()
    module = get_mocked_module()

    @delete_object_wrapper
    def function_that_delete_object(module, client):
        raise ClientException

    output = function_that_delete_object(module, client)

    assert module.exit_json.called is False
    assert module.fail_json.called is True
    assert module.fail_json.call_count == 1
    assert output is not None
    assert output == params.NOT_DELETED
