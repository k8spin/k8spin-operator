import logging
import os
from functools import partial
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Generator
import yaml
from pytest import fixture
from requests_html import HTMLSession

kind_cluster_name = "k8spin-operator-e2e"

@fixture(scope="session")
def cluster(kind_cluster) -> Generator[dict, None, None]:
    kubectl = kind_cluster.kubectl

    operator_image = "k8spin/k8spin-operator:v1.0.0-rc12"
    kind_cluster.load_docker_image(operator_image)

    webhook_image = "k8spin/k8spin-webhook:v1.0.0-rc12"
    kind_cluster.load_docker_image(webhook_image)

    logging.info("Deploying Calico")
    kubectl("delete", "daemonset", "-n" "kube-system", "kindnet")
    kubectl("apply", "-f", "https://docs.projectcalico.org/v3.16/manifests/calico.yaml")

    logging.info("Deploying CertManager")
    kubectl("apply", "-f", str(Path(__file__).parent.parent.parent / "deployments/kubernetes/cert-manager"))
    kubectl("rollout", "status", "-n", "cert-manager", "deployment/cert-manager")
    kubectl("rollout", "status", "-n", "cert-manager", "deployment/cert-manager-cainjector")
    kubectl("wait", "--for=condition=Available", "deployment", "--timeout=2m", "-n", "cert-manager" ,"--all")

    logging.info("Deploying K8Spin CRDS")
    kubectl("apply", "-f", str(Path(__file__).parent.parent.parent / "deployments/kubernetes/crds"))

    logging.info("Deploying Operator and Validator")
    kubectl("apply", "-f", str(Path(__file__).parent.parent.parent / "deployments/kubernetes"))

    logging.info("Waiting for rollout ...")
    kubectl("rollout", "status", "deployment/k8spin-webhook")
    kubectl("rollout", "status", "deployment/k8spin-operator")

    # with kind_cluster.port_forward("service/kube-web-view", 80) as port:
    #     url = f"http://localhost:{port}/"
    #     yield {"url": url}

    yield kind_cluster

    os.makedirs("./e2elogs", exist_ok=True)

    webhook_logs = open("e2elogs/webhook-logs.txt", "w")
    webhook_logs_out = kubectl("logs", "deployments/k8spin-webhook")
    webhook_logs.write(webhook_logs_out)
    webhook_logs.close()

    operator_logs = open("e2elogs/operator-logs.txt", "w")
    operator_logs_out = kubectl("logs", "deployments/k8spin-operator")
    operator_logs.write(operator_logs_out)
    operator_logs.close()

    custer_status_logs = open("e2elogs/cluster-status-logs.txt", "w")
    custer_status_out = kubectl("get", "all,org,tenant,space,ns", "-A")
    custer_status_logs.write(custer_status_out)
    custer_status_logs.close()

@fixture(scope="session")
def session(populated_cluster):

    url = populated_cluster["url"].rstrip("/")

    s = HTMLSession()

    def new_request(prefix, f, method, url, *args, **kwargs):
        return f(method, prefix + url, *args, **kwargs)

    s.request = partial(new_request, url, s.request)
    return s
