from mock import Mock, MagicMock

from tests import params


def get_mocked_client():
    client = Mock()
    client.floatingips = Mock()
    client.subnets = Mock()
    client.licenses = Mock()
    client.projects = Mock()
    client.vrrp = Mock()
    client.floatingips.list = Mock(
        side_effect=lambda project_id: params.FLOATING_IPS_LIST)
    client.subnets.list = Mock(
        side_effect=lambda project_id: params.SUBNETS_LIST)
    client.licenses.list = Mock(
        side_effect=lambda project_id: params.LICENSES_LIST)
    client.projects.list = Mock(
        side_effect=lambda: params.PROJECT_LIST
    )
    client.vrrp.list = Mock(
        side_effect=lambda project_id: params.VRRP_LIST)
    return client


def get_mocked_module():
    mdl = MagicMock()
    mdl.exit_json = MagicMock(side_effect=lambda **kwargs: kwargs)
    mdl.fail_json = MagicMock(side_effect=lambda **kwargs: kwargs)
    return mdl
