from datetime import timedelta
import datetime
import time

from app import *


@app.route("/", methods=['GET', 'POST'])
def index():
    '''
    This method is here only to test at times if the app is working correctly.
    :return:
    '''
    log_entry = LOG.info("testing")
    AppLog.info(message="Testing the app.", user="api")
    # samples = db.session.query(Sample).filter(sa.not_(Sample.sample_status.like('%Failed%')), sa.not_(Sample.sampleid == '')).all()
    # samples = db.session.query(Sample).filter(sa.not_(Sample.sample_status.like('%Failed%'))).all()
    # samples = db.session.query(Sample).all()
    # return jsonify(totalrecords = len(samples))
    return jsonify(columnHeaders=gridconfigs.clinicalColHeaders, columns=gridconfigs.clinicalColumns,
                   settings=gridconfigs.settings), 200


def get_ldap_connection():
    conn = ldap.initialize(AUTH_LDAP_URL)
    conn.protocol_version = ldap.VERSION3
    conn.set_option(ldap.OPT_REFERRALS, 0)
    return conn


@app.route("/login", methods=['GET', 'POST'])
def login():
    '''
    Login user using ldap connection and validate user role.
    :return:
    '''
    if request.method == "POST":
        login_credentials = request.get_json(silent=True)
        username = login_credentials.get('username').split("@")[0]
        print(username)
        password = login_credentials.get('password')
        try:
            conn = get_ldap_connection()
            conn.simple_bind_s('%s@mskcc.org' % username, password)
            attrs = ['sAMAccountName', 'displayName', 'memberOf', 'title']
            result = conn.search_s(
                'DC=MSKCC,DC=ROOT,DC=MSKCC,DC=ORG',
                ldap.SCOPE_SUBTREE,
                'sAMAccountName=' + username,
                attrs,
            )
            role = 'user'
            user_fullname = ''
            user_groups = get_user_group(result)
            # check user role
            if len(set(user_groups).intersection(set(ADMIN_GROUPS))) > 0:
                role = 'admin'
            elif len(set(user_groups).intersection(set(CLINICAL_GROUPS))) > 0:
                role = 'clinical'
            conn.unbind_s()
            LOG.info("Successfully authenticated and logged {} into the app with role {}.".format(username, role))
            AppLog.info(message="Successfully authenticated and logged into the app.", user=username)
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)
            response = make_response(
                jsonify(
                    valid=True,
                    username=username,
                    role=role,
                    title="not found",
                    user_fullname=user_fullname,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    message="Login Successful"
                ),
                200, None)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        except ldap.INVALID_CREDENTIALS:
            response = make_response(
                jsonify(
                    valid=False,
                    username=None,
                    role=None,
                    title=None,
                    user_fullname=None,
                    access_token=None,
                    refresh_token=None,
                    message="Invalid username of password"
                ),
                200, None)
            response.headers.add('Access-Control-Allow-Origin', '*')
            AppLog.log(AppLog(level="WARNING", process="Root", user=username,
                              message="Invalid username or password."))
            AppLog.warning(message="Invalid username or password.", user=username)
            return make_response(response)
        except ldap.OPERATIONS_ERROR as e:
            response = make_response(
                jsonify(
                    valid=False,
                    username=None,
                    role=None,
                    title=None,
                    user_fullname=None,
                    access_token=None,
                    refresh_token=None,
                    message="Server error, try again later"
                ),
                200, None)
            response.headers.add('Access-Control-Allow-Origin', '*')
            AppLog.error(message="ldap OPERATION ERROR occured. {}".format(e), user=username)
            return make_response(response)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token) :
    '''
    Add JWT token to blacklist.
    :param decrypted_token:
    :return:
    '''
    jti = decrypted_token['jti']
    return jti in blacklist


@app.route('/logout', methods=['POST'])
@jwt_required
def logout():
    try:
        if request.method == "POST":
            user_data = request.get_json(silent=True)
            print(user_data)
            current_user = get_jwt_identity()
            jti = get_raw_jwt()['jti']
            blacklist.add(jti)
            AppLog.log(AppLog(level="INFO", process="Root", user=current_user,
                              message="Successfully logged out user " + current_user))
            response = make_response(
                jsonify(success=True,
                        username=None,
                        role=None,
                        title=None,
                        user_fullname=None,
                        access_token=None,
                        refresh_token=None,
                        message="Successfully logged out user {}".format(current_user)),
                200, None)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
    except Exception as e:
        AppLog.log(AppLog(level="ERROR",
                          process="Root",
                          user=current_user,
                          message="Error while logging out user {}: {}".format(current_user, repr(e))))
        response = make_response(
            jsonify(success=False,
                    message="Error while logging out user {}: {}".format(current_user, repr(e)),
                    error=repr(e)),
            200, None)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@app.route('/search', methods=['POST'])
@jwt_required
def search():
    try:
        if request.method == "POST":
            search_data = request.get_json(silent=True)
            current_user= get_jwt_identity()
            response = make_response(
                jsonify(success=True,
                        data="",
                        message=""
                        ),
                200, None)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
    except Exception as e:
        response = make_response(
            jsonify(success=False,
                    data="",
                    message="Search Error: {}".format(repr(e))
                    ),
            200, None)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        return e


@app.route("/get_metadata", methods=['GET', 'POST'])
def get_metadata():
    try:
        timestamp = None
        if request.args.get('timestamp') is not None:
            timestamp = request.args.get('timestamp')
        else:
            timestamp = time.mktime((datetime.datetime.today() - timedelta(
            days=1.1)).timetuple()) * 1000
        print(timestamp)
        r = s.get(LIMS_API_ROOT + "/LimsRest/getSampleMetadata?timestamp=" + str(int(timestamp)),
                  auth=(USER, PASSW), verify=False)
        data = r.content.decode("utf-8", "strict")
        print(data)
        return data
    except Exception as e:
        print(repr(e))
        return ""
