from ansible.module_utils.selvpc_utils import wrappers


@wrappers.get_object('quotas')
def get_domain_quotas(module, client):
    return client.quotas.get_domain_quotas()


@wrappers.get_object('quotas')
def get_free_domain_quotas(module, client):
    return client.quotas.get_free_domain_quotas()
