import datetime
import os
from datetime import timedelta
import time
from flask import json
import requests
import sqlalchemy as sa
import logging as LOG
import ldap
import yaml
from flask_cors import CORS
from flask import Flask
from flask_caching import Cache
from flask import request, make_response, jsonify, send_from_directory
from flask_jwt_extended import (
    JWTManager, jwt_required, get_jwt_identity,
    create_access_token, create_refresh_token,
    jwt_refresh_token_required, get_raw_jwt
)
from flask_migrate import Migrate
from flask import Flask
from dbmodels.dbmodels import db, Sample, Patient, Assay, Baitset, AppLog
import appconfigs.user_view_configs as gridconfigs
from utils.utils import get_user_title, get_user_group, get_user_fullname, get_crdb_connection
from flask_caching import Cache
app = Flask(__name__)

###################################### register blueprints ##########################################
from outbound_api.outbound_api import outbound_api

app.register_blueprint(outbound_api, url_prefix="/api")

from outbound_api.outbound_api import SWAGGER_URL, SWAGGERUI_BLUEPRINT

app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
#print(SWAGGER_URL, SWAGGERUI_BLUEPRINT)
####################################### app configuration settings ###################################

config = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../appconfigs/lims_user_config")
print(config)
config_options = yaml.safe_load(open(config, "r"))
USER = config_options['username']
PASSW = config_options['password']
ENV = config_options['env']
PORT = config_options['port_dev']

LIMS_API_ROOT = config_options['lims_end_point_dev']

CRDB_UN = config_options['crdb_un']
CRDB_PW = config_options['crdb_pw']
CRDB_URL = config_options['crdb_url']

if ENV == 'dev':
    PORT = config_options['port_dev']
    LIMS_API_ROOT = config_options['lims_end_point_dev']
    app.config['SQLALCHEMY_DATABASE_URI'] = config_options['db_uri_dev']
elif ENV == 'prod':
    PORT = config_options['port_prod']
    LIMS_API_ROOT = config_options['lims_end_point_prod']
    app.config['SQLALCHEMY_DATABASE_URI'] = config_options['db_uri_prod']
elif ENV == 'local':
    PORT = config_options['port_dev']
    LIMS_API_ROOT = config_options['lims_end_point_local']
    app.config['SQLALCHEMY_DATABASE_URI'] = config_options['db_uri_local']

# print(PORT)
# print(LIMS_API_ROOT)
print(app.config['SQLALCHEMY_DATABASE_URI'])
AUTH_LDAP_URL = config_options['auth_ldap_url']
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

###################################### JWT TOKENS ###################################################
app.config['JWT_SECRET_KEY'] = config_options['secret_key']  # Change this!
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
jwt = JWTManager(app)

blacklist = set()

###################################### CACHING SETTINGS #########################################################cache = Cache(app, config=config_options['cache_config_prod'])

cache = Cache(app, config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': '../cache'})

###################################### CORS #########################################################

CORS(app)

#################################### APP CONSTANTS ###################################################

# ADMIN_GROUPS = ['AHDHD'] # add another admin group from PM's when available
ADMIN_GROUPS = ['zzPDL_SKI_IGO_DATA', 'GRP_SKI_CMO_WESRecapture']
CLINICAL_GROUPS = ['GRP_SKI_CMO_WESRecapture_Clinical']

##################################### Logging settings ###############################################
log_file_path = ''
if ENV == 'local':
    log_file_path = config_options['log_file_local']
elif ENV == 'prod' or ENV == 'dev':
    log_file_path = config_options['log_file_prod']

LOG.basicConfig(level=LOG.INFO,
                filename=log_file_path.format(datetime.datetime.now().date()),
                format='%(asctime)s  %(levelname)-10s %(processName)s  %(name)s %(message)s')

##################################### DB Initialization###############################################

with app.app_context():
    db.init_app(app)
    db.create_all()
