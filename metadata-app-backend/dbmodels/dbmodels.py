import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_continuum import make_versioned
import sqlalchemy as sa

db = SQLAlchemy()
make_versioned(user_cls=None)


class Patient(db.Model):
    """
    DB Model for Patient object. Has One to Many relationship with Sample object.
    """
    __versioned__ = {}
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True, index=True)
    mrn = db.Column(db.String(45), unique=True, nullable=False, index=True)
    cmo_patient_id = db.Column(db.String(300), nullable=False)
    cmo_sample_id = db.Column(db.String(300))
    dmp_id = db.Column(db.String(300))
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)
    created_by = db.Column(db.String(300), default="api")
    date_updated = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_by = db.Column(db.String(300), default="api")
    samples = db.relationship('Sample', backref='patient', lazy='joined')


class Sample(db.Model):
    """
    DB Model for Sample object. Has Many to One relationship with Patient object.
    """
    __versioned__ = {}
    __tablename__ = 'sample'
    id = db.Column(db.Integer, primary_key=True, index=True)
    mrn = db.Column(db.String(45), db.ForeignKey('patient.mrn'), index=True)
    igo_id = db.Column(db.String(300), unique=True, nullable=True)
    investigator_sample_id = db.Column(db.String(300))
    sample_type = db.Column(db.String(300))
    species = db.Column(db.String(300), nullable=False)
    preservation = db.Column(db.String(300))
    tumor_normal = db.Column(db.String(300))
    tissue_source = db.Column(db.String(300))
    sample_origin = db.Column(db.String(300))
    specimen_type = db.Column(db.String(300))
    sex = db.Column(db.String(300))
    parent_tumor_type = db.Column(db.String(300))
    tumor_type = db.Column(db.String(300))
    tissue_location = db.Column(db.String(300))
    ancestor_sample = db.Column(db.String(300))
    #sample_status = db.Column(db.String(300))
    lab_head = db.Column(db.String(300))
    data_access = db.Column(db.String(300), default="Restricted")
    do_not_use = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)
    created_by = db.Column(db.String(300), default="api")
    date_updated = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_by = db.Column(db.String(300), default="api")
    assay = db.Column(db.Integer, db.ForeignKey('assay.id'), index=True)
    baitset = db.Column(db.Integer, db.ForeignKey('baitset.id'), index=True)


class Assay(db.Model):
    """
    DB Model for Assay object. Has One to Many relationship with Sample object.
    """
    __versioned__ = {}
    __tablename__ = 'assay'
    id = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    recipe = db.Column(db.String(300))
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)
    created_by = db.Column(db.String(300), default="api")
    date_updated = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_by = db.Column(db.String(300), default="api")
    samples = db.relationship('Sample', backref='sample_assay', lazy='joined')

class Baitset(db.Model):
    """
    DB Model for Baitset object. Has One to Many relationship with Sample object.
    """
    __versioned__ = {}
    __tablename__ = 'baitset'
    id = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    bait_set = db.Column(db.String(300))
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)
    created_by = db.Column(db.String(300), default="api")
    date_updated = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_by = db.Column(db.String(300), default="api")
    samples = db.relationship('Sample', backref='sample_baitset', lazy='joined')


class AppLog(db.Model):
    """
    DB Model for AppLog object to record App logging.
    """
    id = db.Column(db.Integer, primary_key=True, unique=True)
    time = db.Column(db.String(300))
    level = db.Column(db.String(300))
    process = db.Column(db.String(300))
    user = db.Column(db.String(300))
    message = db.Column(db.Text(4294000000))

    def __init__(self, time=datetime.datetime.now(), level=None, process=None, user=None, message=None):
        self.time = time
        self.level = level,
        self.process = process
        self.user = user
        self.message = message

    def log(self, db=db):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def info(message, user):
        applog = AppLog()
        applog.level = "INFO"
        applog.process = "root"
        applog.user = user
        applog.message = message
        db.session.add(applog)
        db.session.commit()

    @staticmethod
    def warning(message, user):
        applog = AppLog()
        applog.level = "WARNING"
        applog.process = "root"
        applog.user = user
        applog.message = message
        db.session.add(applog)
        db.session.commit()

    @staticmethod
    def error(message, user):
        applog = AppLog()
        applog.level = "ERROR"
        applog.process = "root"
        applog.user = user
        applog.message = message
        db.session.add(applog)
        db.session.commit()


class UserViewConfig(db.Model):
    """
    DB Model for UserViewConfig object to save client side grid view configurations.
    """
    __tablename__ = 'userviewconfig'
    id = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    username = db.Column(db.String(300))
    hidden_columns = db.Column(db.String(300), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)
    date_updated = db.Column(db.DateTime, default=datetime.datetime.now)


class SampleData:
    """
    Sample class to create Sample Objects to pass to client side.
    """
    def __init__(self, id=None, mrn=None, igo_id=None, investigator_sample_id=None, sample_type=None, species=None,
                 cmo_patient_id=None, cmo_sample_id=None, dmp_id=None, preservation=None, tumor_normal=None,
                 tissue_source=None, sample_origin=None, specimen_type=None, sex=None, parent_tumor_type=None,
                 tumor_type=None, tissue_location=None, ancestor_sample=None, sample_status=None, lab_head=None,
                 data_access=None, do_not_use=False, recipe=None, bait_set=None, fastq_data=None):
        self.id = id  # db id for Sample Table. This will be used when saving user edited changes on front end.
        # All editable fields are on Sample table.
        self.mrn = mrn
        self.igo_id = igo_id
        self.investigator_sample_id = investigator_sample_id
        self.sample_type = sample_type
        self.species = species
        self.cmo_patient_id = cmo_patient_id
        self.cmo_sample_id = cmo_sample_id
        self.dmp_id = dmp_id
        self.preservation = preservation
        self.tumor_normal = tumor_normal
        self.tumor_normal = tumor_normal
        self.tissue_source = tissue_source
        self.sample_origin = sample_origin
        self.specimen_type = specimen_type
        self.sex = sex
        self.parent_tumor_type = parent_tumor_type
        self.tumor_type = tumor_type
        self.tissue_location = tissue_location
        self.ancestor_sample = ancestor_sample
        self.sample_status = sample_status
        self.lab_head = lab_head
        self.data_access = data_access
        self.do_not_use = do_not_use
        self.recipe = recipe
        self.bait_set = bait_set
        self.fastq_data = fastq_data


sa.orm.configure_mappers()
