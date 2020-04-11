import kopf

from k8spin_common.resources import organization


@kopf.on.create("k8spin.cloud", "v1", "organizations")
@kopf.on.update("k8spin.cloud", "v1", "organizations")
def create_organization(name, **kwargs):
    organization.ensure_organization_resources(organization_name=name)
