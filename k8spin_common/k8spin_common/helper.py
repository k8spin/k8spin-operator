import os

import pykube
from pykube.objects import APIObject, NamespacedAPIObject


def kubernetes_api(function):
    def wrap_function(*args, **kwargs):
        api = _get_kube_api()
        res = function(api, *args, **kwargs)
        api.session.close()
        return res
    return wrap_function


def adopt(owner: APIObject, children: APIObject) -> APIObject:
    if not children.metadata.get("ownerReferences", None):
        children.metadata["ownerReferences"] = list()
    ownerReference = {
        "apiVersion": owner.version,
        "kind": owner.__class__.__name__,
        "name": owner.name,
        "uid": owner.metadata["uid"]
    }
    if not any(child_owner.get("uid") == owner.metadata["uid"] for child_owner in children.metadata["ownerReferences"]):
        children.metadata["ownerReferences"].append(ownerReference)
    return children


def _get_kube_api():
    try:
        config = pykube.KubeConfig.from_service_account()
    except FileNotFoundError:
        config = pykube.KubeConfig.from_file(
            os.getenv("KUBECONFIG", "~/.kube/config"))
    api = pykube.HTTPClient(config)
    return api


def ensure(resource: APIObject, owner: APIObject):
    if not resource.exists():
        resource = adopt(owner, resource)
        resource.create()
    else:
        resource.update()
    return resource