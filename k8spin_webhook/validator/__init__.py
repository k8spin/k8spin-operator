from flask import Blueprint, request, jsonify

from .validator_utils import check_space_quotas, check_tenant_quotas

blueprint = Blueprint("validator", __name__, url_prefix="/validator")

def validator_response(allowed, message): 
    return jsonify({"response": {"allowed": allowed, "status": {"message": message}}})

@blueprint.route('/tenants', methods=['POST'])
def tenant_validator():
    request_info = request.get_json()
    resource_object = request_info["request"]["object"]
    response, message = check_tenant_quotas(resource_object)
    return validator_response(response, message)

@blueprint.route('/spaces', methods=['POST'])
def space_validator():
    request_info = request.get_json()
    resource_object = request_info["request"]["object"]
    response, message = check_space_quotas(resource_object)
    return validator_response(response, message)