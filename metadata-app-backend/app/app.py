import re
import traceback

# import uwsgi as uwsgi

from app import *
from dbmodels.dbmodels import UserViewConfig
from utils.utils import get_column_configs, get_sample_objects, s, add_to_logs, add_error_to_logs, \
    add_error_to_db_logs, create_cache_key, cache_data, get_cached_data


@app.route("/", methods=['GET', 'POST'])
def index():
    """
    This method is here only to test at times if the app is working correctly.
    :return:
    """
    add_to_logs("Testing the app.", user="api")
    return jsonify(columnHeaders=gridconfigs.clinicalColHeaders, columns=gridconfigs.clinicalColumns,
                   settings=gridconfigs.settings), 200


def get_lims_recipes():
    """
    Method to get recipe list from LIMS to populate recipe selection field on front end.
    :return
    """
    try:
        recipes = db.session.query(Assay.recipe).distinct().all()
        print("returning distinct recipes", recipes)
        LOG.info("returning distinct recipes: {}".format(recipes))
        return recipes
    except Exception:
        LOG.error("Error while reading distinct recipes form db table 'Assay':\n{}".format(traceback.print_exc()))
        return []


def get_ldap_connection():
    """
    Method to get ldap connection to validate user credentials.
    :return
    """
    conn = ldap.initialize(AUTH_LDAP_URL)
    conn.protocol_version = ldap.VERSION3
    conn.set_option(ldap.OPT_REFERRALS, 0)
    return conn


@app.route("/login", methods=['GET', 'POST'])
def login():
    """
    Login user using ldap connection and validate user role.
    :return:
    """
    if request.method == "POST":
        login_credentials = request.get_json(silent=True)
        username = login_credentials.get('username').split("@")[0]
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
            user_fullname = ''  # this variable works on dev side but fails on the production hence marked as
            # not found for time being.
            user_groups = get_user_group(result)
            # check user role
            if len(set(user_groups).intersection(set(ADMIN_GROUPS))) > 0:
                role = 'admin'
            elif len(set(user_groups).intersection(set(CLINICAL_GROUPS))) > 0:
                role = 'clinical'
            conn.unbind_s()
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)
            recipe_list = get_lims_recipes()
            response = make_response(
                jsonify(
                    success=True,
                    username=username,
                    role=role,
                    title="not found",  # this variable works on dev side but fails on the production hence marked as
                    # not found for time being.
                    user_fullname=user_fullname,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    recipes=recipe_list,
                    message="Successfully logged in {}".format(username)
                ),
                200, None)
            response.headers.add('Access-Control-Allow-Origin', '*')
            message = "Successfully authenticated and logged {} into the app with role {}.".format(username, role)
            add_to_logs(message, username)
            return response
        except ldap.INVALID_CREDENTIALS:
            response = make_response(
                jsonify(
                    success=False,
                    username=None,
                    role=None,
                    title=None,
                    user_fullname=None,
                    access_token=None,
                    refresh_token=None,
                    recipes=None,
                    error=True,
                    message="Invalid username or password"
                ),
                200, None)
            response.headers.add('Access-Control-Allow-Origin', '*')
            message = "Invalid username or password."
            add_error_to_db_logs(message, username)
            return make_response(response)
        except ldap.OPERATIONS_ERROR as e:
            response = make_response(
                jsonify(
                    success=False,
                    username=None,
                    role=None,
                    title=None,
                    user_fullname=None,
                    access_token=None,
                    refresh_token=None,
                    message="Server error, try again later"
                ),
                500, None)
            response.headers.add('Access-Control-Allow-Origin', '*')
            message = "ldap OPERATION ERROR occured. {}".format(traceback.print_exc())
            add_error_to_logs(message, username)
            return make_response(response)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    """
    Add JWT token to blacklist.
    :param decrypted_token:
    :return:
    """
    jti = decrypted_token['jti']
    return jti in blacklist


@app.route('/logout', methods=['POST'])
@jwt_required
def logout():
    """
    To log out user and also to end user session.
    :return
    """
    current_user = None
    try:
        if request.method == "POST":
            user_data = request.get_json(silent=True)
            current_user = get_jwt_identity()
            jti = get_raw_jwt()['jti']
            blacklist.add(jti)
            add_to_logs("Successfully logged out user ", current_user)
            response = make_response(
                jsonify(
                    success=True,
                    username=None,
                    role=None,
                    title=None,
                    user_fullname=None,
                    access_token=None,
                    refresh_token=None,
                    recipes=None,
                    message="Successfully logged out user {}".format(current_user)),
                200, None)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
    except Exception as e:
        mesage = "Error while logging out user {}: {}".format(current_user, traceback.print_exc())
        add_error_to_logs(mesage, current_user)
        response = make_response(
            jsonify(
                success=False,
                message="Error while logging out user {}: {}".format(current_user, traceback.print_exc()),
                error=True),
            401, None)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@app.route("/get_metadata", methods=['GET', 'POST'])
def get_metadata():
    """
    @:param timestamp
    @:param projectId
    Method to get 'Sample' metadata from LimsRest endpoint 'getSampleMetadata' using a 'timestamp' and/or 'projectId'
    as parameter. If timestamp parameter passed is 'None' then this method generates a timestamp and passes to LimsRest
    endpoint. The end point returns metadata for all the child samples of a request created after the given timestamp.
    :return: List of SampleMetadata objects
    """
    try:
        # check if user has passed timestamp value in parameter if present then grab that value
        timestamp = None
        project_id = request.args.get("projectId")
        if request.args.get('timestamp') is not None:
            timestamp = request.args.get('timestamp')
        else:
            # if timestamp is not present generate one current time minus 1.1 days.
            timestamp = time.mktime((datetime.datetime.today() - timedelta(
                days=1.1)).timetuple()) * 1000
        print("timestamp: ", timestamp)
        print("projectid: ", project_id)
        r = None
        if timestamp and project_id:
            r = s.get(
                LIMS_API_ROOT + "/LimsRest/getSampleMetadata?timestamp=" + str(timestamp) + "&projectId=" + project_id,
                auth=(USER, PASSW), verify=False)
            print("LimsRest endpoint url: ", r.url)
        else:
            r = s.get(LIMS_API_ROOT + "/LimsRest/getSampleMetadata?timestamp=" + str(timestamp), auth=(USER, PASSW),
                      verify=False)
            print("LimsRest endpoint url: ", r.url)
        data = r.content.decode("utf-8", "strict")
        # to record how many new Sample records were added to the database.
        ids = save_to_db(data)
        add_to_logs("Added {} new records to the Metadata Database".format(ids), "api")
        response = make_response(jsonify(data=(len(ids))), 200, None)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        message = "Error {}".format(traceback.print_exc())
        add_error_to_logs(message, "api")
        response = make_response(jsonify(data="", error="There was a problem processing the request."), 500, None)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


def get_mrn(connection, cmo_id):
    """
    Method to get 'MRN' and 'DMP_ID' from CRDB
    :param connection
    :param cmo_id
    :returns MRN, DMP_ID
    """
    try:
        sql = """ 
              SELECT pt_mrn, dmp_id FROM crdb_cmo_loj_dmp_map
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
        add_to_logs("get mrn -> mrn and dmp_id: {}, {}".format(mrn, dmp_id), "api")
        cursor.close()
        return mrn, dmp_id
    except Exception as e:
        print(traceback.print_exc())
        add_error_to_logs("Error: CRDB query failed. {}".format(traceback.print_exc()), "api")
        return None, None


def get_cmo_id_for_mrn(cmo_id):
    """
    Valid CMO ID's are in a general format of 'C-001717-P001-d' it is the second substring in the '001717' that is valid
    cmo_id for quering the CRDB database.
    @:param cmo_id
    :returns cmo_id_for_mrn
    """
    try:
        if cmo_id:
            add_to_logs("get cmo id for mrn -> cmo_id: {}".format(cmo_id), "api")
            cmo_id_split = cmo_id.split("-")
            if len(cmo_id_split) > 1:
                cmo_id_for_mrn = cmo_id_split[1]
                return cmo_id_for_mrn
        return None
    except Exception as e:
        add_error_to_logs("Error: {}".format(traceback.print_exc()), "api")
        return None


def save_to_db(data):
    """
    Method to save data returned by LimsRest endpoint to the database.
    :param data
    """
    try:
        # open crdb connection and keep it open until all data is added to the db.
        connection = get_crdb_connection(CRDB_UN, CRDB_PW, CRDB_URL)
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
                    sex=item.get("sex"),
                    parent_tumor_type=item.get("parentTumorType"),
                    tumor_type=item.get("tumorType"),
                    tissue_location=item.get("tissueLocation"),
                    ancestor_sample=item.get("ancestorSample"),
                    #sample_status=item.get("sampleStatus"),
                    lab_head=item.get("principalInvestigator"),
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
                        cmo_patient_id = dmp_id if dmp_id else ""
                        # check if Patient record exists
                    patient_rec = Patient.query.filter_by(mrn=mrn).first()
                    if not patient_rec:
                        # create new Patient record
                        print("mrn {}, dmpid {}".format(mrn, dmp_id))
                        new_patient_record = Patient(
                            mrn=mrn,
                            cmo_patient_id=cmo_patient_id,
                            cmo_sample_id=cmo_id,
                            dmp_id=dmp_id,
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
                        new_sample_record.patient = patient_rec
                        db.session.commit()

                recipe = item.get("recipe")
                assay = Assay.query.filter_by(recipe=recipe).first()
                # if recipe value is present on data create new Assay record if required.
                if recipe != "":
                    if not assay:
                        new_assay_record = Assay(
                            recipe=recipe,
                        )
                        new_sample_record.sample_assay = new_assay_record
                        db.session.commit()
                        add_to_logs("Added new Assay record with  ID: {}".format(new_assay_record.id), "api")
                    else:
                        new_sample_record.sample_assay = assay
                        db.session.commit()
                        add_to_logs("Added new Sample record with  ID: {}".format(new_sample_record.id), "api")

                baits = item.get("baitset")
                print("baitset:", baits)
                if baits != "":
                    baitset = Baitset.query.filter_by(bait_set=baits).first()
                    # if baitset value is present on data create new Assay record if required.
                    if not baitset and baits and baits != "":
                        new_baitset_record = Baitset(
                            bait_set=baits,
                        )
                        new_sample_record.sample_baitset = new_baitset_record
                        db.session.commit()
                        add_to_logs("Added new Baitset record with  ID: {}".format(new_baitset_record.id), "api")
                    else:
                        new_sample_record.sample_baitset = baitset
                        db.session.commit()
                        add_to_logs("Added new Sample record with  ID: {}".format(new_sample_record.id), "api")
            elif sample_record:
                update_record(sample_record, item, connection)
        connection.close()
        return new_record_ids  # return list of new Sample record ids created and saved to db
    except Exception:
        print(traceback.print_exc())
        add_error_to_logs("Error: while saving new records to db: {}".format(traceback.print_exc()), "api")


def update_record(sample_record, item, connection):
    """:param
    """
    try:
        cmo_id_for_mrn = get_cmo_id_for_mrn(item.get("cmoSampleId"))
        dmp_id = None
        mrn = None
        if cmo_id_for_mrn:
            mrn, dmp_id = get_mrn(connection, cmo_id_for_mrn)
            sample_record.investigator_sample_id = item.get("investigatorSampleId")
            sample_record.sample_type = item.get("sampleType")
            sample_record.species = item.get("species")
            sample_record.preservation = item.get("preservation")
            sample_record.tumor_normal = item.get("tumorOrNormal")
            sample_record.tissue_source = item.get("tissueSource")
            sample_record.sample_origin = item.get("sampleOrigin")
            sample_record.specimen_type = item.get("specimenType")
            sample_record.sex = item.get("sex")
            sample_record.parent_tumor_type = item.get("parentTumorType")
            sample_record.tumor_type = item.get("tumorType")
            sample_record.tissue_location = item.get("tissueLocation")
            sample_record.ancestor_sample = item.get("ancestorSample")
            #sample_record.sample_status = item.get("sampleStatus")
            sample_record.date_updated = datetime.datetime.now()
            sample_record.updated_by = "api"
            db.session.commit()
            add_to_logs("Update Sample record with ID: {}".format(sample_record.id), "api")
        # find and update the Patient record.
        if mrn:
            patient_record = Patient.query.filter_by(mrn=mrn).first()
            if patient_record:
                if item.get("cmoPatientId"):
                    patient_record.cmo_patient_id = item.get("cmoPatientId")
                elif dmp_id:
                    patient_record.cmo_patient_id = dmp_id if dmp_id else ""
                patient_record.cmo_sample_id = item.get("cmoSampleId")
                patient_record.dmp_id = dmp_id
                patient_record.date_updated = datetime.datetime.now()
                patient_record.updated_by = "api"
                db.session.commit()
                add_to_logs("Updated Patient record with ID: {}".format(patient_record.id), "api")

            else:
                new_patient_record = Patient(
                    mrn=mrn,
                    cmo_patient_id=item.get("cmoPatientId") if item.get("cmoPatientId") else dmp_id,
                    cmo_sample_id=item.get("cmoSampleId"),
                    dmp_id=dmp_id
                )
                sample_record.patient = new_patient_record
                db.session.add(new_patient_record)
                db.session.commit()
                add_to_logs("Added new Patient record with ID: {}".format(new_patient_record.id), "api")

        # update the assay record
        #check if sample assay record exists.
        assay_record = sample_record.sample_assay
        # if assay recipe and updated data recipe match then skip
        print("item recipe", item.get("recipe"), "assay_recipe", item.get("recipe"))
        if assay_record and assay_record.recipe == item.get("recipe"):
            pass
        # if assay recipe and updated recipe does not match then it needs to be updated
        if assay_record and assay_record.recipe != item.get("recipe"):
            # if updated data recipe exist, then update it on sample
            assay_record_new_recipe = Assay.query.filter(recipe=item.get("recipe"))
            if assay_record_new_recipe:
                sample_record.sample_assay = assay_record_new_recipe
                db.session.commit()
                add_to_logs("Updated Assay for Sample with ID: {}".format(sample_record.id), "api")
            # if updated data recipe does not exist in db, then created new assay and update on sampif not assay_record_new_recipe:
                new_assay_record = Assay(
                    recipe=item.get("recipe"),
                    sample=sample_record
                )
                sample_record.sample_assay = new_assay_record
                db.session.commit()
                add_to_logs("Created new Assay record with ID: {}".format(new_assay_record.id), "api")

        baits = item.get("baitset")

        # update the Baitset record
        # check if sample Baitset record exists.
        baitset = sample_record.sample_baitset

        # if baitset value is not present on Sample, create new Baitset record and add to Sample.
        if not baitset and baits and baits != "":
            new_baitset_record = Baitset(
                bait_set=baits,
            )
            sample_record.sample_baitset = new_baitset_record
            db.session.commit()
            add_to_logs("Updated Sample with ID {}, Added new Baitset record with  ID: {}".format(sample_record.id, new_baitset_record.id), "api")

        # if baitset value in lims changed since last import, check if there is Baitset record with new value in db,
        # and update sample. If there are no Baitset records with new value in db, then create new Baitset record and
        # update sample record.
        if baitset and baits and baits != "" and baits != baitset.bait_set:
            matching_baitset_rec = Baitset.query.filter_by(bait_set=baits).first()
            if matching_baitset_rec:
                sample_record.sample_baitset = matching_baitset_rec
            else:
                new_baitset_record = Baitset(
                    bait_set=baits,
                )
                sample_record.sample_baitset = new_baitset_record
                db.session.commit()
                add_to_logs("Updated Sample with ID {}, Updated Sample Baitset  record with ID: {}".format(sample_record.id,
                                                                                                      baitset.id),
                            "api")
    except Exception:
        message = "Error: while updating Sample records: {}".format(traceback.print_exc())
        print(message)
        add_error_to_logs(message, "api")


@app.route('/search', methods=['POST'])
@jwt_required
def search():
    global sample_objects
    try:
        if request.method == "POST":
            search_data = request.get_json(silent=True)
            print(search_data)
            search_keywords = search_data.get("search_keywords")
            search_type = search_data.get("search_type")
            exact_match = search_data.get("exact_match")
            application = search_data.get("application")
            has_data = search_data.get("has_data")
            user_role = search_data.get("user_role")
            current_user = get_jwt_identity()
            col_headers, column_defs, settings = get_column_configs(user_role, current_user)
            print(settings)
            cache_key = create_cache_key(search_keywords, search_type, exact_match, application, has_data)
            cached_response = get_cached_data(cache_key)
            print("cached response", cached_response)
            if cached_response:
                add_to_logs("Returning response from cache:\n{}".format(cached_response), "api")
                return cached_response
            # log search event in AppLog table.
            add_to_logs("User data search using parameters: {}.".format(search_data), user=current_user)
            # create empty response object.
            response = make_response(jsonify(
                data=[], col_headers=col_headers, column_defs=column_defs,
                settings=settings, success=True, error=False), 200, None)
            kwargs = {}  # initialize kwargs for filtering
            if application:
                kwargs["application"] = application
            if has_data:
                kwargs["has_data"] = has_data
            ## search for mrn's
            if search_keywords and search_type == "mrn":
                search_keywords = [x.strip() for x in re.split(r'[,\s\n]\s*', search_keywords)]
                db_results = db.session.query(Patient) \
                    .outerjoin(Sample, Patient.mrn == Sample.mrn) \
                    .outerjoin(Assay, Sample.assay == Assay.id) \
                    .outerjoin(Baitset, Sample.baitset == Baitset.id) \
                    .add_columns(Sample.id, Sample.mrn, Sample.igo_id, Sample.investigator_sample_id,
                                 Sample.sample_type,
                                 Sample.species, Patient.cmo_patient_id, Patient.cmo_sample_id, Patient.dmp_id,
                                 Sample.preservation, Sample.tumor_normal, Sample.tissue_source, Sample.sample_origin,
                                 Sample.specimen_type, Sample.sex, Sample.parent_tumor_type, Sample.tumor_type,
                                 Sample.tissue_location, Sample.ancestor_sample, Sample.lab_head,
                                 Sample.data_access, Sample.do_not_use, Assay.recipe, Baitset.bait_set) \
                    .filter(Sample.mrn.in_(search_keywords)).all()
                sample_objects = get_sample_objects(db_results, **kwargs)
                response = make_response(jsonify(
                    data=(json.dumps([r.__dict__ for r in sample_objects], sort_keys=True,
                                     indent=4,
                                     separators=(',', ': '))), col_headers=col_headers, column_defs=column_defs,
                    settings=settings, success=True, error=False), 200, None)

            ## search for tumor type with exact match for search_keywords.
            elif search_keywords and search_type == "tumor type" and exact_match:
                search_keywords = [x.strip() for x in re.split(r'[,\n]', search_keywords)]
                db_results = db.session.query(Sample) \
                    .outerjoin(Patient, Patient.mrn == Sample.mrn) \
                    .outerjoin(Assay, Sample.assay == Assay.id) \
                    .outerjoin(Baitset, Sample.baitset == Baitset.id) \
                    .add_columns(Sample.id, Sample.mrn, Sample.igo_id, Sample.investigator_sample_id,
                                 Sample.sample_type,
                                 Sample.species, Patient.cmo_patient_id, Patient.cmo_sample_id, Patient.dmp_id,
                                 Sample.preservation, Sample.tumor_normal, Sample.tissue_source, Sample.sample_origin,
                                 Sample.specimen_type, Sample.sex, Sample.parent_tumor_type, Sample.tumor_type,
                                 Sample.tissue_location, Sample.ancestor_sample, Sample.lab_head,
                                 Sample.data_access, Sample.do_not_use, Assay.recipe, Baitset.bait_set) \
                    .filter(Sample.parent_tumor_type.in_(search_keywords)).all()
                print("db search complete. returned {} objects".format(len(db_results)))
                sample_objects = get_sample_objects(db_results, **kwargs)
                response = make_response(jsonify(
                    data=(json.dumps([r.__dict__ for r in sample_objects], sort_keys=True,
                                     indent=4,
                                     separators=(',', ': '))), col_headers=col_headers, column_defs=column_defs,
                    settings=settings, success=True, error=False), 200, None)

            ## search for tumor type that is like %search_keywords%.
            elif search_keywords and search_type == "tumor type" and not exact_match:
                search_keywords = ["%{}%".format(x.strip()) for x in re.split(r'[,\n]', search_keywords)]
                print(search_keywords)
                db_results = db.session.query(Sample) \
                    .outerjoin(Patient, Patient.mrn == Sample.mrn) \
                    .outerjoin(Assay, Sample.assay == Assay.id) \
                    .outerjoin(Baitset, Sample.baitset == Baitset.id) \
                    .add_columns(Sample.id, Sample.mrn, Sample.igo_id, Sample.investigator_sample_id,
                                 Sample.sample_type,
                                 Sample.species, Patient.cmo_patient_id, Patient.cmo_sample_id, Patient.dmp_id,
                                 Sample.preservation, Sample.tumor_normal, Sample.tissue_source, Sample.sample_origin,
                                 Sample.specimen_type, Sample.sex, Sample.parent_tumor_type, Sample.tumor_type,
                                 Sample.tissue_location, Sample.ancestor_sample, Sample.lab_head,
                                 Sample.data_access, Sample.do_not_use, Assay.recipe, Baitset.bait_set) \
                    .filter(Sample.parent_tumor_type.like(search_keywords[0])).all()
                print("db search complete. returned {} objects".format(len(db_results)))
                sample_objects = get_sample_objects(db_results, **kwargs)
                # apply additional filtering like has_data and is_published
                response = make_response(jsonify(
                    data=(json.dumps([r.__dict__ for r in sample_objects], sort_keys=True,
                                     indent=4,
                                     separators=(',', ': '))), col_headers=col_headers, column_defs=column_defs,
                    settings=settings, success=True, error=False), 200, None)

            ## search db using patient id.
            elif search_keywords and search_type == "patient id":
                search_keywords = [x.strip() for x in re.split(r'[,\s\n]\s*', search_keywords)]
                db_results = db.session.query(Patient) \
                    .outerjoin(Sample, Patient.mrn == Sample.mrn) \
                    .outerjoin(Assay, Sample.assay == Assay.id) \
                    .outerjoin(Baitset, Sample.baitset == Baitset.id) \
                    .add_columns(Sample.id, Sample.mrn, Sample.igo_id, Sample.investigator_sample_id,
                                 Sample.sample_type,
                                 Sample.species, Patient.cmo_patient_id, Patient.cmo_sample_id, Patient.dmp_id,
                                 Sample.preservation, Sample.tumor_normal, Sample.tissue_source, Sample.sample_origin,
                                 Sample.specimen_type, Sample.sex, Sample.parent_tumor_type, Sample.tumor_type,
                                 Sample.tissue_location, Sample.ancestor_sample, Sample.lab_head,
                                 Sample.data_access, Sample.do_not_use, Assay.recipe, Baitset.bait_set) \
                    .filter(Patient.cmo_patient_id.in_(search_keywords)).all()
                # apply additional filtering like has_data and is_published
                sample_objects = get_sample_objects(db_results, **kwargs)
                response = make_response(jsonify(
                    data=(json.dumps([r.__dict__ for r in sample_objects], sort_keys=True,
                                     indent=4,
                                     separators=(',', ': '))), col_headers=col_headers, column_defs=column_defs,
                    settings=settings, success=True, error=False), 200, None)
            ## search db using igo id
            elif search_keywords and search_type == "igo id":
                search_keywords = [x.strip() for x in re.split(r'[,\s\n]\s*', search_keywords)]
                db_results = db.session.query(Sample) \
                    .outerjoin(Patient, Patient.mrn == Sample.mrn) \
                    .outerjoin(Assay, Sample.assay == Assay.id) \
                    .outerjoin(Baitset, Sample.baitset == Baitset.id) \
                    .add_columns(Sample.id, Sample.mrn, Sample.igo_id, Sample.investigator_sample_id,
                                 Sample.sample_type,
                                 Sample.species, Patient.cmo_patient_id, Patient.cmo_sample_id, Patient.dmp_id,
                                 Sample.preservation, Sample.tumor_normal, Sample.tissue_source, Sample.sample_origin,
                                 Sample.specimen_type, Sample.sex, Sample.parent_tumor_type, Sample.tumor_type,
                                 Sample.tissue_location, Sample.ancestor_sample, Sample.lab_head,
                                 Sample.data_access, Sample.do_not_use, Assay.recipe, Baitset.bait_set) \
                    .filter(Sample.igo_id.in_(search_keywords)).all()
                # apply additional filtering like has_data and is_published
                sample_objects = get_sample_objects(db_results, **kwargs)
                response = make_response(jsonify(
                    data=(json.dumps([r.__dict__ for r in sample_objects], sort_keys=True,
                                     indent=4,
                                     separators=(',', ': '))), col_headers=col_headers, column_defs=column_defs,
                    settings=settings, success=True, error=False), 200, None)

            ## search db using cmo id
            elif search_keywords and search_type == "cmo id":
                search_keywords = [x.strip() for x in re.split(r'[,\s\n]\s*', search_keywords)]
                db_results = db.session.query(Patient) \
                    .outerjoin(Sample, Patient.mrn == Sample.mrn) \
                    .outerjoin(Assay, Sample.assay == Assay.id) \
                    .outerjoin(Baitset, Sample.baitset == Baitset.id) \
                    .add_columns(Sample.id, Sample.mrn, Sample.igo_id, Sample.investigator_sample_id,
                                 Sample.sample_type,
                                 Sample.species, Patient.cmo_patient_id, Patient.cmo_sample_id, Patient.dmp_id,
                                 Sample.preservation, Sample.tumor_normal, Sample.tissue_source, Sample.sample_origin,
                                 Sample.specimen_type, Sample.sex, Sample.parent_tumor_type, Sample.tumor_type,
                                 Sample.tissue_location, Sample.ancestor_sample, Sample.lab_head,
                                 Sample.data_access, Sample.do_not_use, Assay.recipe, Baitset.bait_set) \
                    .filter(Patient.cmo_sample_id.in_(search_keywords)).all()
                # apply additional filtering like has_data and is_published
                sample_objects = get_sample_objects(db_results, **kwargs)
                response = make_response(jsonify(
                    data=(json.dumps([r.__dict__ for r in sample_objects], sort_keys=True,
                                     indent=4,
                                     separators=(',', ': '))), col_headers=col_headers, column_defs=column_defs,
                    settings=settings, success=True, error=False), 200, None)
            response.headers.add('Access-Control-Allow-Origin', '*')
            # cache response
            add_to_logs("Saving response data to cache.\n{}".format(response), "api")
            cache.set
            return response

    except Exception:
        print(traceback.print_exc())
        message = "Error while executing search query.: {}".format(traceback.print_exc())
        add_error_to_logs(message, "api")
        response = make_response(
            jsonify(success=False,
                    data=None,
                    error=True,
                    message="Error while executing search query."
                    ),
            500, None)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@app.route('/save_data', methods=['POST'])
@jwt_required
def save_user_view_configs():
    try:
        if request.method == "POST":
            request_data = request.get_json(silent=True)
            username = get_jwt_identity()
            add_to_logs("Saving data to db: {}".format(request_data), username)
            total_saved = 0
            for item in request_data:
                sample_data = db.session.query(Sample).filter_by(id=item.get("id")).first()
                if sample_data:
                    sample_data.do_not_use = 1 if item.get("do_not_use").lower() == "true" else 0
                    sample_data.data_access = item.get("data_access")
                    sample_data.date_updated = datetime.datetime.now()
                    sample_data.updated_by = username
                    db.session.commit()
                    total_saved += 1
                    AppLog.info(message="Updated Sample record with ID: {}".format(sample_data.id), user=username)
            response = make_response(
                jsonify(
                    success=True,
                    error=False,
                    message="Successfully updated {} Sample records.".format(total_saved),
                ),
                200, None)
            response.headers.add('Access-Control-Allow-Origin', '*')
            add_to_logs("Successfully saved data.", username)
            return response
    except Exception:
        message = "while updating data: {}".format(traceback.print_exc())
        add_error_to_logs(message, "api")
        response = make_response(
            jsonify(
                success=False,
                error=True,
                message="Error while updating Sample records."), 500, None)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@app.route('/save_view_configs', methods=['POST'])
@jwt_required
def save_view_configs():
    try:
        if request.method == "POST":
            request_params = request.get_json(silent=True)
            hidden_columns = request_params.get("hiddenColumns")
            username = get_jwt_identity()
            hidden_columns_str_val = ",".join(str(integer) for integer in hidden_columns) if len(hidden_columns) > 0 \
                else None
            if username:
                user_view_config = UserViewConfig.query.filter_by(username=username).first()
                if user_view_config:
                    user_view_config.hidden_columns = hidden_columns_str_val
                    user_view_config.date_updated = datetime.datetime.now()
                    db.session.commit()
                    add_to_logs("Updated UserViewConfig record with ID: {}".format(user_view_config.id), username)
                    response = make_response(
                        jsonify(
                            success=True,
                            data=hidden_columns,
                            error=False,
                            message="Successfully saved view configs"), 200, None)
                    response.headers.add('Access-Control-Allow-Origin', '*')
                    return response
                else:
                    user_view_config = UserViewConfig(
                        username=username,
                        hidden_columns=hidden_columns_str_val
                    )
                    db.session.add(user_view_config)
                    db.session.commit()
                    add_to_logs("Created new UserViewConfig record with ID: {}".format(user_view_config.id), username)
                    response = make_response(
                        jsonify(
                            success=True,
                            data=hidden_columns,
                            error=False,
                            message="Successfully saved view configs"), 200, None)
                    response.headers.add('Access-Control-Allow-Origin', '*')
                    return response

    except Exception:
        message = "Error while updating user view configs: {}".format(traceback.print_exc())
        add_error_to_logs(message, "api")
        response = make_response(
            jsonify(
                success=False,
                data=None,
                error=False,
                message="Error while saving view configs"), 500, None)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
