import yaml
from k8spin_common import Organization, Tenant, Space


def create_org_object(api, organization_name):
    obj = yaml.safe_load(
        f"""
            apiVersion: k8spin.cloud/v1
            kind: Organization
            metadata:
                name: {organization_name}
            spec:
                resources:
                    cpu: "5"
                    memory: "5G"
        """
    )
    return Organization(api, obj)

def create_tenant_object(api, organization_name, tenant_name):
    obj = yaml.safe_load(
        f"""
            apiVersion: k8spin.cloud/v1
            kind: Tenant
            metadata:
                namespace: org-{organization_name}
                name: {tenant_name}
            spec:
                resources:
                    cpu: "2"
                    memory: "2G"
        """
    )
    return Tenant(api, obj)

def create_space_object(api, organization_name, tenant_name, space_name):
    obj = yaml.safe_load(
        f"""
            apiVersion: k8spin.cloud/v1
            kind: Space
            metadata:
                namespace: org-{organization_name}-tenant-{tenant_name}
                name: {space_name}
            spec:
                resources:
                    cpu: "1"
                    memory: "1G"
                containers:
                    defaults: 
                        resources:
                            cpu: 10m
                            memory: 64Mi
        """
    )
    return Space(api, obj)