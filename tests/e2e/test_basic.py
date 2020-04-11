
from pathlib import Path
import time
import inspect

from slugify import slugify
from pykube import Namespace
import pykube
import pytest

from .utils import create_org_object, create_space_object, create_tenant_object
from k8spin_common.resources.organization import organization_namespacename_generator, get_organization
from k8spin_common.resources.tenant import tenant_namespacename_generator, get_tenant
from k8spin_common.resources.space import space_namespacename_generator, get_space

TIMEOUT = 2
ORG_NAME = "acme"
TENANT_NAME = "looney"
SPACE_NAME = "tunes"


def test_create_org(cluster):
    test_id = "t1"
    org = create_org_object(api=cluster.api, organization_name=test_id+ORG_NAME)
    org.create()
    time.sleep(TIMEOUT)

    namespace = Namespace.objects(cluster.api).get(name=organization_namespacename_generator(organization_name=test_id+ORG_NAME))
    assert namespace.labels["k8spin.cloud/type"] == "organization"
    assert namespace.labels["k8spin.cloud/org"] == test_id+ORG_NAME

def test_create_tenant(cluster):
    test_id = "t2"
    org = create_org_object(api=cluster.api, organization_name=test_id+ORG_NAME)
    org.create()
    time.sleep(TIMEOUT)

    tenant = create_tenant_object(api=cluster.api, organization_name=test_id+ORG_NAME, tenant_name=test_id+TENANT_NAME)
    tenant.create()
    time.sleep(TIMEOUT)

    namespace = Namespace.objects(cluster.api).get(name=tenant_namespacename_generator(organization_name=test_id+ORG_NAME, tenant_name=test_id+TENANT_NAME))
    assert namespace.labels["k8spin.cloud/type"] == "tenant"
    assert namespace.labels["k8spin.cloud/org"] == test_id+ORG_NAME
    assert namespace.labels["k8spin.cloud/tenant"] == test_id+TENANT_NAME

def test_create_spaces(cluster):
    test_id = "t3"
    org = create_org_object(api=cluster.api, organization_name=test_id+ORG_NAME)
    org.create()
    time.sleep(TIMEOUT)

    tenant = create_tenant_object(api=cluster.api, organization_name=test_id+ORG_NAME, tenant_name=test_id+TENANT_NAME)
    tenant.create()
    time.sleep(TIMEOUT)

    space = create_space_object(api=cluster.api, organization_name=test_id+ORG_NAME, tenant_name=test_id+TENANT_NAME, space_name=test_id+SPACE_NAME)
    space.create()
    time.sleep(TIMEOUT)

    namespace = Namespace.objects(cluster.api).get(name=space_namespacename_generator(organization_name=test_id+ORG_NAME, tenant_name=test_id+TENANT_NAME, space_name=test_id+SPACE_NAME))
    assert namespace.labels["k8spin.cloud/type"] == "space"
    assert namespace.labels["k8spin.cloud/org"] == test_id+ORG_NAME
    assert namespace.labels["k8spin.cloud/tenant"] == test_id+TENANT_NAME
    assert namespace.labels["k8spin.cloud/space"] == test_id+SPACE_NAME

    resourceQuotas = pykube.ResourceQuota.objects(cluster.api, namespace.name).filter(selector={
        "k8spin.cloud/type": "quotas"
    })
    assert len(resourceQuotas) == 1

    limitRanges = pykube.LimitRange.objects(cluster.api, namespace.name).filter(selector={
        "k8spin.cloud/type": "defaults"
    })
    assert len(limitRanges) == 1

def test_manage_limits_tenant(cluster):
    test_id = "t4"
    org = create_org_object(api=cluster.api, organization_name=test_id+ORG_NAME)
    org.obj["spec"]["resources"]["cpu"] = "2"
    org.obj["spec"]["resources"]["memory"] = "2G"
    org.create()
    time.sleep(TIMEOUT)

    tenant = create_tenant_object(api=cluster.api, organization_name=test_id+ORG_NAME, tenant_name=test_id+TENANT_NAME)
    tenant.obj["spec"]["resources"]["cpu"] = "3"
    tenant.obj["spec"]["resources"]["memory"] = "2G"
    with pytest.raises(pykube.exceptions.HTTPError, match=".*validating.tenants.k8spin.cloud.*Resources exceeded.*"):
        tenant.create()

    tenant.obj["spec"]["resources"]["cpu"] = "2"
    tenant.obj["spec"]["resources"]["memory"] = "3T"
    with pytest.raises(pykube.exceptions.HTTPError, match=".*validating.tenants.k8spin.cloud.*Resources exceeded.*"):
        tenant.create()

    tenant.obj["spec"]["resources"]["cpu"] = "2000"
    tenant.obj["spec"]["resources"]["memory"] = "3000M"
    with pytest.raises(pykube.exceptions.HTTPError, match=".*validating.tenants.k8spin.cloud.*Resources exceeded.*"):
        tenant.create()

    tenant.obj["spec"]["resources"]["cpu"] = "2000m"
    tenant.obj["spec"]["resources"]["memory"] = "2000M"
    tenant.create()

def test_manage_limits_tenant_modorg(cluster):
    test_id = "t5"
    org = create_org_object(api=cluster.api, organization_name=test_id+ORG_NAME)
    org.obj["spec"]["resources"]["cpu"] = "2"
    org.obj["spec"]["resources"]["memory"] = "2G"
    org.create()
    time.sleep(TIMEOUT)

    tenant = create_tenant_object(api=cluster.api, organization_name=test_id+ORG_NAME, tenant_name=test_id+TENANT_NAME)
    tenant.obj["spec"]["resources"]["cpu"] = "3"
    tenant.obj["spec"]["resources"]["memory"] = "3G"
    with pytest.raises(pykube.exceptions.HTTPError, match=".*validating.tenants.k8spin.cloud.*Resources exceeded.*"):
        tenant.create()

    org = get_organization(organization_name=test_id+ORG_NAME)
    org.obj["spec"]["resources"]["cpu"] = "10"
    org.obj["spec"]["resources"]["memory"] = "10G"
    org.update()
    time.sleep(TIMEOUT)

    tenant.create()

def test_manage_limits_space(cluster):
    test_id = "t6"
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
    space.obj["spec"]["resources"]["cpu"] = "10"
    space.obj["spec"]["resources"]["memory"] = "10G"
    with pytest.raises(pykube.exceptions.HTTPError, match=".*validating.spaces.k8spin.cloud.*Resources exceeded.*"):
        space.create()

    space.obj["spec"]["resources"]["cpu"] = "4"
    space.obj["spec"]["resources"]["memory"] = "4G"
    space.create()

def test_manage_limits_space_modtenant(cluster):
    test_id = "t7"
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
    space.obj["spec"]["resources"]["cpu"] = "10"
    space.obj["spec"]["resources"]["memory"] = "10G"
    with pytest.raises(pykube.exceptions.HTTPError, match=".*validating.spaces.k8spin.cloud.*Resources exceeded.*"):
        space.create()

    tenant = get_tenant(organization_name=test_id+ORG_NAME, tenant_name=test_id+TENANT_NAME)
    tenant.obj["spec"]["resources"]["cpu"] = "10"
    tenant.obj["spec"]["resources"]["memory"] = "10G"
    tenant.update()
    time.sleep(TIMEOUT)

    space.obj["spec"]["resources"]["cpu"] = "10"
    space.obj["spec"]["resources"]["memory"] = "10G"
    space.create()
