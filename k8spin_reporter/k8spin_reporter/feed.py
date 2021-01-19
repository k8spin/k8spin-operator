import pykube
from k8spin_common import Organization
from k8spin_common.helper import kubernetes_api


@kubernetes_api
def do_feed(api):
    orgs = Organization.objects(api).all()
    for org in orgs:
        print(org)
        tenants = org.tenants
        for tenant in tenants:
            print(tenant)
            spaces = tenant.spaces
            for space in spaces:
                print(space)
                namespace = space.space_namespace
                quota = pykube.ResourceQuota.objects(
                    api, namespace.name).get(name="quotas")
                quota_cpu_hard = quota.obj["status"]["hard"]["requests.cpu"]
                quota_mem_hard = quota.obj["status"]["hard"]["requests.memory"]
                quota_cpu_used = quota.obj["status"]["used"]["requests.cpu"]
                quota_mem_used = quota.obj["status"]["used"]["requests.memory"]
                print(
                    f"Organization: {org.name}. Tenant {tenant.name}. Space {space.name}")
                print(
                    f"CPU: {quota_cpu_used}/{quota_cpu_hard}. Memory: {quota_mem_used}/{quota_mem_hard}")
