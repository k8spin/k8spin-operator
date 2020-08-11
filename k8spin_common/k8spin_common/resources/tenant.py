import pykube

import k8spin_common
from k8spin_common.helper import adopt, ensure, kubernetes_api
from k8spin_common.resources.namespace import create_namespace
from k8spin_common.resources.organization import \
    organization_namespacename_generator
from k8spin_common.resources.rbac import (create_cluster_role_binding,
                                          create_role_binding)

TENANT_NAMESPACE_PREFIX = "tenant-"


def tenant_namespacename_generator(tenant_name, organization_name):
    org_namespace = organization_namespacename_generator(organization_name)
    return f"{org_namespace}-{TENANT_NAMESPACE_PREFIX}{tenant_name}"


def ensure_tenant_resources(organization: k8spin_common.Organization, tenant_name: str):
    ensure_tenant_namespace(
        organization=organization, tenant_name=tenant_name)
    ensure_tenant_role_bindings(
        organization=organization, tenant_name=tenant_name)


@kubernetes_api
def ensure_tenant_namespace(api, organization: k8spin_common.Organization, tenant_name: str):
    tenant_namespace_name = tenant_namespacename_generator(
        organization_name=organization.name, tenant_name=tenant_name)
    labels = {
        "k8spin.cloud/type": "tenant",
        "k8spin.cloud/org": organization.name,
        "k8spin.cloud/tenant": tenant_name
    }
    owner = get_tenant(tenant_name, organization.name)
    tenant_namespace = create_namespace(tenant_namespace_name, labels)
    tenant_namespace = ensure(tenant_namespace, owner)
    return tenant_namespace


@kubernetes_api
def ensure_tenant_role_bindings(api, organization: k8spin_common.Organization, tenant_name: str):
    tenant = get_tenant(tenant_name=tenant_name,
                        organization_name=organization.name)
    namespace = tenant.tenant_namespace
    roles = tenant.roles
    rolebindings_names = list()
    # Tenant level permissions
    for role in roles:
        # Cluster role to assign
        name = role.get('name')
        target_kind = "ServiceAccount"
        targets = role.get('serviceAccounts', None)
        if not targets:
            target_kind = "Group"
            targets = role.get('groups', None)
            if not targets:
                target_kind = "User"
                targets = role.get('users', list())
        for target in targets:
            target_namespace = target.split(":")[0] if target_kind == "ServiceAccount" else None
            target = target.split(":")[1] if target_kind == "ServiceAccount" else target
            rolebinding_name = f"{tenant_name}-{name}-{target_kind.lower()}-{target.lower()}"
            labels = {
                "k8spin.cloud/type": "role",
                "k8spin.cloud/org": organization.name,
                "k8spin.cloud/tenant": tenant_name
            }
            role_binding = create_role_binding(
                rolebinding_name, namespace.name, labels, name, target_kind, target, target_namespace)
            ensure(role_binding, tenant)
            rolebindings_names.append(rolebinding_name)
            # Create required binding to allow user query namespaces
            cluster_rolebinding_name = f"{tenant_name}-{name}-{target_kind.lower()}-{target.lower()}"
            cluster_role_binding = create_cluster_role_binding(
                cluster_rolebinding_name, labels, "namespace-viewer", target_kind, target, target_namespace)
            ensure(cluster_role_binding, tenant)
    # Finally, cleanup
    _clean_tenant_roles(organization, tenant, rolebindings_names)


@kubernetes_api
def _clean_tenant_roles(api, organization: k8spin_common.Organization, tenant: k8spin_common.Tenant, rolebindings_names: list):
    namespace = tenant.tenant_namespace
    tenant_role_bindings = pykube.RoleBinding.objects(api, namespace=namespace.name).filter(
        selector={"k8spin.cloud/type": "role", "k8spin.cloud/org": organization.name, "k8spin.cloud/tenant": tenant.name})
    for tenant_role_binding in tenant_role_bindings:
        if tenant_role_binding.name not in rolebindings_names:
            tenant_role_binding.delete()


@kubernetes_api
def get_tenant_from_namespace(api, tenant_namespace_name: str):
    tenant_namespace = pykube.Namespace.objects(
        api).get(name=tenant_namespace_name)
    org_name = tenant_namespace.labels["k8spin.cloud/org"]
    tenant_name = tenant_namespace.labels["k8spin.cloud/tenant"]
    return get_tenant(tenant_name=tenant_name, organization_name=org_name)


@kubernetes_api
def get_tenant(api, tenant_name: str, organization_name: str):
    organization_namespace_name = organization_namespacename_generator(
        organization_name=organization_name)
    return k8spin_common.Tenant.objects(api, namespace=organization_namespace_name).get(name=tenant_name)
