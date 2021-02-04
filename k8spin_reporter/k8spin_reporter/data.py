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