import kopf
import pykube

from k8spin_common.helper import kubernetes_api
from k8spin_common.resources import organization, tenant


@kubernetes_api
def lives_in_org_namespace(api, namespace, **_):
    parent_namespace = pykube.Namespace.objects(api).get(name=namespace)
    # pylint: disable=E1120
    if parent_namespace.labels.get("k8spin.cloud/type", "") == "organization" and any(
            [owner.get('kind') == 'Organization'
                for owner in parent_namespace.metadata.get('ownerReferences', list())]):
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
