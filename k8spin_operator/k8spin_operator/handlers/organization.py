import kopf
from k8spin_common.resources import organization
from pykube.exceptions import ObjectDoesNotExist


@kopf.on.create("k8spin.cloud", "v1", "organizations")
@kopf.on.update("k8spin.cloud", "v1", "organizations")
def create_organization(name, **kwargs):  # pylint: disable=W0613
    organization.ensure_organization_resources(organization_name=name)


@kopf.on.delete("k8spin.cloud", "v1", "organizations")
def delete_organization(name, **kwargs):  # pylint: disable=W0613
    try:
        org = organization.get_organization(name)  # pylint: disable=E1120
        tenants = org.tenants
        for tenant in tenants:
            spaces = tenant.spaces
            for space in spaces:
                space_namespace = space.space_namespace
                space_namespace.delete()
            tenant_namespace = tenant.tenant_namespace
            tenant_namespace.delete()
        organization_namespace = org.organization_namespace
        organization_namespace.delete()
    except ObjectDoesNotExist:
        pass
