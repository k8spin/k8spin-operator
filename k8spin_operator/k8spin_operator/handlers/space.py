import kopf
import pykube

from k8spin_common.helper import kubernetes_api
from k8spin_common.resources import space, tenant


@kubernetes_api
def lives_in_tenant_namespace(api, namespace, **_):
    parent_namespace = pykube.Namespace.objects(api).get(name=namespace)
    # pylint: disable=E1120
    if parent_namespace.labels.get("k8spin.cloud/type", "") == "tenant" and any(
            [owner.get('kind') == 'Tenant'
             for owner in parent_namespace.metadata.get('ownerReferences', list())]):
        return True
    return False


@kopf.on.create("k8spin.cloud", "v1", "spaces", when=lives_in_tenant_namespace)
@kopf.on.update("k8spin.cloud", "v1", "spaces", when=lives_in_tenant_namespace)
def create_space(name, namespace, **kwargs):  # pylint: disable=W0613
    # pylint: disable=E1120
    parent_tenant = tenant.get_tenant_from_namespace(
        tenant_namespace_name=namespace)
    parent_organization = parent_tenant.org
    space.ensure_space_resources(
        organization=parent_organization, tenant=parent_tenant, space_name=name)
