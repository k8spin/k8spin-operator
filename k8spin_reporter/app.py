from flask import Flask
from flask_apscheduler import APScheduler
from healthcheck import HealthCheck
from k8spin_reporter import feed

scheduler = APScheduler()

# interval examples
@scheduler.task("interval", id="feed", seconds=3, misfire_grace_time=900)
def asyncFeed():
    feed.do_feed()

if __name__ == "__main__":
    app = Flask(__name__)
    health = HealthCheck(app, "/health")
    scheduler.init_app(app)
    scheduler.start()
    app.run()
