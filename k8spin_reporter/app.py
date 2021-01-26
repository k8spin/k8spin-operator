import os

from flask import Flask, jsonify
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


@app.route('/organization')
def organizations():
    orgs = data.orgs(db.engine)
    return jsonify(orgs)


if __name__ == "__main__":
    health = HealthCheck(app, "/health")
    scheduler.init_app(app)
    scheduler.start()
    app.run()
