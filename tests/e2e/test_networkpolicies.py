from pathlib import Path
import time
import inspect
import subprocess

from slugify import slugify
from pykube import Namespace
import pykube
import pytest

from .utils import create_org_object, create_space_object, create_tenant_object, create_helloworld_deployment, create_helloworld_service
from k8spin_common.resources.organization import organization_namespacename_generator, get_organization
from k8spin_common.resources.tenant import tenant_namespacename_generator, get_tenant
from k8spin_common.resources.space import space_namespacename_generator, get_space
from k8spin_common import NetworkPolicy

TIMEOUT = 2
ORG_NAME = "acme"
TENANT_NAME = "looney"
SPACE_NAME = "tunes"

def test_create_np(cluster):
    test_id = "np1"
    org = create_org_object(api=cluster.api, organization_name=test_id+ORG_NAME)
    org.obj["spec"]["resources"]["cpu"] = "10"
    org.obj["spec"]["resources"]["memory"] = "10G"
    org.create()
    time.sleep(TIMEOUT)

    tenant = create_tenant_object(api=cluster.api, organization_name=test_id+ORG_NAME, tenant_name=test_id+TENANT_NAME)
    tenant.obj["spec"]["resources"]["cpu"] = "5"
    tenant.obj["spec"]["resources"]["memory"] = "5G"
    tenant.create()
    time.sleep(TIMEOUT)

    space = create_space_object(api=cluster.api, organization_name=test_id+ORG_NAME, tenant_name=test_id+TENANT_NAME, space_name=test_id+SPACE_NAME)
    space.obj["spec"]["resources"]["cpu"] = "1"
    space.obj["spec"]["resources"]["memory"] = "1G"
    space.create()
    time.sleep(TIMEOUT)

    namespace = Namespace.objects(cluster.api).get(name=space_namespacename_generator(organization_name=test_id+ORG_NAME, tenant_name=test_id+TENANT_NAME, space_name=test_id+SPACE_NAME))
    networkPolicies = NetworkPolicy.objects(cluster.api, namespace.name).filter()
    assert len(networkPolicies) == 1

def test_check_np(cluster):
    test_id = "np2"
    org = create_org_object(api=cluster.api, organization_name=test_id+ORG_NAME+"1").create()
    time.sleep(TIMEOUT)

    tenant = create_tenant_object(api=cluster.api, organization_name=test_id+ORG_NAME+"1", tenant_name=test_id+TENANT_NAME+"1").create()
    time.sleep(TIMEOUT)

    space = create_space_object(api=cluster.api, organization_name=test_id+ORG_NAME+"1", tenant_name=test_id+TENANT_NAME+"1", space_name=test_id+SPACE_NAME+"1")
    space.obj["spec"]["allowIncomingNetwork"] = {
        "organizations": [
            {"organization_name": test_id+ORG_NAME+"2"},
        ]
    }
    space.create()
    time.sleep(TIMEOUT)

    deployment = create_helloworld_deployment(api=cluster.api, organization_name=test_id+ORG_NAME+"1", tenant_name=test_id+TENANT_NAME+"1", space_name=test_id+SPACE_NAME+"1", deployment_name="helloworld")
    deployment.create()
    service = create_helloworld_service(api=cluster.api, organization_name=test_id+ORG_NAME+"1", tenant_name=test_id+TENANT_NAME+"1", space_name=test_id+SPACE_NAME+"1", service_name="helloworld")
    service.create()
    time.sleep(TIMEOUT)

    org2 = create_org_object(api=cluster.api, organization_name=test_id+ORG_NAME+"2").create()
    time.sleep(TIMEOUT)

    tenant2 = create_tenant_object(api=cluster.api, organization_name=test_id+ORG_NAME+"2", tenant_name=test_id+TENANT_NAME+"2").create()
    time.sleep(TIMEOUT)

    space2 = create_space_object(api=cluster.api, organization_name=test_id+ORG_NAME+"2", tenant_name=test_id+TENANT_NAME+"2", space_name=test_id+SPACE_NAME+"2").create()
    time.sleep(TIMEOUT)

    deployment2 = create_helloworld_deployment(api=cluster.api, organization_name=test_id+ORG_NAME+"2", tenant_name=test_id+TENANT_NAME+"2", space_name=test_id+SPACE_NAME+"2", deployment_name="helloworld")
    deployment2.create()
    service2 = create_helloworld_service(api=cluster.api, organization_name=test_id+ORG_NAME+"2", tenant_name=test_id+TENANT_NAME+"2", space_name=test_id+SPACE_NAME+"2", service_name="helloworld")
    service2.create()
    time.sleep(TIMEOUT)

    kubectl = cluster.kubectl

    namespace1 = space_namespacename_generator(organization_name=test_id+ORG_NAME+"1", tenant_name=test_id+TENANT_NAME+"1", space_name=test_id+SPACE_NAME+"1")
    namespace2 = space_namespacename_generator(organization_name=test_id+ORG_NAME+"2", tenant_name=test_id+TENANT_NAME+"2", space_name=test_id+SPACE_NAME+"2")

    kubectl("wait", "--for=condition=Available", "deployment", "--timeout=2m", "-n", namespace1 ,"helloworld")
    pod1_list = pykube.Pod.objects(cluster.api).filter(
        namespace=namespace1,
        selector={"app": "helloworld"},
    ).iterator()
    pod1_name = str(next(pod1_list))
    print(pod1_name)

    kubectl("wait", "--for=condition=Available", "deployment", "--timeout=2m", "-n", namespace2 ,"helloworld")
    pod2_list = pykube.Pod.objects(cluster.api).filter(
        namespace=namespace2,
        selector={"app": "helloworld"},
    ).iterator()
    pod2_name = str(next(pod2_list))
    print(pod2_name)

    #Raising error means that network is not enabled
    with pytest.raises(subprocess.CalledProcessError):
        result1 = kubectl("exec", pod1_name, "-n", namespace1, "--",  "curl", "--max-time", "5", f"http://helloworld.{namespace2}.svc")
        print(result1)

    result2 = kubectl("exec", pod2_name, "-n", namespace2, "--", "curl", "--max-time", "5", f"http://helloworld.{namespace1}.svc")
    print(result2)
