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

def memory_convert_unit(value: str) -> float:
    # https://k8smeetup.github.io/docs/tasks/configure-pod-container/assign-cpu-ram-container/#cpu-and-ram-units
    #E, P, T, G, M, K, Ei, Pi, Ti, Gi, Mi, Ki
    value = value.replace("i", "")
    scale_dict = {
        "E": pow(10, 18),
        "P": pow(10, 15),
        "T": pow(10, 12),
        "G": pow(10, 9),
        "M": pow(10, 6),
        "K": pow(10, 3)
    }
    for unit in scale_dict:
        if unit in value:
            value = value.replace(unit, "")
            return float(value)*scale_dict[unit]
    return float(value)


def cpu_convert_unit(value: str) -> float:
    # https://k8smeetup.github.io/docs/tasks/configure-pod-container/assign-cpu-ram-container/#cpu-and-ram-units
    # 0.1, 1, 100m
    scale = 1000
    if "m" in value:
        scale = 1
        value = value.replace("m", "")
    return float(value)*scale
