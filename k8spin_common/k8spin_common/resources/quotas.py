import pykube
import yaml

from k8spin_common.helper import kubernetes_api


@kubernetes_api
def create_limit_range(api, name: str, namespace: str, labels: dict, cpu: str, memory: str) -> pykube.LimitRange:
    _obj = yaml.safe_load(
        f"""
        apiVersion: v1
        kind: LimitRange
        metadata:
          name: {name}
          namespace: {namespace}
        spec:
          limits:
          - default:
              cpu: {cpu}
              memory: {memory}
            defaultRequest:
              cpu: {cpu}
              memory: {memory}
            type: Container
        """
    )
    metadata = _obj.get("metadata")
    metadata["labels"] = labels
    return pykube.LimitRange(api, _obj)


@kubernetes_api
def create_resource_quota(api, name: str, namespace: str, labels: dict, cpu: str, memory: str) -> pykube.ResourceQuota:
    _obj = yaml.safe_load(
        f"""
        apiVersion: v1
        kind: ResourceQuota
        metadata:
          name: {name}
          namespace: {namespace}
        spec:
          hard:
            requests.cpu: {cpu}
            requests.memory: {memory}
            limits.cpu: {cpu}
            limits.memory: {memory}
        """
    )
    metadata = _obj.get("metadata")
    metadata["labels"] = labels
    return pykube.ResourceQuota(api, _obj)
