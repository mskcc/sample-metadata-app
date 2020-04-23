import traceback

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
def check_if_token_in_blacklist(decrypted_token):
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
            current_user = get_jwt_identity()
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
    """
    @:param timestamp
    Method to get 'Sample' metadata from LimsRest endpoint 'getSampleMetadata' using a 'timestamp' as parameter.
    If timestamp parameter passed is 'None' then this method generates a timestamp and passes to LimsRest endpoint.
    The end point returns metadata for all the child samples of a request where Request.status is 'Completed'
    and Request.DateCompleted greater than 'timestamp' passed as parameter to this endpoint.
    :return: List of SampleMetadata objects
    """
    try:
        # check if user has passed timestamp value in parameter if present then grab that value
        if request.args.get('timestamp') is not None:
            timestamp = request.args.get('timestamp')
        else:
            # if timestamp is not present generate one for 1.1 days in the past.
            timestamp = time.mktime((datetime.datetime.today() - timedelta(
                days=1.1)).timetuple()) * 1000
        print(timestamp)

        # query LimsRest endpoint
        r = s.get(LIMS_API_ROOT + "/LimsRest/getSampleMetadata?timestamp=" + str(int(timestamp)),
                  auth=(USER, PASSW), verify=False)
        data = r.content.decode("utf-8", "strict")

        # to record how many new Sample records were added to the database.
        ids = save_to_db(data)
        LOG.info("Added {} new records to the Metadata Database".format(ids))
        AppLog.info(message="Added {} new records to the Sample Metadata Database".format(ids), user="api")
        response = make_response(jsonify(data=(len(ids))), 200, None)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        print(e)
        AppLog.error(message=str(repr(e)), user='api')
        LOG.error(traceback.print_exc())
        response = make_response(jsonify(data="", error="There was a problem processing the request."), 200, None)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


def get_mrn(connection, cmo_id):
    """
    Method to get 'MRN' and 'DMP_ID' from CRDB
    :param connection
    :param cmo_id
    :returns MRN, DMP_ID
    """
    sql = """ 
          SELECT pt_mrn, dmp_id FROM crdb_cmo_dmp_map
          WHERE cmo_id = :p_cmo_id
          """
    # Allocate Cursor
    cursor = connection.cursor()
    cursor.execute(sql, p_cmo_id=cmo_id)
    mrn = None
    dmp_id = None
    for row in cursor:
        mrn, dmp_id = row
        # we need only first record. break loop after first iteration is done.
        break
    print("get mrn -> mrn and dmp_id: ", mrn, dmp_id)
    cursor.close()
    return mrn, dmp_id


def get_cmo_id_for_mrn(cmo_id):
    """
    Valid CMO ID's are in a general format of 'C-001717-P001-d' it is the second substring in the '001717' that is valid
    cmo_id for quering the CRDB database.
    @:param cmo_id
    :returns cmo_id_for_mrn
    """
    if cmo_id:
        print("get cmo id for mrn -> cmo_id: ", cmo_id)
        cmo_id_split = cmo_id.split("-")
        if len(cmo_id_split) > 1:
            cmo_id_for_mrn = cmo_id_split[1]
            print("get cmo id for mrn -> cmo_id_for_mrn: ", cmo_id_for_mrn)
            return cmo_id_for_mrn
    return None


def save_to_db(data):
    """
    Method to save data returned by LimsRest endpoint to the database.
    :param data
    """
    try:
        # open crdb connection and keep it open until all data is added to the db.
        connection = get_crdb_connection()
        data_to_json = json.loads(data)
        new_record_ids = []
        for item in data_to_json:
            igo_id = item.get('igoId');
            cmo_id = item.get("cmoSampleId")
            # extract value from cmo_id that is valid for CRDB query.
            # Valid CMO ID's are in a general format of 'C-001717-P001-d'
            # It is the second substring eg '001717' in the above CMO ID that is valid cmo_id for querying the CRDB for MRN.
            cmo_id_for_mrn = get_cmo_id_for_mrn(cmo_id)
            dmp_id = None
            mrn = None
            if cmo_id_for_mrn:
                mrn, dmp_id = get_mrn(connection, cmo_id_for_mrn)
            # check if sample record with igo_id already exists
            sample_record = Sample.query.filter_by(igo_id=igo_id).first()
            if not sample_record:
                # create new record if Sample record does not exist already.
                print("creating new sample record.")
                new_sample_record = Sample(
                    igo_id=item.get('igoId'),
                    investigator_sample_id=item.get("investigatorSampleId"),
                    sample_type=item.get("sampleType"),
                    species=item.get("species"),
                    preservation=item.get("preservation"),
                    tumor_normal=item.get("tumorOrNormal"),
                    tissue_source=item.get("tissueSource"),
                    sample_origin=item.get("sampleOrigin"),
                    specimen_type=item.get("specimenType"),
                    gender=item.get("sex"),
                    parent_tumor_type=item.get("parentTumorType"),
                    tumor_type=item.get("tumorType"),
                    tissue_location=item.get("tissueLocation"),
                    ancestor_sample=item.get("ancestorSample"),
                    sample_status=item.get("sampleStatus"),
                    do_not_use=item.get("doNotUse"),
                )
                db.session.add(new_sample_record)
                db.session.commit()
                new_record_ids.append(new_sample_record.id)  # update the new_record_ids list

                AppLog.info(
                    message="Added new Sample record with ID: {}".format(
                        new_sample_record.id),
                    user="api")
                # if mrn value is returned by CRDB, then also create new Patient record if not already exists.
                if mrn:
                    cmo_patient_id = item.get("cmoPatientId")
                    if not cmo_patient_id:
                        # if cmo_patient_id is not present in data then replace it with dmp_id returned by CRDB. dmp_id is DMP_PATIENTID.
                        cmo_patient_id = dmp_id
                        # check if Patient record exists
                    patient_rec = Patient.query.filter_by(mrn=mrn).first()
                    if not patient_rec:
                        # create new Patient record
                        print("creating new patient record.")
                        new_patient_record = Patient(
                            mrn=mrn,
                            cmo_patient_id=cmo_patient_id,
                            cmo_sample_id=cmo_id,
                        )
                        # Link Patient record to Sample record.
                        new_sample_record.patient = new_patient_record
                        db.session.add(new_patient_record)
                        db.session.commit()
                        AppLog.info(
                            message="Added new Cvrdata record with ID: {}".format(
                                new_patient_record.id),
                            user="api")
                    else:
                        new_sample_record.patient=patient_rec
                        db.session.commit()
                recipe = item.get("recipe")
                # if recipe value is present on data create new Assay record if required.
                if recipe:
                    print("creating new assay record")
                    new_assay_record = Assay(
                        id_sample=igo_id,
                        recipe=recipe,
                        bait_set=item.get("baitset"),
                        sample=new_sample_record
                    )
                    db.session.add(new_assay_record)
                    db.session.commit()
                    AppLog.info(
                        message="Added new Sample record with  ID: {}".format(new_assay_record.id),
                        user="api")
            # If sample record with igo_id already exists update Sample record and related Records.
            elif sample_record:
                update_record(sample_record, item, connection)
        connection.close()
        return new_record_ids  # return list of new Sample record ids created and saved to db
    except Exception as e:
        print(e)
        AppLog.error(message=str(repr(e)), user='api')
        LOG.error(e, exc_info=True)


def update_record(sample_record, item, connection):
    """:param
    """
    try:
        print("started updating Sample record")
        cmo_id_for_mrn = get_cmo_id_for_mrn(item.get("cmoSampleId"))
        print("update record -> cmo_id_for_mrn: ", cmo_id_for_mrn)
        dmp_id = None
        mrn = None
        if cmo_id_for_mrn:
            print("updating sample record.")
            mrn, dmp_id = get_mrn(connection, cmo_id_for_mrn)
            sample_record.investigator_sample_id = item.get("investigatorSampleId")
            sample_record.sample_type = item.get("sampleType")
            sample_record.species = item.get("species")
            sample_record.preservation = item.get("preservation")
            sample_record.tumor_normal = item.get("tumorOrNormal")
            sample_record.tissue_source = item.get("tissueSource")
            sample_record.sample_origin = item.get("sampleOrigin")
            sample_record.specimen_type = item.get("specimenType")
            sample_record.gender = item.get("sex")
            sample_record.parent_tumor_type = item.get("parentTumorType")
            sample_record.tumor_type = item.get("tumorType")
            sample_record.tissue_location = item.get("tissueLocation")
            sample_record.ancestor_sample = item.get("ancestorSample")
            sample_record.sample_status = item.get("sampleStatus")
            sample_record.date_updated = datetime.datetime.now()
            sample_record.updated_by = "api"
            db.session.commit()
            AppLog.info(message="Update Sample record with ID: {}".format(sample_record.id),
                        user="api")
        # find and update the Patient record.
        if mrn:
            print("mrn true:", mrn)
            patient_record = Patient.query.filter_by(mrn=mrn).first()
            print(patient_record)
            if patient_record:
                print("Updating existing patient record", patient_record)
                if item.get("cmoPatientId"):
                    patient_record.cmo_patient_id = item.get("cmoPatientId")
                elif dmp_id:
                    patient_record.cmo_patient_id = dmp_id
                patient_record.cmo_sample_id = item.get("cmoSampleId")
                patient_record.date_updated = datetime.datetime.now()
                patient_record.updated_by = "api"
                db.session.commit()
                AppLog.info(message="Updated Patient record with ID: {}".format(patient_record.id),
                            user="api")

            else:
                print("creating new Patient record")
                new_patient_record = Patient(
                    mrn=mrn,
                    cmo_patient_id=item.get("cmoPatientId") if item.get("cmoPatientId") else dmp_id,
                    cmo_sample_id=item.get("cmoSampleId"),
                )
                sample_record.patient = new_patient_record
                db.session.add(new_patient_record)
                db.session.commit()
                AppLog.info(message="Added new Patient record with ID: {}".format(new_patient_record.id),
                            user="api")

        assay_record = Assay.query.filter_by(id_sample=sample_record.id).first()
        if assay_record:
            print("updating assay record")
            assay_record.recipe = item.get("recipe")
            assay_record.bait_set = item.get("baitset")
            assay_record.date_updated = datetime.datetime.now()
            assay_record.updated_by = "api"
            db.session.commit()
            AppLog.info(message="Updated Assay record with ID: {}".format(assay_record.id),
                        user="api")
        else:
            print("creating new assay record")
            new_assay_record = Assay(
                recipe=item.get("recipe"),
                bait_set=item.get("baitset"),
                sample=sample_record
            )
            db.session.add(new_assay_record)
            db.session.commit()
            AppLog.info(message="Created new Assay record with ID: {}".format(new_assay_record.id),
                        user="api")

    except Exception as e:
        print(e)
        AppLog.error(message=str(repr(e)), user='api')
        LOG.error(e, exc_info=True)
