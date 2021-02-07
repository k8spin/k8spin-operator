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
