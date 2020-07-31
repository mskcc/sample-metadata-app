import re
import traceback
from functools import wraps

from flask import Blueprint, request, make_response, jsonify, json, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint

from appconfigs.api_configs import auth_key
from dbmodels.dbmodels import AppLog, Sample, Patient, Assay, db
from utils.utils import get_sample_objects, ENV, add_error_to_logs, add_to_logs

outbound_api = Blueprint('outbound_api', __name__)

### swagger specific ###
SWAGGER_URL = '/api'
API_URL = None
if ENV == "dev":
    API_URL= 'https://delphi.mskcc.org/sample-metadata-dev-api/api/static/dev/swagger.json'
if ENV == "local":
    API_URL= 'http://localhost:5000/api/static/local/swagger.json'
if ENV == "prod":
    API_URL= 'https://delphi.mskcc.org/sample-metadata-api/api/static/prod/swagger.json'

print(API_URL)
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Sample Metadata"
    }
)


### end swagger specific ###


def api_key_required(f):
    @wraps(f)
    def wrapper():
        if request.headers:
            host = request.headers.get("Host")
            authorization = request.headers.get("Authorization")
            access_key = re.split(r'[,\s\n]\s*', authorization)[1].strip() if authorization else None
            if auth_key == access_key:
                return f()
            else:
                message = "Incorrect authorization key: {}, requesting hostname: {}".format(access_key, host)
                add_error_to_logs(message, host)
        response = make_response(jsonify(data=None, success=False, message="Authorization failed"), 401, None)
        return response

    return wrapper


@outbound_api.route("/search_metadata", methods=['POST'])
@api_key_required
def search_metadata():
    try:
        host = None
        arguments = request.args.to_dict()
        print(arguments)
        host = request.headers.get("Host")
        if len(arguments) == 1 and ("igo_id" in arguments or "cmo_id" in arguments):
            if "igo_id" in arguments:
                igo_id = arguments["igo_id"]
                kwargs = {}
                search_start_message = "Metadata search using 'igo_id={}', Requesting Host: {}.".format(igo_id, host)
                add_to_logs(search_start_message,
                            host)  # add messages to db logging, local app logging and uwsgi logging.
                db_results = db.session.query(Sample) \
                    .outerjoin(Patient, Patient.mrn == Sample.mrn) \
                    .outerjoin(Assay, Sample.id == Assay.id_sample) \
                    .add_columns(Sample.id, Sample.mrn, Sample.igo_id, Sample.investigator_sample_id,
                                 Sample.sample_type,
                                 Sample.species, Patient.cmo_patient_id, Patient.cmo_sample_id, Patient.dmp_id,
                                 Sample.preservation, Sample.tumor_normal, Sample.tissue_source, Sample.sample_origin,
                                 Sample.specimen_type, Sample.sex, Sample.parent_tumor_type, Sample.tumor_type,
                                 Sample.tissue_location, Sample.ancestor_sample, Sample.sample_status, Sample.lab_head,
                                 Sample.data_access, Sample.do_not_use, Assay.recipe, Assay.bait_set) \
                    .filter(Sample.igo_id == igo_id).all()
                print(len(db_results))
                sample_objects = get_sample_objects(db_results, **kwargs)
                response = make_response(jsonify(
                    data=(json.dumps([r.__dict__ for r in sample_objects], sort_keys=True,
                                     indent=4,
                                     separators=(',', ': '))),
                    success=True,
                    error=False,
                    message="success"), 200, None)
                response.headers.add('Access-Control-Allow-Origin', '*')
                post_search_message = "Returned {} results: {}".format(len(sample_objects), sample_objects)
                add_to_logs(post_search_message, host)
                return response
            if "cmo_id" in arguments:
                cmo_id = arguments["cmo_id"]
                kwargs = {}
                search_start_message = "Metadata search using 'igo_id={}', Requesting Host: {}.".format(cmo_id, host)
                add_to_logs(search_start_message,
                            host)  # add messages to db logging, local app logging and uwsgi logging.
                db_results = db.session.query(Patient) \
                    .outerjoin(Sample, Patient.mrn == Sample.mrn) \
                    .outerjoin(Assay, Sample.id == Assay.id_sample) \
                    .add_columns(Sample.id, Sample.mrn, Sample.igo_id, Sample.investigator_sample_id,
                                 Sample.sample_type,
                                 Sample.species, Patient.cmo_patient_id, Patient.cmo_sample_id, Patient.dmp_id,
                                 Sample.preservation, Sample.tumor_normal, Sample.tissue_source, Sample.sample_origin,
                                 Sample.specimen_type, Sample.sex, Sample.parent_tumor_type, Sample.tumor_type,
                                 Sample.tissue_location, Sample.ancestor_sample, Sample.sample_status, Sample.lab_head,
                                 Sample.data_access, Sample.do_not_use, Assay.recipe, Assay.bait_set) \
                    .filter(Patient.cmo_sample_id == cmo_id).all()
                print(len(db_results))
                sample_objects = get_sample_objects(db_results, **kwargs)
                response = make_response(jsonify(
                    data=(json.dumps([r.__dict__ for r in sample_objects], sort_keys=True,
                                     indent=4,
                                     separators=(',', ': '))),
                    success=True,
                    error=False,
                    message="success"), 200, None)
                response.headers.add('Access-Control-Allow-Origin', '*')
                post_search_message = "Returned {} results: {}".format(len(sample_objects), sample_objects)
                add_to_logs(post_search_message, host)
                return response
            return "api method"
        else:
            message = "Bad request, invalid arguments passed: {}. You need to pass one keyword argument" \
                      " {} or {} with value. Requesting Host: {}".format(arguments, "igo_id", "cmo_id", host)
            add_error_to_logs(message, host)
            response = make_response(jsonify(data=None, success=False, error=True, message=message), 400, None)
            return response
    except Exception as e:
        message = "Error : {}".format(traceback.print_exc())
        add_error_to_logs(message, "api")
        response = make_response(jsonify(data=None, success=False, message="Internal server error."), 500, None)
        return response


@outbound_api.route("/static/<path:path>")
def api(path):
    """
    Method to serve Swagger.json file for swagger api.
    :return
    """
    return send_from_directory("../static", path)
