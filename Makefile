PROJECTNAME=$(shell basename "$(PWD)")
CLUSTER_VERSION="1.18.2"
KIND_CLUSTER_NAME="k8spin-operator"
PYTEST_PARAMS=""
TAG_VERSION="dev"

.PHONY: help
all: help
help: Makefile
	@echo
	@echo " Choose a command run in "$(PROJECTNAME)":"
	@echo
	@sed -n 's/^##//p' $< | column -t -s ':' |  sed -e 's/^/ /'
	@echo

## cluster-up: Creates the kind cluster
cluster-up:
	@kind create cluster --name $(KIND_CLUSTER_NAME) --image kindest/node:v${CLUSTER_VERSION} --config kind-calico.yaml && echo "Cluster created" || echo "Cluster already exists"

## cluster-down: Teardown the kind cluster
cluster-down:
	@kind delete cluster --name $(KIND_CLUSTER_NAME) -q && echo "Cluster deleted" || echo "Cluster does not exist exists"

## build: Local build the operator
build:
	@docker build -t k8spin/k8spin-operator:dev . -f dockerfiles/Dockerfile-operator
	@docker build -t k8spin/k8spin-webhook:dev . -f dockerfiles/Dockerfile-webhook

## deploy: Deploys the complete solution
deploy: load
	@kubectl --context kind-$(KIND_CLUSTER_NAME) apply -f https://docs.projectcalico.org/v3.8/manifests/calico.yaml
	@kubectl --context kind-$(KIND_CLUSTER_NAME) apply -f ./deploy/cert-manager
	@kubectl --context kind-$(KIND_CLUSTER_NAME) wait --for=condition=Available deployment --timeout=2m -n cert-manager --all
	@kubectl --context kind-$(KIND_CLUSTER_NAME) apply -f ./deploy/crds/ -n default
	@kubectl --context kind-$(KIND_CLUSTER_NAME) apply -f ./deploy/ -n default

## update: Update the complete solution
update: load
	@kubectl --context kind-$(KIND_CLUSTER_NAME) delete -f ./deploy/ --wait=true -n default
	@kubectl --context kind-$(KIND_CLUSTER_NAME) apply -f ./deploy/ -n default

## test-e2e: End-to-End tests. Use `PYTEST_ADDOPTS=--keep-cluster make test-e2e` to keep cluster
## --workers auto could be added when we want multiple workers installing the package pytest-parallel
test-e2e: build
	@virtualenv -p python3.8 .venv-test
	source .venv-test/bin/activate; \
	pip install -r tests/requirements.txt; \
	pip install -e k8spin_common; \
	pytest -v -r=a \
		--log-cli-level info \
		--log-cli-format '%(asctime)s %(levelname)s %(message)s' \
		--cluster-name k8spin-operator \
		${PYTEST_PARAMS} \
		tests/e2e;

test-kubeconfig:
	@export KUBECONFIG=.pytest-kind/k8spin-operator/kind-config-k8spin-operator

load: cluster-up build
	@kind load docker-image --name $(KIND_CLUSTER_NAME) k8spin/k8spin-operator:dev
	@kind load docker-image --name $(KIND_CLUSTER_NAME) k8spin/k8spin-webhook:dev

## kubie: Sets the kind cluster context
kubie:
	@kubie ctx kind-$(KIND_CLUSTER_NAME)

publish_dockerhub:
	@docker tag k8spin/k8spin-operator:dev k8spin/k8spin-operator:$(TAG_VERSION)
	@docker tag k8spin/k8spin-webhook:dev k8spin/k8spin-webhook:$(TAG_VERSION)
	@docker push k8spin/k8spin-operator:$(TAG_VERSION)
	@docker push k8spin/k8spin-webhook:$(TAG_VERSION)

clean:
	@rm -rf .kube .pytest_cache .pytest-kind .venv-test e2elogs
	@find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

.PHONY: kubectl_plugin
## kubectl_plugin: installs the plugin in /usr/local/bin/kubectl-k8spin. Requires root privileges
kubectl_plugin:
	@cp kubectl-k8spin.py /usr/local/bin/kubectl-k8spin
	@chmod +x /usr/local/bin/kubectl-k8spin
