import datetime
import random
import uuid

from faker import Faker
from faker.providers import company, job

fake = Faker()
fake.add_provider(company)
fake.add_provider(job)


def gen_orgs(amount):
    data = list()
    for _ in range(amount):
        data.append({
            "id": str(uuid.uuid4()),
            "name": fake.company(),
        })
    return data


def gen_org_resources(orgs, since, hour_step):
    current_date = datetime.datetime.now()
    data_date = since
    data = list()
    while data_date < current_date:
        data_date = data_date + datetime.timedelta(hours=hour_step)
        for org in orgs:
            data.append({
                "reported": data_date,
                "organization_id": org.get("id"),
                "cpu": random.randrange(5, 10, 1),
                "memory": random.randrange(512, 1024, 128),
            })
    return data


def gen_tenant(orgs, amount):
    data = list()
    for _ in range(amount):
        data.append({
            "id": str(uuid.uuid4()),
            "name": fake.company(),
            "organization_id": orgs[random.randint(0, len(orgs)-1)].get("id")
        })
    return data


def gen_tenant_resources(tenants, since, hour_step):
    current_date = datetime.datetime.now()
    data_date = since
    data = list()
    while data_date < current_date:
        data_date = data_date + datetime.timedelta(hours=hour_step)
        for tenant in tenants:
            data.append({
                "reported": data_date,
                "tenant_id": tenant.get("id"),
                "cpu": random.randrange(3, 5, 1),
                "memory": random.randrange(128, 512, 128),
            })
    return data


def gen_spaces(tenants, amount):
    data = list()
    for _ in range(amount):
        tenant_index = random.randint(0, len(tenants)-1)
        data.append({
            "id": str(uuid.uuid4()),
            "name": fake.job(),
            "organization_id": tenants[tenant_index].get("organization_id"),
            "tenant_id": tenants[tenant_index].get("id")
        })
    return data


def gen_space_resources(spaces, since, hour_step):
    current_date = datetime.datetime.now()
    data_date = since
    data = list()
    while data_date < current_date:
        data_date = data_date + datetime.timedelta(hours=hour_step)
        for space in spaces:
            data.append({
                "reported": data_date,
                "space_id": space.get("id"),
                "cpu": random.randrange(1, 3, 1),
                "memory": random.randrange(128, 512, 128),
            })
    return data

def gen_space_usage(spaces, since, hour_step):
    current_date = datetime.datetime.now()
    data_date = since
    data = list()
    while data_date < current_date:
        data_date = data_date + datetime.timedelta(hours=hour_step)
        for space in spaces:
            data.append({
                "reported": data_date,
                "organization_id": space.get("organization_id"),
                "tenant_id": space.get("tenant_id"),
                "space_id": space.get("id"),
                "cpu": random.randrange(1, 2, 1),
                "memory": random.randrange(16, 256, 16),
            })
    return data

def gen_sql(data, table_name):
    columns = ",".join(data.keys())
    values = ""
    for val in data.values():
        if type(val) == str:
            values = values + f"\"{val}\","
        elif type(val) == int:
            values = values + f"{val},"
        elif type(val) == datetime.datetime:
            data_date = val.strftime("%Y-%m-%d %H:%M:%S.%f")
            values = values + f"\"{data_date}\","
    return f"INSERT INTO {table_name} ({columns}) VALUES ({values[:-1]});"

if __name__ == "__main__":
    since = datetime.datetime.now() - datetime.timedelta(days=10)
    orgs = gen_orgs(1)
    org_resources = gen_org_resources(orgs, since, 1)
    tenants = gen_tenant(orgs, 1)
    tenant_resources = gen_tenant_resources(tenants, since, 1)
    spaces = gen_spaces(tenants, 2)
    space_resources = gen_space_resources(spaces, since, 1)
    space_usage = gen_space_usage(spaces, since, 1)

    for org in orgs:
        print(gen_sql(org, "organization"))
    for res in org_resources:
        print(gen_sql(res, "organization_resources"))
    for tenant in tenants:
        print(gen_sql(tenant, "tenant"))
    for res in tenant_resources:
        print(gen_sql(res, "tenant_resources"))
    for space in spaces:
        print(gen_sql(space, "space"))
    for res in space_resources:
        print(gen_sql(res, "space_resources"))
    for res in space_usage:
        print(gen_sql(res, "space_usage"))
