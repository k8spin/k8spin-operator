import pykube
from k8spin_common import Organization
from k8spin_common.helper import kubernetes_api
from k8spin_common.resources import quotas

from k8spin_reporter import db


@kubernetes_api
def do_feed(api, db_engine):
    orgs = Organization.objects(api).all()
    for org in orgs:
        feed_org(api, db_engine, org)


def feed_org(api, db_engine, org):
    org_id = org.metadata["uid"]
    if not org_exists(db_engine, org_id):
        insert_org(db_engine, org_id, org.name)
    org_resources = org.resources
    insert_org_resources(db_engine,
                         org_id, org_resources["cpu"], org_resources["memory"])
    tenants = org.tenants
    for tenant in tenants:
        feed_tenant(api, db_engine, org_id, tenant)


def feed_tenant(api, db_engine, org_id, tenant):
    tenant_id = tenant.metadata["uid"]
    if not tenant_exists(db_engine, tenant_id, org_id):
        insert_tenant(db_engine, tenant_id, tenant.name, org_id)
    tenant_resources = tenant.resources
    insert_tenant_resources(db_engine,
                            tenant_id, tenant_resources["cpu"], tenant_resources["memory"])
    spaces = tenant.spaces
    for space in spaces:
        feed_space(api, db_engine, org_id, tenant_id, space)


def feed_space(api, db_engine, org_id, tenant_id, space):
    space_id = space.metadata["uid"]
    if not space_exists(db_engine, space_id, org_id, tenant_id):
        insert_space(db_engine, space_id, space.name, org_id, tenant_id)
    space_resources = space.resources
    insert_space_resources(db_engine,
                           space_id, space_resources["cpu"], space_resources["memory"])

    namespace = space.space_namespace
    quota = pykube.ResourceQuota.objects(
        api, namespace.name).get(name="quotas")
    cpu = quota.obj["status"]["used"]["requests.cpu"]
    memory = quota.obj["status"]["used"]["requests.memory"]
    print(
        f"Organization: {org_id}. Tenant {tenant_id}. Space {space.name}")
    print(
        f"CPU: {cpu}/{space_resources['cpu']}. Memory: {memory}/{space_resources['memory']}")
    insert_space_usage(db_engine, space_id, cpu, memory)


def org_exists(db_engine, uid):
    query = f"SELECT id FROM organization WHERE id='{uid}'"
    rows = db.query(db_engine, query)
    if rows:
        return True
    return False


def insert_org(db_engine, uid, name):
    query = f"INSERT INTO organization(id,name) VALUES ('{uid}', '{name}')"
    org_id = db.insert(db_engine, query)
    print(f"Organization {name} inserted in DB with id {org_id}")


def insert_org_resources(db_engine, uid, cpu, memory):
    query = f"INSERT INTO organization_resources(organization_id,cpu,memory) VALUES ('{uid}', '{quotas.cpu_convert_unit(cpu)}', '{quotas.memory_convert_unit(memory)}')"
    r_id = db.insert(db_engine, query)
    print(f"Current organization resources inserted in DB with id {r_id}")


def tenant_exists(db_engine, uid, org_id):
    query = f"SELECT id FROM tenant WHERE id='{uid}' AND organization_id='{org_id}'"
    rows = db.query(db_engine, query)
    if rows:
        return True
    return False


def insert_tenant(db_engine, uid, name, org_id):
    query = f"INSERT INTO tenant(id,name,organization_id) VALUES ('{uid}', '{name}', '{org_id}')"
    tenant_id = db.insert(db_engine, query)
    print(f"Tenant {name} inserted in DB with id {tenant_id}")


def insert_tenant_resources(db_engine, uid, cpu, memory):
    query = f"INSERT INTO tenant_resources(tenant_id,cpu,memory) VALUES ('{uid}', '{quotas.cpu_convert_unit(cpu)}', '{quotas.memory_convert_unit(memory)}')"
    r_id = db.insert(db_engine, query)
    print(f"Current tenant resources inserted in DB with id {r_id}")


def space_exists(db_engine, uid, org_id, tenant_id):
    query = f"SELECT id FROM space WHERE id='{uid}' AND organization_id='{org_id}' AND tenant_id='{tenant_id}'"
    rows = db.query(db_engine, query)
    if rows:
        return True
    return False


def insert_space(db_engine, uid, name, org_id, tenant_id):
    query = f"INSERT INTO space(id,name,organization_id,tenant_id) VALUES ('{uid}', '{name}', '{org_id}', '{tenant_id}')"
    space_id = db.insert(db_engine, query)
    print(f"Space {name} inserted in DB with id {space_id}")


def insert_space_resources(db_engine, uid, cpu, memory):
    query = f"INSERT INTO space_resources(space_id,cpu,memory) VALUES ('{uid}', '{quotas.cpu_convert_unit(cpu)}', '{quotas.memory_convert_unit(memory)}')"
    r_id = db.insert(db_engine, query)
    print(f"Current space resources inserted in DB with id {r_id}")


def insert_space_usage(db_engine, space_id, cpu, memory):
    query = f"INSERT INTO space_usage(space_id,cpu,memory) VALUES ('{space_id}', {quotas.cpu_convert_unit(cpu)}, {quotas.memory_convert_unit(memory)})"
    r_id = db.insert(db_engine, query)
    print(f"Current space usage inserted in DB with id {r_id}")
