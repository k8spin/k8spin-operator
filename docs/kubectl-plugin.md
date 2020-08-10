# K8Spin kubectl plugin

This plugin makes straight forward to use and manage K8Spin concepts with the
[kubectl binary](https://kubernetes.io/docs/tasks/extend-kubectl/kubectl-plugins/).

## Install

Place [kubectl-k8spin.py](../kubectl-k8spin.py) file in your path **without extension**.

```bash
$ cp ./../kubectl-k8spin.py /usr/local/bin/kubectl-k8spin
$ chmod +x /usr/local/bin/kubectl-k8spin
```

or, run in the root of this repository

```bash
$ sudo make kubectl_plugin
```

### Requirements

The plugin requires python 3.6+ to be previously installed.

### Check

```bash
$ kubectl k8spin
usage: kubectl k8spin [-h] [--debug] {get,create,delete} ...

K8Spin kubectl plugin to manage multi-tenancy concepts

optional arguments:
  -h, --help           show this help message and exit
  --debug              Activate debug mode

commands:
  {get,create,delete}
    get                Get K8Spin resources
    create             Create K8Spin resources
    delete             Delete K8Spin resources
```

## Usage

To start using it, execute `kubectl k8spin`.

### Create

```bash
$ kubectl k8spin create --help
usage: kubectl k8spin create [-h] {org,tenant,space} ...

optional arguments:
  -h, --help          show this help message and exit

Create:
  {org,tenant,space}
    org               Organization
    tenant            Tenant
    space             Space
```

#### Organizations

```bash
$ kubectl k8spin create org --help
usage: kubectl k8spin create org [-h] --cpu cpu --memory memory org_name

positional arguments:
  org_name

optional arguments:
  -h, --help       show this help message and exit
  --cpu cpu        CPU Amount
  --memory memory  Memory Amount
```

**Example:**

```bash
$ kubectl k8spin create org demo --cpu 10 --memory 10Gi
organization.k8spin.cloud/demo created
```

#### Tenants

```bash
$ kubectl k8spin create tenant --help
usage: kubectl k8spin create tenant [-h] --org org --cpu cpu --memory memory tenant_name

positional arguments:
  tenant_name

optional arguments:
  -h, --help       show this help message and exit
  --org org        Filter by Organization
  --cpu cpu        CPU Amount
  --memory memory  Memory Amount
```

**Example:**

```bash
$ kubectl k8spin create tenant demo --org demo --cpu 10 --memory 10Gi
tenant.k8spin.cloud/demo created
```

#### Spaces

```bash
$ kubectl k8spin create space --help
usage: kubectl k8spin create space [-h] --org org --tenant tenant --cpu cpu --memory memory --default-cpu cpu --default-memory memory space_name

positional arguments:
  space_name

optional arguments:
  -h, --help            show this help message and exit
  --org org             Filter by Organization
  --tenant tenant       Filter by Tenant
  --cpu cpu             CPU Amount
  --memory memory       Memory Amount
  --default-cpu cpu     CPU Amount
  --default-memory memory
                        Memory Amount
```

**Example:**

```bash
$ kubectl k8spin create space demo --org demo --tenant demo --cpu 10 --memory 10Gi --default-cpu 0.1 --default-memory 1Mi
space.k8spin.cloud/demo created
```

### Get

```bash
$ kubectl k8spin get --help
usage: kubectl k8spin get [-h] {org,tenant,space} ...

optional arguments:
  -h, --help          show this help message and exit

Query For:
  {org,tenant,space}
    org               Organization
    tenant            Tenant
    space             Space
```

#### Organizations

```bash
$ kubectl k8spin get org --help
usage: kubectl k8spin get org [-h] [org_name]

positional arguments:
  org_name

optional arguments:
  -h, --help  show this help message and exit
```

**Example:**

```bash
$ kubectl k8spin get org
Name                CPU                 Memory
demo                10                  10Gi
```

#### Tenants

```bash
$ kubectl k8spin get tenant --help
usage: kubectl k8spin get tenant [-h] [--org org] [tenant_name]

positional arguments:
  tenant_name

optional arguments:
  -h, --help   show this help message and exit
  --org org    Filter by Organization
```

**Example:**

```bash
$ kubectl k8spin get tenant
Organization        Name                CPU                 Memory
demo                demo                10                  10Gi
```

#### Spaces

```bash
$ kubectl k8spin get space --help
usage: kubectl k8spin get space [-h] [--tenant tenant] [--org org] [space_name]

positional arguments:
  space_name

optional arguments:
  -h, --help       show this help message and exit
  --tenant tenant  Filter by Tenant
  --org org        Filter by Organization
```

**Example:**

```bash
$ kubectl k8spin get space
Organization        Tenant              Name                CPU                 Memory              Default CPU         Default Memory
demo                demo                demo                10                  10Gi                0.1                 1Mi
```

### Delete

```bash
$ kubectl k8spin delete --help
usage: kubectl k8spin delete [-h] {org,tenant,space} ...

optional arguments:
  -h, --help          show this help message and exit

Delete:
  {org,tenant,space}
    org               Organization
    tenant            Tenant
    space             Space
```

#### Spaces

```bash
$ kubectl k8spin delete space --help
usage: kubectl k8spin delete space [-h] --org org --tenant tenant space_name

positional arguments:
  space_name

optional arguments:
  -h, --help       show this help message and exit
  --org org        Filter by Organization
  --tenant tenant  Filter by Tenant
```

**Example:**

```bash
$ kubectl k8spin delete space demo --org demo --tenant demo
space.k8spin.cloud "demo" deleted
```

#### Tenants

```bash
$ kubectl k8spin delete space tenant --help
usage: kubectl k8spin delete space [-h] --org org --tenant tenant space_name

positional arguments:
  space_name

optional arguments:
  -h, --help       show this help message and exit
  --org org        Filter by Organization
  --tenant tenant  Filter by Tenant
```

**Example:**

```bash
$ kubectl k8spin delete tenant demo --org demo
tenant.k8spin.cloud "demo" deleted
```

#### Organizations

```bash
$ kubectl k8spin delete org --help
usage: kubectl k8spin delete org [-h] org_name

positional arguments:
  org_name

optional arguments:
  -h, --help  show this help message and exit
```

**Example:**

```bash
$ kubectl k8spin delete org demo
organization.k8spin.cloud "demo" deleted
```
