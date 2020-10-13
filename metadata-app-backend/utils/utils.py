import concurrent.futures
import os
import re
import traceback
import cx_Oracle
import requests
import urllib3
import yaml
from flask import json
from requests.adapters import HTTPAdapter
from urllib3 import PoolManager
import appconfigs.user_view_configs as grid_configs
from dbmodels.dbmodels import SampleData, UserViewConfig, AppLog
import ssl
from app import LOG

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

config = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../appconfigs/lims_user_config")
config_options = yaml.safe_load(open(config, "r"))
ENV = config_options['env']
USER = config_options['username']
PASSW = config_options['password']
DELPHI_URL = None
if ENV == 'dev':
    LIMS_API_ROOT = config_options['lims_end_point_dev']
elif ENV == 'prod':
    LIMS_API_ROOT = config_options['lims_end_point_prod']
elif ENV == 'local':
    LIMS_API_ROOT = config_options['lims_end_point_local']

if ENV == 'dev' or ENV == 'local':
    DELPHI_URL = config_options['delphi_url_dev']
elif ENV == 'prod':
    DELPHI_URL = config_options['delphi_url_prod']


class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_SSLv23)


s = requests.Session()
s.mount('http://', MyAdapter(max_retries=5))


def get_user_title(result):
    p = re.search("title(.*?)\]\,", str(result))
    title = re.sub(r'title\': \[b\'', "", p[0])
    title = re.sub(r'\']\,', "", title)
    return title


# returns user's full_name
def get_user_fullname(result):
    p = re.search("displayName(.*?)\]\,", str(result))
    full_name = re.sub(r'displayName\': \[b\'', "", p[0])
    full_name = re.sub(r'\/.*', "", full_name)
    name = full_name.split(", ")[1] + " " + full_name.split(", ")[0]
    return name


# checks whether user is in GRP_SKI_Haystack_NetIQ
# returns ezGroups the user is a part of
def get_user_group(result):
    # compiles reg ex pattern into reg ex object
    p = re.compile('CN=(.*?)\,')
    groups = re.sub('CN=Users', '', str(result))
    # returns all matching groups
    return p.findall(groups)


def get_column_configs(role, username):
    '''
    Method to return column configurations based on user role. Not all users are authorized to see all the data returned by this server.
    :param role:
    :return: column configurations
    '''
    try:
        settings = grid_configs.settings
        user_view_config = UserViewConfig.query.filter_by(username=username).first()
        print(user_view_config)
        if user_view_config:
            print("is user view config")
            hidden_columns = user_view_config.hidden_columns
            hidden_columns_values = hidden_columns.split(",") if hidden_columns else []
            hidden_column_arr = []
            if not hidden_columns_values:
                settings["hiddenColumns"]["columns"] = hidden_column_arr
            else:
                for item in hidden_columns_values:
                    print(item)
                    hidden_column_arr.append(int(item))
                    settings["hiddenColumns"]["columns"] = hidden_column_arr
                print(settings)
            # print(username, "view settings", settings)
        if role == 'clinical':
            return grid_configs.clinicalColHeaders, grid_configs.clinicalColumns, settings
        elif role == 'admin':
            return grid_configs.adminColHeaders, grid_configs.adminColumns, settings
        elif role == 'user':
            return grid_configs.nonClinicalColHeaders, grid_configs.nonClinicalColumns, settings
    except Exception:
        add_error_to_logs("Error getting column configs {}".format(traceback.print_exc()))


def get_crdb_connection(CRDB_UN, CRDB_PW, CRDB_URL):
    try:
        conn = cx_Oracle.connect(CRDB_UN, CRDB_PW, CRDB_URL)
        return conn
    except Exception:
        add_error_to_logs("Error connecting to CRDB {}".format(traceback.print_exc()), "api")
        return None


def get_id_without_aliquot_annotations(igo_id):
    """
    IGO ID's in LIMS have trailing "_+[1-9]" to annotate aliquot samples. To query fastq endpoint, we need igo id's
    without trailing aliquot annotations. You would think that the ID's under request should not have trailing aliquot
    annotations, well you are wrong, check for "05457_I_17". The first sample under request in LIMS for this ID is
    "05457_I_17_1". Therefore, it is important to the sanity check and if there are such cases this method is to handle
    them and return usable IGO ID for the fastq endpoint.
    :return id
    """
    try:
        pattern = re.compile("^[0-9]+_[0-9]+.*$")  # sample id without alphabets
        pattern2 = re.compile("^[0-9]+_[A-Z]+_[0-9]+.*$")  # sample id without alphabets
        id_without_letters = re.findall(pattern, igo_id)
        id_with_letters = re.findall(pattern2, igo_id)
        if id_without_letters:
            return "_".join(id_without_letters[0].split("_")[:2])
        if id_with_letters:
            return "_".join(id_with_letters[0].split("_")[:3])
        return igo_id
    except Exception:
        err_msg = "error while extrating IGO ID without aliquot annotations for id {}:\n{}".format(igo_id,
                                                                                                   traceback.print_exc())
        add_error_to_logs(err_msg)
        return igo_id


def get_fastq_data(igo_id):
    """
    Method to get Fastq file path for Sample using IGO ID.
    :return
    """
    url = None
    sanitized_id = get_id_without_aliquot_annotations(igo_id)
    try:
        if not sanitized_id:
            return None
        url = "{}ngs-stats/rundone/fastqsbyigoid/{}".format(DELPHI_URL, sanitized_id)
        request = requests.get(url)
        data = json.loads(request.content.decode("utf-8", "strict"))
        fastq_data = []
        for item in data:
            fastq_data.append(item.get("fastq"))
        return ",".join(fastq_data)
    except Exception:
        message = "Error querying delphi fastq endpoint {} , {}: ".format(url, traceback.print_exc())
        add_error_to_logs(message, "api")
        return None


def get_sample_status(igo_id):
    """
    Method to get current LIMS Sample status IGO ID.
    :return
    """
    try:
        r = s.get(LIMS_API_ROOT + "/LimsRest/getSampleStatus?igoId={}".format(igo_id),
                  auth=(USER, PASSW), verify=False)
        data = r.content.decode("utf-8", "strict")
        return data
    except Exception:
        err_message = "Error querying /LimsRest/getSampleStatus?igoId={} endpoint: ".format(
            igo_id), traceback.print_exc()
        add_error_to_logs(err_message, "api")
        print(err_message)
        return None


def create_sample_object(db_sample_data):
    """
    Method to create Sample object to send to the frontend.
    :return
    """
    status = get_sample_status(db_sample_data.igo_id)
    fastq = None
    if status and "data qc" in status:
        fastq = get_fastq_data(db_sample_data.igo_id)
    sample_object = SampleData(
        id=db_sample_data.id,
        mrn=db_sample_data.mrn,
        igo_id=db_sample_data.igo_id,
        investigator_sample_id=db_sample_data.investigator_sample_id,
        sample_type=db_sample_data.sample_type,
        species=db_sample_data.species,
        cmo_patient_id=db_sample_data.cmo_patient_id,
        cmo_sample_id=db_sample_data.cmo_sample_id,
        dmp_id=db_sample_data.dmp_id,
        preservation=db_sample_data.preservation,
        tumor_normal=db_sample_data.tumor_normal,
        tissue_source=db_sample_data.tissue_source,
        sample_origin=db_sample_data.sample_origin,
        specimen_type=db_sample_data.specimen_type,
        sex=db_sample_data.sex,
        parent_tumor_type=db_sample_data.parent_tumor_type,
        tumor_type=db_sample_data.tumor_type,
        tissue_location=db_sample_data.tissue_location,
        ancestor_sample=db_sample_data.ancestor_sample,
        sample_status=status,
        lab_head=db_sample_data.lab_head,
        data_access=db_sample_data.data_access,
        do_not_use=str(bool(db_sample_data.do_not_use)).lower(),
        recipe=db_sample_data.recipe,
        bait_set=db_sample_data.bait_set,
        fastq_data=fastq
    )
    return sample_object


def get_sample_objects(db_results, **kwargs):
    """
    Method to create Sample objects and filter based on parameters selected by user on frontend.
    :return
    """
    sample_objects = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(create_sample_object, db_results))
        sample_objects.extend(list(results))
    if "application" in kwargs and kwargs.get("application") != 'None':
        print(kwargs.get("application"))
        sample_objects = list(
            filter(lambda x: x.recipe.lower() == kwargs.get("application")[0].lower(), sample_objects))
    if "has_data" in kwargs:
        sample_objects = list(filter(lambda x: x.fastq_data, sample_objects))
    return sample_objects


def add_to_logs(message, user):
    """
    Method to important info messages to different logs.
    """
    print(message, "User: {}".format(user))
    LOG.info(message + " User: {}".format(user))


def add_error_to_logs(message, user):
    """
    Method to important error messages to app logs.
    """
    print(message, "User: {}".format(user))
    LOG.error(message + " User: {}".format(user))


def add_to_db_logs(message, user):
    """
    Method to add important info messages to db AppLog table.
    """
    print(message, "User: {}".format(user))
    AppLog.info(message=message, user=user)


def add_error_to_db_logs(message, user):
    """
    Method to important error messages to db AppLog table.
    """
    print(message, "User: {}".format(user))
    AppLog.error(message=message, user=user)


def create_cache_key(*args):
    key_items = []
    for item in args:
        key_items.append(str(item).replace(" ", "_"))
    return "_".join(key_items)


def get_cached_data(key):
    # TODO - Do a json-dumps so that any data-type can be cached
    if uwsgi.cache_exists(key, CACHE_NAME):
        data = uwsgi.cache_get(key, CACHE_NAME)
        AppLog.info("Using cached data for %s" % key, "api")
        return data
    AppLog.info("No data cached for %s" % key, "api")
    return None


def cache_data(key, content, time):
    AppLog("Caching %s for %d seconds" % (key, time), "api")
    uwsgi.cache_update(key, content, time, CACHE_NAME)