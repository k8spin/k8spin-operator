import pykube
import yaml

from k8spin_common.helper import kubernetes_api


@kubernetes_api
def create_namespace(api, name: str, labels: dict) -> pykube.Namespace:
    _obj = yaml.safe_load(
        f"""
        apiVersion: v1
        kind: Namespace
        metadata:
          name: {name}
        """
    )
    metadata = _obj.get("metadata")
    metadata["labels"] = labels
    return pykube.Namespace(api, _obj)
