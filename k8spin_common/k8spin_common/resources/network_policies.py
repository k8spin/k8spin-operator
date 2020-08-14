import pykube
import yaml

from k8spin_common.helper import kubernetes_api

from k8spin_common import NetworkPolicy

@kubernetes_api
def create_network_policy(api, name: str, namespace: str, labels: dict, allow_incoming_network: list) -> NetworkPolicy:

    _obj = yaml.safe_load(
        f"""
        apiVersion: networking.k8s.io/v1
        kind: NetworkPolicy
        metadata:
            name: k8spin-space-network-policy
            namespace: {namespace}
        spec:
            podSelector: {{}}
            ingress: []
            policyTypes:
            - Ingress
        """
    )

    allow_organizations = allow_incoming_network.get("organizations", [])
    allow_tenants = allow_incoming_network.get("tenants", [])
    allow_spaces = allow_incoming_network.get("spaces", [])

    for organization in allow_organizations:
        _obj["spec"]["ingress"].append({
            "from": [
                {
                    "namespaceSelector":{
                        "matchLabels":{
                            "k8spin.cloud/org": organization.get("organization_name")
                        }
                    }
                }
            ]
        })

    for tenant in allow_tenants:
        _obj["spec"]["ingress"].append({
            "from": [
                {
                    "namespaceSelector":{
                        "matchLabels":{
                            "k8spin.cloud/org": tenant.get("organization_name"),
                            "k8spin.cloud/tenant": tenant.get("tenant_name")
                        }
                    }
                }
            ]
        })

    for space in allow_spaces:
        _obj["spec"]["ingress"].append({
            "from": [
                {
                    "namespaceSelector":{
                        "matchLabels":{
                            "k8spin.cloud/org": space.get("organization_name"),
                            "k8spin.cloud/tenant": space.get("tenant_name"),
                            "k8spin.cloud/space": space.get("space_name")
                        }
                    }
                }
            ]
        })

    metadata = _obj.get("metadata")
    metadata["labels"] = labels
    return NetworkPolicy(api, _obj)