from flask import Flask, jsonify
from flask_apscheduler import APScheduler
from healthcheck import HealthCheck

from k8spin_reporter import data, feed

scheduler = APScheduler()

app = Flask(__name__)


# interval examples
@scheduler.task("interval", id="feed", seconds=3, misfire_grace_time=900)
def asyncFeed():
    feed.do_feed()


@app.route('/organization')
def organizations():
    orgs = data.orgs()
    return jsonify(orgs)


if __name__ == "__main__":
    health = HealthCheck(app, "/health")
    scheduler.init_app(app)
    scheduler.start()
    app.run()
