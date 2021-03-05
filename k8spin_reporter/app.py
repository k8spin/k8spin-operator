import os

from flask import Flask, jsonify, render_template
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from healthcheck import HealthCheck

from k8spin_reporter import data, feed
scheduler = APScheduler()

app = Flask(__name__)

# TODO: Add an environment variable to setup the database.
# With SQLAlchemy is suppose that any SQL database will work
# We use during development sqlite.
PATH = os.path.dirname(os.path.abspath(__file__))
DB_FILE_PATH = f"{PATH}/k8spin.db"

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE_PATH}"
db = SQLAlchemy(app)


# interval examples
@scheduler.task("interval", id="feed", seconds=3, misfire_grace_time=900)
def asyncFeed():
    feed.do_feed(db.engine)


@app.route("/organizations")
def organizations():
    return render_template("organization.html")


@app.route("/organizations/<organization_id>")
def organization(organization_id):
    return render_template("organization.html", organization_id=organization_id)


@app.route("/organizations/<organization_id>/tenants")
def tenants(organization_id):
    return render_template("tenant.html", organization_id=organization_id)


@app.route("/organizations/<organization_id>/tenants/<tenant_id>")
def tenant(organization_id, tenant_id):
    return render_template("tenant.html", organization_id=organization_id, tenant_id=tenant_id)


@app.route("/report")
def report():
    return render_template("report.html")


@app.route("/api/organizations")
def api_organizations():
    orgs = data.orgs(db.engine)
    return jsonify(orgs)


@app.route("/api/organizations/<organization_id>")
def api_organization(organization_id):
    orgs = data.org(db.engine, organization_id)
    return jsonify(orgs)


@app.route("/api/organizations/<organization_id>/resources")
def org_resources(organization_id):
    resources = data.org_current_resources(db.engine, organization_id)
    return jsonify(resources)


@app.route("/api/organizations/<organization_id>/history")
def org_history(organization_id):
    resources = data.org_history_resources(db.engine, organization_id)
    return jsonify(resources)


@app.route("/api/organizations/<organization_id>/tenants")
def api_tenants(organization_id):
    tenants = data.tenants(db.engine, organization_id)
    return jsonify(tenants)


@app.route("/api/organizations/<organization_id>/tenants/<tenant_id>")
def api_tenant(organization_id, tenant_id):
    t = data.tenant(db.engine, organization_id, tenant_id)
    return jsonify(t)


@app.route("/api/organizations/<organization_id>/tenants/<tenant_id>/history")
def tenant_history(organization_id, tenant_id):
    resources = data.tenant_history_resources(db.engine, organization_id, tenant_id)
    return jsonify(resources)


@app.route("/api/organizations/<organization_id>/tenants/<tenant_id>/spaces")
def spaces(organization_id, tenant_id):
    spaces = data.spaces(db.engine, tenant_id)
    return jsonify(spaces)


@app.route("/api/organizations/<organization_id>/tenants/<tenant_id>/spaces/<space_id>/resources")
def space_resources(organization_id, tenant_id, space_id):
    resources = data.space_current_resources(db.engine, space_id)
    return jsonify(resources)


@app.route("/api/organizations/<organization_id>/tenants/<tenant_id>/resources")
def tenant_resources(organization_id, tenant_id):
    resources = data.tenant_current_resources(db.engine, tenant_id)
    return jsonify(resources)


if __name__ == "__main__":
    health = HealthCheck(app, "/health")
    scheduler.init_app(app)
    scheduler.start()
    app.run(debug=True)
