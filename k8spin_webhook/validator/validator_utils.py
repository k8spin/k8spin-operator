from typing import List, Tuple

import k8spin_common
from k8spin_common.helper import kubernetes_api
from k8spin_common.resources import quotas
from loguru import logger


def get_namespace_type(resource: object) -> str:
    if "k8spin.cloud/type" in resource["metadata"]["labels"]:
        return resource["metadata"]["labels"]["k8spin.cloud/type"]
    return None


def get_cpu(resource: object) -> float:
    return quotas.cpu_convert_unit(resource["spec"]["resources"]["cpu"])


def get_memory(resource: object) -> float:
    return quotas.memory_convert_unit(resource["spec"]["resources"]["memory"])


def check_tenant_quotas(resource: object) -> Tuple[bool, str]:
    tenant_name = resource["metadata"]["name"]
    organization_name = resource["metadata"]["namespace"].replace("org-", "")

    logger.debug(
        f'Checking tenant quota for tenant {tenant_name} in organization {organization_name}')
    # pylint: disable=E1120
    organization, tenants = get_organization_data(organization_name)
    organization_cpu = get_cpu(organization.obj)
    organization_memory = get_memory(organization.obj)
    logger.debug("Organization found: " + organization_name + " CPU Limit: " +
                 str(organization_cpu) + " Memory Limit: " + str(organization_memory))

    incoming_cpu = get_cpu(resource)
    incoming_memory = get_memory(resource)
    logger.debug("Incoming tenant resources CPU Limit: " +
                 str(incoming_cpu) + " Memory Limit: " + str(incoming_memory))

    total_cpu, total_memory = get_total_resources(
        [tenant for tenant in tenants if tenant.name != tenant_name])
    logger.debug("Total other tenants found for organization " + organization_name +
                 " CPU: " + str(total_cpu) + " Memory: " + str(total_memory))

    if (
        ((incoming_cpu+total_cpu) <= organization_cpu)
        and
        ((incoming_memory+total_memory) <= organization_memory)
    ):
        return True, ""
    return False, "Resources exceeded"


def check_space_quotas(resource: object) -> Tuple[bool, str]:
    space_name = resource["metadata"]["name"]
    organization_name = resource["metadata"]["labels"]["k8spin.cloud/org"]
    tenant_name = resource["metadata"]["labels"]["k8spin.cloud/tenant"]
    logger.debug(
        f'Checking space quota for space {space_name} in tenant {tenant_name}')
    # pylint: disable=E1120
    tenant, spaces = get_tenant_data(
        organization=organization_name, tenant=tenant_name)
    tenant_cpu = get_cpu(tenant.obj)
    tenant_memory = get_memory(tenant.obj)
    logger.debug("Tenant found: " + tenant_name + " CPU Limit: " +
                 str(tenant_cpu) + " Memory Limit: " + str(tenant_memory))

    incoming_cpu = get_cpu(resource)
    incoming_memory = get_memory(resource)
    logger.debug("Incoming space resources CPU Limit: " +
                 str(incoming_cpu) + " Memory Limit: " + str(incoming_memory))

    total_cpu, total_memory = get_total_resources(
        [space for space in spaces if space.name != space_name])
    logger.debug("Total other spaces found for tenant " + tenant_name +
                 " CPU: " + str(total_cpu) + " Memory : " + str(total_memory))

    if (incoming_cpu+total_cpu) <= tenant_cpu and (incoming_memory+total_memory) <= tenant_memory:
        return True, ""
    return False, "Resources exceeded"


def get_total_resources(objects) -> Tuple[float, float]:
    total_cpu = total_mem = 0
    for obj in objects:
        total_cpu += get_cpu(obj.obj)
        total_mem += get_memory(obj.obj)
    return total_cpu, total_mem


@kubernetes_api
def get_organization_data(api, organization: str) -> Tuple[object, List[object]]:
    org = k8spin_common.Organization.objects(api).get(name=organization)
    ten = k8spin_common.Tenant.objects(api, namespace="org-"+organization)
    return org, ten


@kubernetes_api
def get_tenant_data(api, organization: str, tenant: str) -> Tuple[object, List[object]]:
    ten = k8spin_common.Tenant.objects(
        api, namespace="org-"+organization).get(name=tenant)
    spa = k8spin_common.Space.objects(
        api, namespace="org-" + organization + "-tenant-"+tenant)
    return ten, spa
