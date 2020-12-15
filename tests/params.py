from selvpcclient.base import Resource
from selvpcclient.resources.projects import ProjectsManager
from selvpcclient.resources.floatingips import FloatingIPManager
from selvpcclient.resources.subnets import SubnetManager
from selvpcclient.resources.licenses import LicenseManager
from selvpcclient.resources.vrrp import VRRPManager

ACTUAL_STATE = {
    "changed": False,
    "msg": "Desirable state already in project"
}

DELETED = {
    "changed": True,
    "msg": "Successfully deleted"
}

NOT_DELETED = {
    "msg": "Object doesn't exist"
}

PROJECT_ID = '1503a33cfa5a466081d4ef3aa661749e'

PROJECT_INFO = {
    "id": "1212d243f34f34fqefwfew",
    "project_name": "TestProject",
    "enabled": True
}
PROJECT_OBJECT = Resource(ProjectsManager, PROJECT_INFO)

PROJECT_CREATED_MSG = "Project 'TestProject' has been created"

PROJECT_CREATED = {
    "changed": True,
    "msg": PROJECT_CREATED_MSG,
    "project": PROJECT_INFO
}

PROJECT_UPDATED = {
    "changed": True,
    "msg": "Project updated"
}

PROJECT_EXISTS = {
    "changed": False,
    "msg": "Project with such name already exists"
}

PROJECT_LIST = [
    Resource(ProjectsManager, {
        "project_name": "Project1",
        "id": "lk0ddb40acdf41a8b58599a8bbd678f1",
        "url": "https://11546.selvpc.ru",
        "enabled": True
    }),
    Resource(ProjectsManager, {
        "project_name": "Project2",
        "id": "jt0ddb40acdf41a8b58599a8bbd678f2",
        "url": "https://11546.selvpc.ru",
        "enabled": True
    }),
    Resource(ProjectsManager, {
        "project_name": "Project3",
        "id": "vd0ddb40acdf41a8b58599a8bbd678f4",
        "url": "https://11546.selvpc.ru",
        "enabled": True
    })
]

FLOATING_IP_INFO = {
    "id": "1",
    "region": "ru-1",
    "floating-ip-address": "95.231.78.11",
    "status": "DOWN"
}

FLOATING_IP_INFO_2 = {
    "id": "2",
    "region": "ru-1",
    "floating-ip-address": "95.231.78.12",
    "status": "DOWN"
}

FLOATING_IP_OBJECT = Resource(FloatingIPManager, FLOATING_IP_INFO)
FLOATING_IP_OBJECT_2 = Resource(FloatingIPManager, FLOATING_IP_INFO_2)

FLOATING_IPS_RESP = {
    "added": [
        FLOATING_IP_OBJECT,
        FLOATING_IP_OBJECT_2
    ],
    "deleted": []
}

FLOATING_IP_CREATED_MSG = "Floating ips have been added"

FLOATING_IP_CREATED = {
    "changed": True,
    "floatingips": [FLOATING_IP_INFO, FLOATING_IP_INFO_2],
    "msg": FLOATING_IP_CREATED_MSG,
    "floatingips_deleted": []
}

FLOATING_IPS_LIST = [
    Resource(FloatingIPManager, {
        "id": "1",
        "region": "ru-1",
        "status": "DOWN"
    }),
    Resource(FloatingIPManager, {
        "id": "2",
        "region": "ru-2",
        "status": "DOWN"
    }),
    Resource(FloatingIPManager, {
        "id": "3",
        "region": "ru-1",
        "status": "ACTIVE"
    }),
    Resource(FloatingIPManager, {
        "id": "4",
        "region": "ru-1",
        "status": "ACTIVE"
    }),
    Resource(FloatingIPManager, {
        "id": "5",
        "region": "ru-2",
        "status": "DOWN"
    })
]

SUBNETS_LIST = [
    Resource(SubnetManager, {
        "cidr": "77.214.217.160/29",
        "region": "ru-1",
        "status": "ACTIVE"
    }),
    Resource(SubnetManager, {
        "cidr": "78.244.217.160/29",
        "region": "ru-2",
        "status": "DOWN"
    }),
    Resource(SubnetManager, {
        "cidr": "67.244.217.160/25",
        "region": "ru-1",
        "status": "ACTIVE"
    }),
    Resource(SubnetManager, {
        "cidr": "77.244.217.160/29",
        "region": "ru-2",
        "status": "ACTIVE"
    }),
    Resource(SubnetManager, {
        "cidr": "77.244.217.160/25",
        "region": "ru-1",
        "status": "DOWN"
    })
]

VRRP_LIST = [
    Resource(SubnetManager, {
        "cidr": "77.214.217.160/29",
        "master_region": "ru-1",
        "slave_region": "ru-7",
        "status": "ACTIVE"
    }),
    Resource(SubnetManager, {
        "cidr": "77.214.217.160/29",
        "master_region": "ru-1",
        "slave_region": "ru-7",
        "status": "DOWN"
    }),
    Resource(SubnetManager, {
        "cidr": "77.214.217.160/29",
        "master_region": "ru-2",
        "slave_region": "ru-7",
        "status": "ACTIVE"
    }),
]

LICENSES_LIST = [
    Resource(LicenseManager, {
        "region": "ru-1",
        "type": "license_windows_2012_standard",
        "status": "ACTIVE"
    }),
    Resource(LicenseManager, {
        "region": "ru-1",
        "type": "license_windows_2012_standard",
        "status": "ACTIVE"
    }),
    Resource(LicenseManager, {
        "region": "ru-1",
        "type": "license_windows_2012_standard",
        "status": "ACTIVE"
    }),
    Resource(LicenseManager, {
        "region": "ru-1",
        "type": "license_windows_2012_standard",
        "status": "DOWN"
    }),
    Resource(LicenseManager, {
        "region": "ru-2",
        "type": "license_windows_2012_standard",
        "status": "DOWN"
    }),
    Resource(LicenseManager, {
        "region": "ru-2",
        "type": "license_windows_2012_standard",
        "status": "ACTIVE"
    })
]
