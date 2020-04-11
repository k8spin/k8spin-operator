import pykube
import yaml

from k8spin_common.helper import kubernetes_api


@kubernetes_api
def create_role_binding(api, name: str, namespace: str, labels: dict, cluster_role: str, subject_kind: str, subject_name: str) -> pykube.RoleBinding:
    _obj = yaml.safe_load(
        f"""
        apiVersion: rbac.authorization.k8s.io/v1
        kind: RoleBinding
        metadata:
          name: {name}
          namespace: {namespace}
        roleRef:
          apiGroup: rbac.authorization.k8s.io
          kind: ClusterRole
          name: {cluster_role}
        subjects:
        - kind: {subject_kind}
          name: {subject_name}
          apiGroup: rbac.authorization.k8s.io
        """
        )
    metadata = _obj.get("metadata")
    metadata["labels"] = labels
    return pykube.RoleBinding(api, _obj)


@kubernetes_api
def create_cluster_role_binding(api, name: str, labels: dict, cluster_role: str, subject_kind: str, subject_name: str) -> pykube.ClusterRoleBinding:
    _obj = yaml.safe_load(
        f"""
        apiVersion: rbac.authorization.k8s.io/v1
        kind: ClusterRoleBinding
        metadata:
          name: {name}
        roleRef:
          apiGroup: rbac.authorization.k8s.io
          kind: ClusterRole
          name: {cluster_role}
        subjects:
        - kind: {subject_kind}
          name: {subject_name}
          apiGroup: rbac.authorization.k8s.io
        """
        )
    metadata = _obj.get("metadata")
    metadata["labels"] = labels
    return pykube.RoleBinding(api, _obj)
