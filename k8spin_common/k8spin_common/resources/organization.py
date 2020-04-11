import pykube

import k8spin_common
from k8spin_common.helper import adopt, ensure, kubernetes_api
from k8spin_common.resources.namespace import create_namespace
from k8spin_common.resources.rbac import (create_cluster_role_binding,
                                          create_role_binding)

ORG_NAMESPACE_PREFIX = "org-"


def organization_namespacename_generator(organization_name):
    return f"{ORG_NAMESPACE_PREFIX}{organization_name}"


def ensure_organization_resources(organization_name: str):
    ensure_organization_namespace(organization_name)
    ensure_organization_role_bindings(organization_name)


@kubernetes_api
def ensure_organization_namespace(api, organization_name: str):
    org_namespace_name = organization_namespacename_generator(
        organization_name=organization_name)
    labels = {
        "k8spin.cloud/type": "organization",
        "k8spin.cloud/org": organization_name
    }
    owner = get_organization(organization_name)
    org_namespace = create_namespace(org_namespace_name, labels)
    org_namespace = ensure(org_namespace, owner)
    return org_namespace


@kubernetes_api
def ensure_organization_role_bindings(api, organization_name: str):
    organization = get_organization(organization_name)
    namespace = organization.organization_namespace
    roles = organization.roles
    rolebindings_names = list()
    # Organization level permissions
    for role in roles:
        # Cluster role to assign
        name = role.get('name')
        target_kind = "Group"
        targets = role.get('groups', None)
        if not targets:
            target_kind = "User"
            targets = role.get('users', list())
        for target in targets:
            rolebinding_name = f"{organization_name}-{name}-{target_kind.lower()}-{target.lower()}"
            labels = {
                "k8spin.cloud/type": "role",
                "k8spin.cloud/org": organization.name
            }
            role_binding = create_role_binding(
                rolebinding_name, namespace.name, labels, name, target_kind, target)
            ensure(role_binding, organization)
            rolebindings_names.append(rolebinding_name)
            # Create required binding to allow user query namespaces
            cluster_rolebinding_name = f"{organization_name}-{name}-{target_kind.lower()}-{target.lower()}"
            cluster_role_binding = create_cluster_role_binding(
                cluster_rolebinding_name, labels, "namespace-viewer", target_kind, target)
            ensure(cluster_role_binding, organization)
    # Finally, cleanup
    _clean_organization_roles(organization, rolebindings_names)


@kubernetes_api
def _clean_organization_roles(api, organization: k8spin_common.Organization, rolebindings_names: list):
    namespace = organization.organization_namespace
    org_role_bindings = pykube.RoleBinding.objects(api, namespace=namespace.name).filter(
        selector={"k8spin.cloud/type": "role", "k8spin.cloud/org": organization.name})
    for org_role_binding in org_role_bindings:
        if org_role_binding.name not in rolebindings_names:
            org_role_binding.delete()


@kubernetes_api
def get_organization_from_namespace(api, organization_namespace_name: str):
    organization_namespace = pykube.objects.Namespace.objects(
        api).get(name=organization_namespace_name)
    org_name = organization_namespace.labels["k8spin.cloud/org"]
    return get_organization(organization_name=org_name)


@kubernetes_api
def get_organization(api, organization_name: str):
    return k8spin_common.Organization.objects(api).get(name=organization_name)
