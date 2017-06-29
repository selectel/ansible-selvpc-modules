from ansible.module_utils.selvpc_utils.wrappers import get_object_wrapper


@get_object_wrapper('quotas')
def get_domain_quotas(module, client):
    return client.quotas.get_domain_quotas()


@get_object_wrapper('quotas')
def get_free_domain_quotas(module, client):
    return client.quotas.get_free_domain_quotas()
