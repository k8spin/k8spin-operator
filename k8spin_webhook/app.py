import logging
from os import getenv

from flask import Flask
from healthcheck import HealthCheck

import mutator  # pylint: disable=E0401
import validator  # pylint: disable=E0401

logger = logging.getLogger()
logger.setLevel(getenv("LOGGING_LEVEL", "INFO"))

app = Flask(__name__)

health = HealthCheck(app, "/health")

app.register_blueprint(validator.blueprint)
app.register_blueprint(mutator.blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443,
            ssl_context=("/certs/tls.crt", "/certs/tls.key"))
