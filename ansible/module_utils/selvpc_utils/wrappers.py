from functools import wraps

from selvpcclient.exceptions.base import ClientException

from ansible.module_utils.selvpc_utils.common import make_plural


def create_object(object_type):
    """
    Covers functions that deal with object creating, catches exceptions
    and parse results. Also adds "object_type" as json key with results.
    """

    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            params = {}
            try:
                result, changed, msg = func(*args, **kwargs)
            except ClientException as exp:
                return args[0].fail_json(msg=str(exp))
            else:
                params.update({"changed": changed, "msg": msg})
                if result:
                    if isinstance(result, dict):
                        if "added" in result:
                            params.update(
                                {
                                    make_plural(object_type):
                                        [el._info for el in result["added"]]
                                }
                            )
                        if "deleted" in result:
                            params.update(
                                {
                                    make_plural(object_type) + "_deleted":
                                        result["deleted"]
                                }
                            )
                    elif isinstance(result, list):
                        params.update(
                            {
                                make_plural(object_type):
                                    [el._info for el in result]
                            }
                        )
                    else:
                        params.update({object_type: result._info})
            return args[0].exit_json(**params)

        return inner

    return decorator


def get_object(object_type):
    """
    Covers functions that getting objects info, catches exceptions
    and parse results
    """

    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            params = {}
            try:
                result = func(*args, **kwargs)
            except ClientException as exp:
                return args[0].fail_json(msg=str(exp))
            else:
                if isinstance(result, list):
                    params.update(
                        {
                            make_plural(object_type):
                                [el._info for el in result]
                        }
                    )
                else:
                    params.update({object_type: result._info})
            return args[0].exit_json(**params)

        return inner

    return decorator


def delete_object(func):
    """
    Covers functions that delete objects, catches exceptions
    and parse results
    """

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except ClientException:
            return args[0].fail_json(msg="Object doesn't exist")
        else:
            return args[0].exit_json(changed=True, msg="Successfully deleted")

    return inner


def update_object(func):
    """
    Covers functions that update objects, catches exceptions
    and parse results
    """

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            changed, msg = func(*args, **kwargs)
        except ClientException as exp:
            return args[0].fail_json(msg=str(exp))
        else:
            return args[0].exit_json(changed=changed, msg=msg)

    return inner
