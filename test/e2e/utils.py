import yaml
from k8spin_common import Organization, Tenant, Space
from pykube import Deployment, Service

def create_org_object(api, organization_name):
    obj = yaml.safe_load(
        f"""
            apiVersion: k8spin.cloud/v1
            kind: Organization
            metadata:
                name: {organization_name}
            spec:
                resources:
                    cpu: "5"
                    memory: "5G"
        """
    )
    return Organization(api, obj)

def create_tenant_object(api, organization_name, tenant_name):
    obj = yaml.safe_load(
        f"""
            apiVersion: k8spin.cloud/v1
            kind: Tenant
            metadata:
                namespace: org-{organization_name}
                name: {tenant_name}
            spec:
                resources:
                    cpu: "2"
                    memory: "2G"
        """
    )
    return Tenant(api, obj)

def create_space_object(api, organization_name, tenant_name, space_name):
    obj = yaml.safe_load(
        f"""
            apiVersion: k8spin.cloud/v1
            kind: Space
            metadata:
                namespace: org-{organization_name}-tenant-{tenant_name}
                name: {space_name}
            spec:
                resources:
                    cpu: "1"
                    memory: "1G"
                containers:
                    defaults:
                        resources:
                            cpu: 10m
                            memory: 64Mi
        """
    )
    return Space(api, obj)

def create_helloworld_deployment(api, organization_name, tenant_name, space_name, deployment_name):
    obj = yaml.safe_load(
        f"""
            apiVersion: apps/v1
            kind: Deployment
            metadata:
                namespace: org-{organization_name}-tenant-{tenant_name}-space-{space_name}
                name: {deployment_name}
            spec:
                selector:
                    matchLabels:
                        app: {deployment_name}
                replicas: 1
                template:
                    metadata:
                        labels:
                            app: {deployment_name}
                    spec:
                        containers:
                        - name: {deployment_name}
                          image: nginxinc/nginx-unprivileged
                          ports:
                            - containerPort: 8080
        """
    )
    return Deployment(api, obj)

def create_helloworld_service(api, organization_name, tenant_name, space_name, service_name):
    obj = yaml.safe_load(
        f"""
            kind: Service
            apiVersion: v1
            metadata:
                namespace: org-{organization_name}-tenant-{tenant_name}-space-{space_name}
                name: {service_name}
            spec:
                selector:
                    app: {service_name}
                ports:
                    - protocol: TCP
                      port: 80
                      targetPort: 8080
        """
    )
    return Service(api, obj)
