from k8spin_reporter import db


def orgs(db_engine):
    data = []
    query = f"""
        SELECT id,name 
        FROM organization
    """
    rows = db.query(db_engine, query)
    for r in rows:
        data.append({
            "id": r[0],
            "name": r[1]
        })
    return data


def org(db_engine, organization_id):
    data = []
    query = f"""
        SELECT id,name 
        FROM organization
        WHERE
        id = "{organization_id}"
    """
    rows = db.query(db_engine, query)
    for r in rows:
        data.append({
            "id": r[0],
            "name": r[1]
        })
    if len(data) == 1:
        return data[0]
    else:
        raise Exception("TBD: Multiple results")


def org_current_resources(db_engine, organization_id):
    data = []
    query = f"""
        SELECT t1.allocated_cpu, t1.allocated_memory, t2.used_cpu, t2.used_memory
        FROM
        (
            SELECT t2.organization_id as organization_id, t2.cpu as allocated_cpu, t2.memory as allocated_memory FROM
            (
                SELECT cpu,memory, max(id) id
                FROM organization_resources
                GROUP BY organization_id
            ) t1, organization_resources t2
            WHERE t1.id = t2.id
        ) t1,
        (
            SELECT t2.organization_id as organization_id, sum(t2.cpu) as used_cpu, sum(t2.memory) as used_memory FROM
            (
                SELECT organization_id, tenant_id, space_id, max(id) id
                FROM space_usage
                GROUP BY organization_id, tenant_id, space_id
            )
            t1, space_usage t2
            WHERE t1.id = t2.id
            GROUP BY t2.organization_id
        ) t2
        WHERE t1.organization_id = t2.organization_id
        AND t1.organization_id = "{organization_id}"
    """
    rows = db.query(db_engine, query, False)
    for r in rows:
        data.append({
            "allocated_cpu": r[0],
            "allocated_memory": r[1],
            "used_cpu": r[2],
            "used_memory": r[3],
        })
    if len(data) != 1:
        return None
    return data[0]


def tenant_current_resources(db_engine, tenant_id):
    data = []
    query = f"""
        SELECT t1.allocated_cpu, t1.allocated_memory, t2.used_cpu, t2.used_memory
        FROM
        (
            SELECT t2.tenant_id as tenant_id, t2.cpu as allocated_cpu, t2.memory as allocated_memory FROM
            (
                SELECT cpu,memory, max(id) id
                FROM tenant_resources
                GROUP BY tenant_id
            ) t1, tenant_resources t2
            WHERE t1.id = t2.id
        ) t1,
        (
            SELECT t2.tenant_id as tenant_id, sum(t2.cpu) as used_cpu, sum(t2.memory) as used_memory FROM
            (
                SELECT tenant_id, space_id, max(id) id
                FROM space_usage
                GROUP BY tenant_id, space_id
            )
            t1, space_usage t2
            WHERE t1.id = t2.id
            GROUP BY t2.tenant_id
        ) t2
        WHERE t1.tenant_id = t2.tenant_id
        AND t1.tenant_id = "{tenant_id}"
    """
    rows = db.query(db_engine, query, False)
    for r in rows:
        data.append({
            "allocated_cpu": r[0],
            "allocated_memory": r[1],
            "used_cpu": r[2],
            "used_memory": r[3],
        })
    if len(data) != 1:
        return None
    return data[0]


def space_current_resources(db_engine, space_id):
    data = []
    query = f"""
        SELECT t1.allocated_cpu, t1.allocated_memory, t2.used_cpu, t2.used_memory
        FROM
        (
            SELECT t2.space_id as space_id, t2.cpu as allocated_cpu, t2.memory as allocated_memory FROM
            (
                SELECT cpu,memory, max(id) id
                FROM space_resources
                GROUP BY space_id
            ) t1, space_resources t2
            WHERE t1.id = t2.id
        ) t1,
        (
            SELECT t2.space_id as space_id, sum(t2.cpu) as used_cpu, sum(t2.memory) as used_memory FROM
            (
                SELECT space_id, max(id) id
                FROM space_usage
                GROUP BY space_id
            )
            t1, space_usage t2
            WHERE t1.id = t2.id
            GROUP BY t2.space_id
        ) t2
        WHERE t1.space_id = t2.space_id
        AND t1.space_id = "{space_id}"
    """
    rows = db.query(db_engine, query, False)
    for r in rows:
        data.append({
            "allocated_cpu": r[0],
            "allocated_memory": r[1],
            "used_cpu": r[2],
            "used_memory": r[3],
        })
    if len(data) != 1:
        return None
    return data[0]

# TODO: Currently it returns up to 7 days of data. Aggregated by day.
# TODO: Make it configurable by day, hour...


def org_history_resources(db_engine, organization_id):
    data = []
    query = f"""
        SELECT used.day, allocated.allocated_cpu, used.used_cpu, allocated.allocated_memory, used.used_memory

        FROM (

            SELECT organization_id, day, sum(cpu) as used_cpu, sum(memory) as used_memory
            FROM (
                SELECT organization_id, tenant_id, space_id, strftime('%Y%m%d', reported) as day, avg(cpu) as cpu, avg(memory) as memory
                FROM space_usage
                WHERE organization_id = "{organization_id}"
                GROUP BY organization_id, tenant_id, space_id, strftime('%Y%m%d', reported)
            )
            GROUP BY organization_id, day

        ) used,

        (
            SELECT organization_id, strftime('%Y%m%d', reported) as day, avg(cpu) as allocated_cpu, avg(memory) as allocated_memory
            FROM organization_resources
            WHERE organization_id = "{organization_id}"
            GROUP BY organization_id, strftime('%Y%m%d', reported)

        ) allocated

        WHERE used.organization_id = "{organization_id}"
        AND used.organization_id = allocated.organization_id
        AND used.day = allocated.day
        ORDER BY used.day DESC
        LIMIT 7;
    """
    rows = db.query(db_engine, query, False)
    for r in rows:
        data.append({
            "day": r[0],
            "allocated_cpu": r[1],
            "used_cpu": r[2],
            "allocated_memory": r[3],
            "used_memory": r[4],
        })
    return data


def tenant_history_resources(db_engine, organization_id, tenant_id):
    data = []
    query = f"""
        SELECT used.day, allocated.allocated_cpu, used.used_cpu, allocated.allocated_memory, used.used_memory

        FROM (

            SELECT tenant_id, day, sum(cpu) as used_cpu, sum(memory) as used_memory
            FROM (
                SELECT tenant_id, space_id, strftime('%Y%m%d', reported) as day, avg(cpu) as cpu, avg(memory) as memory
                FROM space_usage
                WHERE
                organization_id = "{organization_id}"
                AND
                tenant_id = "{tenant_id}"
                GROUP BY tenant_id, space_id, strftime('%Y%m%d', reported)
            )
            GROUP BY tenant_id, day

        ) used,

        (
            SELECT tenant_id, strftime('%Y%m%d', reported) as day, avg(cpu) as allocated_cpu, avg(memory) as allocated_memory
            FROM tenant_resources
            WHERE tenant_id = "{tenant_id}"
            GROUP BY tenant_id, strftime('%Y%m%d', reported)

        ) allocated

        WHERE used.tenant_id = "{tenant_id}"
        AND used.tenant_id = allocated.tenant_id
        AND used.day = allocated.day
        ORDER BY used.day DESC
        LIMIT 7;
    """
    rows = db.query(db_engine, query, False)
    for r in rows:
        data.append({
            "day": r[0],
            "allocated_cpu": r[1],
            "used_cpu": r[2],
            "allocated_memory": r[3],
            "used_memory": r[4],
        })
    return data


def tenants(db_engine, organization_id):
    data = []
    query = f"""
        SELECT id,name 
        FROM tenant
        WHERE organization_id = "{organization_id}"
    """
    rows = db.query(db_engine, query)
    for r in rows:
        data.append({
            "id": r[0],
            "name": r[1]
        })
    return data


def tenant(db_engine, organization_id, tenant_id):
    data = []
    query = f"""
        SELECT id,name 
        FROM tenant
        WHERE
        organization_id = "{organization_id}"
        AND
        id = "{tenant_id}"
    """
    rows = db.query(db_engine, query)
    for r in rows:
        data.append({
            "id": r[0],
            "name": r[1]
        })
    if len(data) == 1:
        return data[0]
    else:
        raise Exception("TBD: Multiple results")


def spaces(db_engine, tenant_id):
    data = []
    query = f"""
        SELECT id,name 
        FROM space
        WHERE tenant_id = "{tenant_id}"
    """
    rows = db.query(db_engine, query)
    for r in rows:
        data.append({
            "id": r[0],
            "name": r[1]
        })
    return data


def space_usage(db_engine, start_date, finish_date, space_id):
    data = []
    query = f"""
        SELECT
            space_id,
            STRFTIME('%Y-%m-%d', reported) reported, 
            AVG(cpu) cpu
        FROM
            space_resources
        GROUP BY
            STRFTIME('%Y-%m-%d', reported),
            space_id
        ORDER BY
            reported;
    """
    rows = db.query(db_engine, query)
    for r in rows:
        data.append({
            "id": r[0],
            "name": r[1]
        })
    return data
