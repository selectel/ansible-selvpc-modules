from ansible.module_utils.selvpc_utils.wrappers import get_object
from tests import params
from tests.mock_objects import get_mocked_module, get_mocked_client


def test_get_project_list():
    client = get_mocked_client()
    module = get_mocked_module()

    @get_object('project')
    def function_that_return_project_params(module, client):
        return params.PROJECT_LIST

    output = function_that_return_project_params(module, client)

    assert module.fail_json.called is False
    assert module.exit_json.called is True
    assert module.exit_json.call_count == 1
    assert output is not None
    assert len(output["projects"]) == len(params.PROJECT_LIST)


def test_get_floatingips_list():
    client = get_mocked_client()
    module = get_mocked_module()

    @get_object('floatingip')
    def function_that_return_fips_params(module, client):
        return params.FLOATING_IPS_LIST

    output = function_that_return_fips_params(module, client)

    assert module.fail_json.called is False
    assert module.exit_json.called is True
    assert module.exit_json.call_count == 1
    assert output is not None
    assert len(output["floatingips"]) == len(params.FLOATING_IPS_LIST)


def test_get_subnets_list():
    client = get_mocked_client()
    module = get_mocked_module()

    @get_object('subnet')
    def function_that_return_subnets_params(module, client):
        return params.SUBNETS_LIST

    output = function_that_return_subnets_params(module, client)

    assert module.fail_json.called is False
    assert module.exit_json.called is True
    assert module.exit_json.call_count == 1
    assert output is not None
    assert len(output["subnets"]) == len(params.SUBNETS_LIST)


def test_get_licenses_list():
    client = get_mocked_client()
    module = get_mocked_module()

    @get_object('license')
    def function_that_return_license_params(module, client):
        return params.LICENSES_LIST

    output = function_that_return_license_params(module, client)

    assert module.fail_json.called is False
    assert module.exit_json.called is True
    assert module.exit_json.call_count == 1
    assert output is not None
    assert len(output["licenses"]) == len(params.LICENSES_LIST)
