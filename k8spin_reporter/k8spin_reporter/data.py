from k8spin_reporter import db


def orgs():
    data = []
    query = f"SELECT id,name FROM organization"
    rows = db.query(query)
    for r in rows:
        data.append({
            "id": r[0],
            "name": r[1]
        })
    return data
