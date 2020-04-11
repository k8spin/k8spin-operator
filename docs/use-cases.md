# Use cases

## Single Organization cluster

The is the example we had in K8Spin.cloud:

Organizations:
  - K8Spin.cloud

Tenants at `K8Spin.cloud` **Organization**:
  - angel@k8spin.cloud
  - pau@k8spin.cloud
  - bill@microsoft.com

Spaces at `angel@k8spin.cloud` **tenant** under `K8Spin.cloud` **organization**:
  - demo-app-1

Spaces at `pau@k8spin.cloud` **tenant** under `K8Spin.cloud` **organization**:
  - single-project


## Multiple Organization cluster

awesomevps.supercloud VPS provider wants to provide access to a managed Kubernetes cluster to multiple organizations.

Organizations:
  - prof-services-dot-com (10 cores, 10Gb)
  - awesome-startup-dot-io (5 cores, 5Gb)

Tenants at `prof-services-dot-com` **Organization**:
  - team-red (3 cores, 5Gb)
  - team-blue (3 cores, 3Gb)

Tenants at `awesome-startup-dot-io` **Organization**:
  - frontend-team (2 cores, 2Gb)
  - backend-team (3 cores, 3Gb)

Spaces at `team-red` **tenant** under `prof-services-dot-com` **organization**:
  - demo-frontend-january (1 core, 1Gb)
  - new-feature-frontend (1 core, 2Gb)

Spaces at `backend-team` **tenant** under `awesome-startup-dot-io` **organization**:
  - poc-kafka (2 cores, 2Gb)
  - fixture-two (0.5 core, 0.5Gb)

Some notes about this Cluster:

- **awesome-startup-dot-io** organization admin can not create more tenants as cluster admin
defined the Organization with 5 cores and 5 Gb and it currently has 2 two tenants with 2+3 cores and 2+3 Gb.

- **prof-services-dot-com** organization admin can create more tenants because the current
organization utilization is 2+3cores and 5+3 Gb. So the current utilization is: 6/10 cores and 8/10 Gb.

- **team-red** tenant admin (in the **prof-services-dot-com** organization) can create more spaces because
tenant has 3 cores and 5Gb allocated, and the current usage is: 1+1 core and 1+2Gb. A new Space
up to 1 core and 2 Gb can be created under **team-red** tenant.

