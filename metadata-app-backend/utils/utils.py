import re
import cx_Oracle
import requests
from flask import json
import appconfigs.user_view_configs as grid_configs
from dbmodels.dbmodels import SampleData


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


def get_column_configs(role):
    '''
    Method to return column configurations based on user role. Not all users are authorized to see all the data returned by this server.
    :param role:
    :return: column configurations
    '''
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
    if not igo_id:
        return None
    url = "http://delphi.mskcc.org:8080/ngs-stats/rundone/fastqsbyigoid/" + igo_id
    request = requests.get(url)
    data = json.loads(request.content.decode("utf-8", "strict"))
    fastq_data = []
    for item in data:
        fastq_data.append(item.get("fastq"))
    return ",".join(fastq_data)


def get_sample_objects(db_results):
    sample_objects = []
    for data in db_results:
        sample_data = SampleData(
            mrn=data.mrn,
            igo_id=data.igo_id,
            investigator_sample_id=data.investigator_sample_id,
            sample_type=data.sample_type,
            species=data.species,
            cmo_patient_id=data.cmo_patient_id,
            cmo_sample_id=data.cmo_sample_id,
            dmp_id=data.dmp_id,
            preservation=data.preservation,
            tumor_normal=data.tumor_normal,
            tissue_source=data.tissue_source,
            sample_origin=data.sample_origin,
            specimen_type=data.specimen_type,
            gender=data.gender,
            parent_tumor_type=data.parent_tumor_type,
            tumor_type=data.tumor_type,
            tissue_location=data.tissue_location,
            ancestor_sample=data.ancestor_sample,
            sample_status=data.sample_status,
            do_not_use=data.do_not_use,
            recipe=data.recipe,
            bait_set=data.bait_set,
            fastq_data=data.fastq_path
        )
        sample_objects.append(sample_data)
    return sample_objects
