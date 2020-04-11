from pykube.objects import APIObject, Namespace, NamespacedAPIObject


class Organization(APIObject):

    version = "k8spin.cloud/v1"
    endpoint = "organizations"
    kind = "Organization"

    @property
    def organization_namespace(self) -> Namespace:
        return Namespace.objects(self.api).get(name="org-"+self.name)

    @property
    def roles(self) -> list:
        return self.obj["spec"].get("roles", list())

    @property
    def tenants(self) -> list:
        ns = self.organization_namespace
        return Tenant.objects(self.api, ns.name).all()


class Tenant(NamespacedAPIObject):

    version = "k8spin.cloud/v1"
    endpoint = "tenants"
    kind = "Tenant"

    @property
    def org(self) -> Organization:
        namespace = Namespace.objects(
            self.api).get(name=self.namespace)
        org_name = namespace.labels["k8spin.cloud/org"]
        return Organization.objects(self.api).get(name=org_name)

    @property
    def tenant_namespace(self) -> Namespace:
        namespaces = Namespace.objects(self.api).filter(
            selector={"k8spin.cloud/org": self.org.name, "k8spin.cloud/type": "tenant"})
        for namespace in namespaces:
            if any([owner.get("name") == self.name for owner in namespace.metadata.get("ownerReferences", list())]):
                return namespace
        # TODO CHANGE WITH K8SPIN EXCEPTIONS
        raise Exception("Tenant namespace not found")

    @property
    def roles(self) -> list:
        return self.obj["spec"].get("roles", list())

    @property
    def spaces(self) -> list:
        ns = self.tenant_namespace
        return Space.objects(self.api, ns.name).all()

class Space(NamespacedAPIObject):

    version = "k8spin.cloud/v1"
    endpoint = "spaces"
    kind = "Space"

    @property
    def org(self) -> Organization:
        namespace = Namespace.objects(
            self.api).get(name=self.namespace)
        org_name = namespace.labels["k8spin.cloud/org"]
        return Organization.objects(self.api).get(name=org_name)

    @property
    def tenant(self) -> Tenant:
        namespace = Namespace.objects(
            self.api).get(name=self.namespace)
        tenant_name = namespace.labels["k8spin.cloud/tenant"]
        tenant_namespace = self.org.organization_namespace
        return Tenant.objects(self.api, tenant_namespace.name).get(name=tenant_name)

    @property
    def space_namespace(self) -> Namespace:
        namespaces = Namespace.objects(self.api).filter(
            selector={"k8spin.cloud/org": self.org.name, "k8spin.cloud/tenant": self.tenant.name, "k8spin.cloud/type": "space"})
        for namespace in namespaces:
            if any([owner.get("name") == self.name for owner in namespace.metadata.get("ownerReferences", list())]):
                return namespace
        # TODO CHANGE WITH K8SPIN EXCEPTIONS
        raise Exception("Space namespace not found")

    @property
    def roles(self) -> list:
        return self.obj["spec"].get("roles", list())

    @property
    def resources(self) -> list:
        return self.obj["spec"]["resources"]

    @property
    def default_container_resources(self) -> list:
        return self.obj["spec"]["containers"]["defaults"]["resources"]
