import kopf
import pykube
from k8spin_common.helper import kubernetes_api
from k8spin_common.resources import organization, tenant
from pykube.exceptions import ObjectDoesNotExist


@kubernetes_api
def lives_in_org_namespace(api, namespace, **_):
    parent_namespace = pykube.Namespace.objects(api).get(name=namespace)
    # pylint: disable=E1120
    if parent_namespace.labels.get("k8spin.cloud/type", "") == "organization":
        return True
    return False


@kopf.on.create("k8spin.cloud", "v1", "tenants", when=lives_in_org_namespace)
@kopf.on.update("k8spin.cloud", "v1", "tenants", when=lives_in_org_namespace)
def create_tenant(name, meta, **kwargs):  # pylint: disable=W0613
    # pylint: disable=E1120
    parent_organization = organization.get_organization(
        organization_name=meta.labels.get("k8spin.cloud/org", None))
    tenant.ensure_tenant_resources(
        organization=parent_organization, tenant_name=name)


@kopf.on.delete("k8spin.cloud", "v1", "tenants")
def delete_tenant(name, meta, **kwargs):  # pylint: disable=W0613
    try:
        # pylint: disable=E1120
        org_tenant = tenant.get_tenant(
            name, meta.labels.get("k8spin.cloud/org", None))
        spaces = org_tenant.spaces
        for space in spaces:
            space_namespace = space.space_namespace
            space_namespace.delete()
        tenant_namespace = org_tenant.tenant_namespace
        tenant_namespace.delete()
    except ObjectDoesNotExist:
        pass
