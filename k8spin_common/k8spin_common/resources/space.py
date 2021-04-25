import k8spin_common
import pykube
from k8spin_common.helper import adopt, ensure, kubernetes_api
from k8spin_common.resources.namespace import create_namespace
from k8spin_common.resources.network_policies import create_network_policy
from k8spin_common.resources.quotas import (create_limit_range,
                                            create_resource_quota)
from k8spin_common.resources.rbac import (create_cluster_role_binding,
                                          create_role_binding)
from k8spin_common.resources.tenant import tenant_namespacename_generator

SPACE_NAMESPACE_PREFIX = "space-"


def space_namespacename_generator(space_name, tenant_name, organization_name):
    tenant_namespace = tenant_namespacename_generator(
        organization_name=organization_name, tenant_name=tenant_name)
    return f"{tenant_namespace}-{SPACE_NAMESPACE_PREFIX}{space_name}"


def ensure_space_resources(organization: k8spin_common.Organization, tenant: k8spin_common.Tenant, space_name: str):
    ensure_space_namespace(organization=organization,
                           tenant=tenant, space_name=space_name)
    ensure_space_role_bindings(organization=organization,
                               tenant=tenant, space_name=space_name)
    ensure_space_resource_quota(
        organization=organization, tenant=tenant, space_name=space_name)
    ensure_space_limit_range(
        organization=organization, tenant=tenant, space_name=space_name)
    ensure_space_network_policies(
        organization=organization, tenant=tenant, space_name=space_name)


@kubernetes_api
def ensure_space_namespace(api, organization: k8spin_common.Organization, tenant: k8spin_common.Tenant, space_name: str):
    space_namespace_name = space_namespacename_generator(
        space_name=space_name, tenant_name=tenant.name, organization_name=organization.name)
    labels = {
        "k8spin.cloud/type": "space",
        "k8spin.cloud/org": organization.name,
        "k8spin.cloud/tenant": tenant.name,
        "k8spin.cloud/space": space_name,
        "k8spin.cloud/name": space_namespace_name
    }
    owner = get_space(space_name, tenant.name, organization.name)
    space_namespace = create_namespace(space_namespace_name, labels)
    space_namespace = ensure(space_namespace, owner)
    return space_namespace


@kubernetes_api
def ensure_space_resource_quota(api, organization: k8spin_common.Organization, tenant: k8spin_common.Tenant, space_name: str):
    space = get_space(space_name, tenant.name, organization.name)
    space_namespace = space.space_namespace
    labels = {
        "k8spin.cloud/type": "quotas",
        "k8spin.cloud/org": organization.name,
        "k8spin.cloud/tenant": tenant.name,
        "k8spin.cloud/space": space_name
    }
    cpu = space.resources.get("cpu")
    memory = space.resources.get("memory")
    space_resource_quota = create_resource_quota(
        "quotas", space_namespace.name, labels, cpu, memory)
    space_resource_quota = ensure(space_resource_quota, space)
    return space_resource_quota


@kubernetes_api
def ensure_space_limit_range(api, organization: k8spin_common.Organization, tenant: k8spin_common.Tenant, space_name: str):
    space = get_space(space_name, tenant.name, organization.name)
    space_namespace = space.space_namespace
    labels = {
        "k8spin.cloud/type": "defaults",
        "k8spin.cloud/org": organization.name,
        "k8spin.cloud/tenant": tenant.name,
        "k8spin.cloud/space": space_name
    }
    cpu = space.default_container_resources.get("cpu")
    memory = space.default_container_resources.get("memory")
    space_limit_range = create_limit_range(
        "defaults", space_namespace.name, labels, cpu, memory)
    space_limit_range = ensure(space_limit_range, space)
    return space_limit_range


@kubernetes_api
def ensure_space_network_policies(api, organization: k8spin_common.Organization, tenant: k8spin_common.Tenant, space_name: str):
    space = get_space(space_name, tenant.name, organization.name)
    space_namespace = space.space_namespace
    labels = {
        "k8spin.cloud/type": "defaults",
        "k8spin.cloud/org": organization.name,
        "k8spin.cloud/tenant": tenant.name,
        "k8spin.cloud/space": space_name
    }
    allow_incoming_network = space.get_allow_incoming_network
    space_network_policy = create_network_policy(
        "defaults", space_namespace.name, labels, allow_incoming_network)
    space_network_policy = ensure(space_network_policy, space)
    return space_network_policy


@kubernetes_api
def ensure_space_role_bindings(api, organization: k8spin_common.Organization, tenant: k8spin_common.Tenant, space_name: str):
    space = get_space(space_name=space_name, tenant_name=tenant.name,
                      organization_name=organization.name)
    namespace = space.space_namespace
    roles = space.roles
    rolebindings_names = list()
    # Space level permissions
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
            target_namespace = target.split(
                ":")[0] if target_kind == "ServiceAccount" else None
            target = target.split(
                ":")[1] if target_kind == "ServiceAccount" else target
            rolebinding_name = f"{space_name}-{name}-{target_kind.lower()}-{target.lower()}"
            labels = {
                "k8spin.cloud/type": "role",
                "k8spin.cloud/org": organization.name,
                "k8spin.cloud/tenant": tenant.name,
                "k8spin.cloud/space": space_name
            }
            role_binding = create_role_binding(
                rolebinding_name, namespace.name, labels, name, target_kind, target, target_namespace)
            ensure(role_binding, space)
            rolebindings_names.append(rolebinding_name)
            # Create required binding to allow user query namespaces
            cluster_rolebinding_name = f"{space_name}-{name}-{target_kind.lower()}-{target.lower()}"
            cluster_role_binding = create_cluster_role_binding(
                cluster_rolebinding_name, labels, "namespace-viewer", target_kind, target, target_namespace)
            ensure(cluster_role_binding, space)
    # Finally, cleanup
    _clean_space_roles(organization, tenant, space, rolebindings_names)


@kubernetes_api
def _clean_space_roles(api, organization: k8spin_common.Organization, tenant: k8spin_common.Tenant, space: k8spin_common.Space, rolebindings_names: list):
    namespace = space.space_namespace
    space_role_bindings = pykube.RoleBinding.objects(api, namespace=namespace.name).filter(
        selector={"k8spin.cloud/type": "role", "k8spin.cloud/org": organization.name, "k8spin.cloud/tenant": tenant.name, "k8spin.cloud/space": space.name})
    for space_role_binding in space_role_bindings:
        if space_role_binding.name not in rolebindings_names:
            space_role_binding.delete()


@kubernetes_api
def get_space_from_namespace(api, space_namespace_name: str):
    space_namespace = pykube.Namespace.objects(
        api).get(name=space_namespace_name)
    org_name = space_namespace.labels["k8spin.cloud/org"]
    tenant_name = space_namespace.labels["k8spin.cloud/tenant"]
    space_name = space_namespace.labels["k8spin.cloud/space"]
    return get_space(space_name=space_name, tenant_name=tenant_name, organization_name=org_name)


@kubernetes_api
def get_space(api, space_name: str, tenant_name: str, organization_name: str):
    tenant_namespace = tenant_namespacename_generator(
        organization_name=organization_name, tenant_name=tenant_name)
    return k8spin_common.Space.objects(api, namespace=tenant_namespace).get(name=space_name)
