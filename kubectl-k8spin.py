#!/usr/bin/env python

import argparse
import json
import subprocess


class CommandArguments():
    def __init__(self, org=None, tenant=None, space=None, namespace=None):
        self.org = org
        self.tenant = tenant
        self.space = space
        self.namespace = namespace


def get_org(arg: CommandArguments):
    org = arg.org
    if not org:
        org = ""
    command = f"kubectl get org {org} -o json"
    result = subprocess.run(
        filter(None, command.split(" ")), capture_output=True)
    if result.returncode == 0:
        j = json.loads(result.stdout)
        print("{:<20s} {:<20s} {:<20s}".format("Name", "CPU", "Memory"))
        if j.get("items", None):
            for item in j.get("items"):
                name = item.get("metadata").get("name")
                cpu = item.get("spec").get("resources").get("cpu")
                mem = item.get("spec").get("resources").get("memory")
                print("{:<20s} {:<20s} {:<20s}".format(name, cpu, mem))
        else:
            item = j
            name = item.get("metadata").get("name")
            cpu = item.get("spec").get("resources").get("cpu")
            mem = item.get("spec").get("resources").get("memory")
            print("{:<20s} {:<20s} {:<20s}".format(name, cpu, mem))
    else:
        print(result.stderr.decode("utf-8"))


def delete_org(arg: CommandArguments):
    org = arg.org
    if not org:
        org = ""
    command = f"kubectl delete org {org}"
    result = subprocess.run(
        filter(None, command.split(" ")), capture_output=True)
    if result.returncode == 0:
        print(result.stdout.decode("utf-8"))
    else:
        print(result.stderr.decode("utf-8"))


def get_tenant(arg: CommandArguments):
    org = arg.org
    if org:
        opts = f"-n org-{org}"
    else:
        opts = "--all-namespaces"

    tenant = arg.tenant
    command = f"kubectl get tenant {tenant} -o json {opts}"
    result = subprocess.run(
        filter(None, command.split(" ")), capture_output=True)
    if result.returncode == 0:
        j = json.loads(result.stdout)
        print("{:<20s} {:<20s} {:<20s} {:<20s}".format(
            "Org", "Name", "CPU", "Memory"))
        if tenant:
            item = j
            org = item.get("metadata").get("labels").get("k8spin.cloud/org")
            name = item.get("metadata").get("name")
            cpu = item.get("spec").get("resources").get("cpu")
            mem = item.get("spec").get("resources").get("memory")
            print("{:<20s} {:<20s} {:<20s} {:<20s}".format(org, name, cpu, mem))
        else:
            for item in j.get("items", None):
                org = item.get("metadata").get(
                    "labels").get("k8spin.cloud/org")
                name = item.get("metadata").get("name")
                cpu = item.get("spec").get("resources").get("cpu")
                mem = item.get("spec").get("resources").get("memory")
                print("{:<20s} {:<20s} {:<20s} {:<20s}".format(
                    org, name, cpu, mem))
    else:
        print(result.stderr.decode("utf-8"))


def get_space(arg: CommandArguments):
    org = arg.org
    tenant = arg.tenant
    if org:
        opts = f"-n org-{org}-tenant-{tenant}"
    else:
        opts = "--all-namespaces"
    space = arg.space

    command = f"kubectl get space {space} -o json {opts}"
    result = subprocess.run(
        filter(None, command.split(" ")), capture_output=True)
    if result.returncode == 0:
        j = json.loads(result.stdout)
        print("{:<20s} {:<20s} {:<20s} {:<20s} {:<20s}".format(
            "Org", "Tenant", "Name", "CPU", "Memory"))
        if space:
            item = j
            org = item.get("metadata").get("labels").get("k8spin.cloud/org")
            tenant = item.get("metadata").get(
                "labels").get("k8spin.cloud/tenant")
            name = item.get("metadata").get("name")
            cpu = item.get("spec").get("resources").get("cpu")
            mem = item.get("spec").get("resources").get("memory")
            print("{:<20s} {:<20s} {:<20s} {:<20s} {:<20s}".format(
                org, tenant, name, cpu, mem))
        else:
            for item in j.get("items", None):
                org = item.get("metadata").get(
                    "labels").get("k8spin.cloud/org")
                tenant = item.get("metadata").get(
                    "labels").get("k8spin.cloud/tenant")
                name = item.get("metadata").get("name")
                cpu = item.get("spec").get("resources").get("cpu")
                mem = item.get("spec").get("resources").get("memory")
                print("{:<20s} {:<20s} {:<20s} {:<20s} {:<20s}".format(
                    org, tenant, name, cpu, mem))
    else:
        print(result.stderr.decode("utf-8"))


# Parent parser
parser = argparse.ArgumentParser(prog="kubectl k8spin",
                                 description="K8Spin kubectl plugin to manage multi-tenancy concepts")

# Parent debug flag
parser.add_argument("--debug", default=False, required=False,
                    action="store_true", dest="debug", help="Activate debug mode")

# Parent commands
commands = parser.add_subparsers(title="commands", dest="command")

# Add get parser
get_parser = commands.add_parser(
    "get", help="Get K8Spin resources")

# Add create parser
create_parser = commands.add_parser(
    "create", help="Create K8Spin resources")

# Add delete parser
delete_parser = commands.add_parser(
    "delete", help="Delete K8Spin resources")

# create commands
get_commands = get_parser.add_subparsers(
    title="Query For", dest="sub_command")
create_commands = create_parser.add_subparsers(
    title="Create", dest="sub_command")
delete_commands = delete_parser.add_subparsers(
    title="Delete", dest="sub_command")

get_org_parser = get_commands.add_parser(
    "org", help="Organization")

get_org_parser.add_argument("org_name", nargs="?", default="")

get_tenant_parser = get_commands.add_parser(
    "tenant", help="Tenant")

get_tenant_parser.add_argument("tenant_name", nargs="?", default="")
get_tenant_parser.add_argument("--org", metavar="org", dest="org_name",
                               help="Filter by Organization")

get_space_parser = get_commands.add_parser(
    "space", help="Space")

get_space_parser.add_argument("space_name", nargs="?", default="")
get_space_parser.add_argument("--tenant", metavar="tenant", dest="tenant_name",
                              help="Filter by Tenant")
get_space_parser.add_argument("--org", metavar="org", dest="org_name",
                              help="Filter by Organization")


create_org_parser = create_commands.add_parser(
    "org", help="Organization")

create_tenant_parser = create_commands.add_parser(
    "tenant", help="Tenant")

create_space_parser = create_commands.add_parser(
    "space", help="Space")

delete_org_parser = delete_commands.add_parser(
    "org", help="Organization")

delete_org_parser.add_argument("org_name", nargs="?", default="")

delete_tenant_parser = delete_commands.add_parser(
    "tenant", help="Tenant")

delete_space_parser = delete_commands.add_parser(
    "space", help="Space")


# Parsing
main_args = parser.parse_args()

command = main_args.command if hasattr(main_args, "command") else None
sub_command = main_args.sub_command if hasattr(
    main_args, "sub_command") else None

if command and sub_command:
    method_to_call = locals()[f"{command}_{sub_command}"]
    org = main_args.org_name if hasattr(main_args, "org_name") else None
    tenant = main_args.tenant_name if hasattr(
        main_args, "tenant_name") else None
    space = main_args.space_name if hasattr(main_args, "space_name") else None
    arg = CommandArguments(org=org, tenant=tenant, space=space)
    method_to_call(arg)
else:
    parser.print_help()
