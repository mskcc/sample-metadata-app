import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_continuum import make_versioned
import sqlalchemy as sa

db = SQLAlchemy()
make_versioned(user_cls=None)


class Patient(db.Model):
    __versioned__ = {}
    __tablename__= 'patient'
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
    gender = db.Column(db.String(300))
    parent_tumor_type = db.Column(db.String(300))
    tumor_type = db.Column(db.String(300))
    tissue_location = db.Column(db.String(300))
    ancestor_sample = db.Column(db.String(300))
    sample_status = db.Column(db.String(300))
    do_not_use = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)
    created_by = db.Column(db.String(300), default="api")
    date_updated=db.Column(db.DateTime, default=datetime.datetime.now)
    updated_by=db.Column(db.String(300), default="api")
    assays = db.relationship('Assay', backref='sample', lazy=True)
    fastq_data = db.relationship('Data', backref='sample', lazy=True)

class Assay(db.Model):
    __versioned__ = {}
    __tablename__ = 'assay'
    id = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    id_sample = db.Column(db.Integer, db.ForeignKey('sample.id'), index=True)
    recipe = db.Column(db.String(300))
    bait_set = db.Column(db.String(300))
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)
    created_by = db.Column(db.String(300), default="api")
    date_updated = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_by = db.Column(db.String(300), default="api")


class Data(db.Model):
    __versioned__ = {}
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    id_sample = db.Column(db.Integer, db.ForeignKey('sample.id'), index=True)
    fastq_path = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)
    created_by = db.Column(db.String(300), default="api")
    date_updated = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_by = db.Column(db.String(300), default="api")


class AppLog(db.Model):
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


class SampleData:
    def __init__(self, mrn= None, igo_id=None, investigator_sample_id=None, sample_type=None, species=None, cmo_patient_id=None, cmo_sample_id=None,
                dmp_id=None, preservation=None, tumor_normal=None, tissue_source=None, sample_origin=None, specimen_type=None, gender=None, parent_tumor_type=None,
                tumor_type=None, tissue_location=None, ancestor_sample=None, sample_status= None, do_not_use=False, recipe=None, bait_set=None, fastq_data=None):

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
        self.tissue_source = tissue_source
        self.sample_origin = sample_origin
        self.specimen_type = specimen_type
        self.gender = gender
        self.parent_tumor_type = parent_tumor_type
        self.tumor_type = tumor_type
        self.tissue_location = tissue_location
        self.ancestor_sample = ancestor_sample
        self.sample_status = sample_status
        self.do_not_use = do_not_use
        self.recipe = recipe
        self.bait_set = bait_set
        self.fastq_data =fastq_data


sa.orm.configure_mappers()
