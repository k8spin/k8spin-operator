from os import getenv

import kopf
from k8spin_common.resources import organization, space, tenant

RECONCILIATION_INTERVAL = int(getenv("RECONCILIATION_INTERVAL_SECONDS", "10"))


@kopf.timer("k8spin.cloud", "v1", "organizations", interval=RECONCILIATION_INTERVAL, idle=10)
def reconciler(name, **kwargs):  # pylint: disable=W0613
    organization.ensure_organization_resources(organization_name=name)
    # pylint: disable=E1120
    org = organization.get_organization(name)
    org_tenants = org.tenants
    for org_tenant in org_tenants:
        tenant.ensure_tenant_resources(
            organization=org, tenant_name=org_tenant.name)
        tenant_spaces = org_tenant.spaces
        for tenant_space in tenant_spaces:
            space.ensure_space_resources(
                organization=org, tenant=org_tenant, space_name=tenant_space.name)
