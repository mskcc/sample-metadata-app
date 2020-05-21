import os
import re
import concurrent.futures
import cx_Oracle
import requests
import yaml
from flask import json
from requests.adapters import HTTPAdapter
from urllib3 import PoolManager
import appconfigs.user_view_configs as grid_configs
from dbmodels.dbmodels import SampleData, UserViewConfig, AppLog
import ssl
from app import LOG

config = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../appconfigs/lims_user_config")
config_options = yaml.safe_load(open(config, "r"))
ENV = config_options['env']
USER = config_options['username']
PASSW = config_options['password']
if ENV == 'dev':
    LIMS_API_ROOT = config_options['lims_end_point_dev']
elif ENV == 'prod':
    LIMS_API_ROOT = config_options['lims_end_point_prod']
elif ENV == 'local':
    LIMS_API_ROOT = config_options['lims_end_point_local']

class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_SSLv23)


s = requests.Session()
s.mount('https://', MyAdapter())


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
    settings = grid_configs.settings
    user_view_config = UserViewConfig.query.filter_by(username=username).first()
    if user_view_config:
        hidden_columns = user_view_config.hidden_columns
        hidden_columns_values = hidden_columns.split(",") if hidden_columns else []
        hidden_column_arr = []
        for item in hidden_columns_values:
            hidden_column_arr.append(int(item))
        settings["hiddenColumns"]["columns"] = hidden_column_arr
    print(username, "view settings", settings)
    if role == 'clinical':
        return grid_configs.clinicalColHeaders, grid_configs.clinicalColumns, grid_configs.settings
    elif role == 'admin':
        return grid_configs.adminColHeaders, grid_configs.adminColumns, grid_configs.settings
    elif role == 'user':
        return grid_configs.nonClinicalColHeaders, grid_configs.nonClinicalColumns, grid_configs.settings


def get_crdb_connection(CRDB_UN, CRDB_PW, CRDB_URL):
    conn = cx_Oracle.connect(CRDB_UN, CRDB_PW, CRDB_URL)
    return conn


def get_fastq_data(igo_id):
    try:
        if not igo_id:
            return None
        url = "http://delphi.mskcc.org:8080/ngs-stats/rundone/fastqsbyigoid/" + igo_id
        request = requests.get(url)
        data = json.loads(request.content.decode("utf-8", "strict"))
        fastq_data = []
        for item in data:
            fastq_data.append(item.get("fastq"))
        return ",".join(fastq_data)
    except Exception as e:
        print("Error querying http://delphi.mskcc.org:8080/ngs-stats/rundone/fastqsbyigoid/{}: ".format(igo_id), repr(e))
        return None

def get_sample_status(igo_id):
    try:
        r = s.get(LIMS_API_ROOT + "/LimsRest/getSampleStatus?igoId={}".format(igo_id),
                  auth=(USER, PASSW), verify=False)
        data = r.content.decode("utf-8", "strict")
        return data
    except Exception as e:
        print("Error querying /LimsRest/getSampleStatus?igoId={} endpoint: ".format(igo_id), repr(e))
        return None

def create_sample_object(db_sample_data):
    status = get_sample_status(db_sample_data.igo_id)
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
        sample_status= status,
        lab_head=db_sample_data.lab_head,
        data_access=db_sample_data.data_access,
        do_not_use=str(bool(db_sample_data.do_not_use)).lower(),
        recipe=db_sample_data.recipe,
        bait_set=db_sample_data.bait_set,
        fastq_data=fastq
    )
    return sample_object


def get_sample_objects(db_results, **kwargs):
    sample_objects = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(create_sample_object, db_results))
        sample_objects.extend(list(results))
    if "application" in kwargs and kwargs.get("application") != 'None':
        sample_objects = list(filter(lambda x: x.recipe.lower() == kwargs.get("application").lower(), sample_objects))
    if "has_data" in kwargs:
        sample_objects = list(filter(lambda x: x.fastq_data, sample_objects))
    # if "is_published" in kwargs:
    #     sample_objects = list(filter(lambda x: x.fastq_data == "true", sample_objects))
    return sample_objects


def add_to_logs(message, user):
    """
    Method to important info messages to different logs.
    """
    print(message, "User: {}".format(user))
    AppLog.info(message=message, user=user)
    LOG.info(message + " User: {}".format(user))


def add_error_to_logs(message, user):
    """
    Method to important error messages to different logs.
    """
    print(message, "User: {}".format(user))
    AppLog.error(message=message, user=user)
    LOG.error(message + " User: {}".format(user))
