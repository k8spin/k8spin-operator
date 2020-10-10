#!/usr/bin/env python

import argparse
import json
import subprocess

ORG = {
    "Name": ("metadata", "name"),
    "CPU": ("spec", "resources", "cpu"),
    "Memory": ("spec", "resources", "memory")
}


TENANT = {
    "Organization": ("metadata", "labels", "k8spin.cloud/org"),
    "Name": ("metadata", "name"),
    "CPU": ("spec", "resources", "cpu"),
    "Memory": ("spec", "resources", "memory")
}

SPACE = {
    "Organization": ("metadata", "labels", "k8spin.cloud/org"),
    "Tenant": ("metadata", "labels", "k8spin.cloud/tenant"),
    "Name": ("metadata", "name"),
    "CPU": ("spec", "resources", "cpu"),
    "Memory": ("spec", "resources", "memory"),
    "Default CPU": ("spec", "containers", "defaults", "resources", "cpu"),
    "Default Memory": ("spec", "containers", "defaults", "resources", "memory")
}


class CommandArguments():
    def __init__(self, org=None, tenant=None, space=None, cpu=None, memory=None, def_cpu=None, def_memory=None):
        self.org = org
        self.tenant = tenant
        self.space = space
        self.cpu = cpu
        self.memory = memory
        self.def_cpu = def_cpu
        self.def_memory = def_memory


def extract_from_dictionary(dictionary, *keys_or_indexes):
    value = dictionary
    for key_or_index in keys_or_indexes:
        value = value[key_or_index]
    return value


def tab_print(values):
    line = "{:<20s}"*len(values)
    print(line.format(*values))


def print_item(item, kind):
    tab_print([extract_from_dictionary(item, *kind[key])
               for key in kind.keys()])


def execute_get_command(command, kind):
    result = subprocess.run(
        filter(None, command.split(" ")), capture_output=True)
    if result.returncode == 0:
        j = json.loads(result.stdout)
        tab_print(list(kind.keys()))
        if j.get("kind") == "List":
            for item in j.get("items"):
                print_item(item, kind)
        else:
            print_item(j, kind)
    else:
        print(result.stderr.decode("utf-8"))


def execute_command(command, input=None):
    result = subprocess.run(
        filter(None, command.split(" ")), capture_output=True, input=input)
    if result.returncode == 0:
        print(result.stdout.decode("utf-8"))
    else:
        print(result.stderr.decode("utf-8"))


def execute_apply_command(json_manifest):
    command = "kubectl apply -f -"
    execute_command(command, json.dumps(json_manifest).encode("utf-8"))


def create_org(arg: CommandArguments):
    json_manifest = {
        "kind": "Organization",
        "apiVersion": "k8spin.cloud/v1",
        "metadata": {
            "name": arg.org
        },
        "spec": {
            "resources": {
                "cpu": arg.cpu,
                "memory": arg.memory
            }
        }
    }
    execute_apply_command(json_manifest)


def get_org(arg: CommandArguments):
    org = arg.org
    if not org:
        org = ""
    command = f"kubectl get org {org} -o json"
    execute_get_command(command, ORG)


def delete_org(arg: CommandArguments):
    org = arg.org
    if not org:
        org = ""
    command = f"kubectl delete org {org}"
    execute_command(command)


def create_tenant(arg: CommandArguments):
    json_manifest = {
        "kind": "Tenant",
        "apiVersion": "k8spin.cloud/v1",
        "metadata": {
            "name": arg.tenant,
            "namespace": f"org-{arg.org}"
        },
        "spec": {
            "resources": {
                "cpu": arg.cpu,
                "memory": arg.memory
            }
        }
    }
    execute_apply_command(json_manifest)


def get_tenant(arg: CommandArguments):
    org = arg.org
    if org:
        opts = f"-n org-{org}"
    else:
        opts = "--all-namespaces"

    tenant = arg.tenant
    command = f"kubectl get tenant {tenant} -o json {opts}"
    execute_get_command(command, TENANT)


def delete_tenant(arg: CommandArguments):
    command = f"kubectl delete tenant {arg.tenant} -n org-{arg.org}"
    execute_command(command)


def create_space(arg: CommandArguments):
    json_manifest = {
        "kind": "Space",
        "apiVersion": "k8spin.cloud/v1",
        "metadata": {
            "name": arg.space,
            "namespace": f"org-{arg.org}-tenant-{arg.tenant}"
        },
        "spec": {
            "resources": {
                "cpu": arg.cpu,
                "memory": arg.memory
            },
            "containers": {
                "defaults": {
                    "resources": {
                        "cpu": arg.def_cpu,
                        "memory": arg.def_memory
                    }
                }
            }
        }
    }
    execute_apply_command(json_manifest)


def get_space(arg: CommandArguments):
    org = arg.org
    tenant = arg.tenant
    if org:
        opts = f"-n org-{org}-tenant-{tenant}"
    else:
        opts = "--all-namespaces"
    space = arg.space

    command = f"kubectl get space {space} -o json {opts}"
    execute_get_command(command, SPACE)


def delete_space(arg: CommandArguments):
    command = f"kubectl delete space {arg.space} -n org-{arg.org}-tenant-{arg.tenant}"
    execute_command(command)


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

version_parser = commands.add_parser("version", help="K8SPin Version")

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

create_org_parser.add_argument("org_name")
create_org_parser.add_argument("--cpu", metavar="cpu", dest="cpu",
                               help="CPU Amount", required=True)
create_org_parser.add_argument("--memory", metavar="memory", dest="memory",
                               help="Memory Amount", required=True)


create_tenant_parser = create_commands.add_parser(
    "tenant", help="Tenant")

create_tenant_parser.add_argument("tenant_name")
create_tenant_parser.add_argument("--org", metavar="org", dest="org_name",
                                  help="Filter by Organization", required=True)
create_tenant_parser.add_argument("--cpu", metavar="cpu", dest="cpu",
                                  help="CPU Amount", required=True)
create_tenant_parser.add_argument("--memory", metavar="memory", dest="memory",
                                  help="Memory Amount", required=True)


create_space_parser = create_commands.add_parser(
    "space", help="Space")

create_space_parser.add_argument("space_name")
create_space_parser.add_argument("--org", metavar="org", dest="org_name",
                                 help="Filter by Organization", required=True)
create_space_parser.add_argument("--tenant", metavar="tenant", dest="tenant_name",
                                 help="Filter by Tenant", required=True)
create_space_parser.add_argument("--cpu", metavar="cpu", dest="cpu",
                                 help="CPU Amount", required=True)
create_space_parser.add_argument("--memory", metavar="memory", dest="memory",
                                 help="Memory Amount", required=True)
create_space_parser.add_argument("--default-cpu", metavar="cpu", dest="def_cpu",
                                 help="CPU Amount", required=True)
create_space_parser.add_argument("--default-memory", metavar="memory", dest="def_memory",
                                 help="Memory Amount", required=True)


delete_org_parser = delete_commands.add_parser(
    "org", help="Organization")

delete_org_parser.add_argument("org_name")

delete_tenant_parser = delete_commands.add_parser(
    "tenant", help="Tenant")

delete_tenant_parser.add_argument("tenant_name")
delete_tenant_parser.add_argument("--org", metavar="org", dest="org_name",
                                  help="Filter by Organization", required=True)

delete_space_parser = delete_commands.add_parser(
    "space", help="Space")

delete_space_parser.add_argument("space_name")
delete_space_parser.add_argument("--org", metavar="org", dest="org_name",
                                 help="Filter by Organization", required=True)
delete_space_parser.add_argument("--tenant", metavar="tenant", dest="tenant_name",
                                 help="Filter by Tenant", required=True)


# Parsing
main_args = parser.parse_args()

command = main_args.command if hasattr(main_args, "command") else None
sub_command = main_args.sub_command if hasattr(
    main_args, "sub_command") else None

if command and sub_command:
    org = main_args.org_name if hasattr(main_args, "org_name") else None
    tenant = main_args.tenant_name if hasattr(
        main_args, "tenant_name") else None
    space = main_args.space_name if hasattr(main_args, "space_name") else None
    cpu = main_args.cpu if hasattr(main_args, "cpu") else None
    memory = main_args.memory if hasattr(main_args, "memory") else None
    def_cpu = main_args.def_cpu if hasattr(main_args, "def_cpu") else None
    def_memory = main_args.def_memory if hasattr(
        main_args, "def_memory") else None
    arg = CommandArguments(org=org, tenant=tenant,
                           space=space, cpu=cpu, memory=memory, def_cpu=def_cpu, def_memory=def_memory)
    method_to_call = locals()[f"{command}_{sub_command}"]
    method_to_call(arg)
elif command == "version":
    print("K8SPin v1.0.0-rc11")
else:
    parser.print_help()
