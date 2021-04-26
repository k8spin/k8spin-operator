from flask import Blueprint, jsonify, request

from .validator_utils import (check_space_quotas,  # pylint: disable=E0401
                              check_tenant_quotas)

blueprint = Blueprint("validator", __name__, url_prefix="/validator")


def validator_response(uid, allowed, message):
    return jsonify({"apiVersion": "admission.k8s.io/v1",
                    "kind": "AdmissionReview",
                    "response":
                        {
                            "uid": uid,
                            "allowed": allowed,
                            "status": {"message": message}
                        }
                    }
                   )


@blueprint.route('/tenants', methods=['POST'])
def tenant_validator():
    request_info = request.get_json()
    resource_object = request_info["request"]["object"]
    response, message = check_tenant_quotas(resource_object)
    return validator_response(request_info["request"]["uid"], response, message)


@blueprint.route('/spaces', methods=['POST'])
def space_validator():
    request_info = request.get_json()
    resource_object = request_info["request"]["object"]
    response, message = check_space_quotas(resource_object)
    return validator_response(request_info["request"]["uid"], response, message)
