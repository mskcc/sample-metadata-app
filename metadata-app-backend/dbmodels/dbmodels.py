import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_continuum import make_versioned
import sqlalchemy as sa

db = SQLAlchemy()
make_versioned(user_cls=None)


class Patient(db.Model):
    __versioned__ = {}
    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(300), unique=True, nullable=False)
    cmo_patientid = db.Column(db.String(300), nullable=False)
    cmo_sampleid = db.Column(db.String(300))
    samples = db.relationship('Sample', backref='patient', lazy='joined')


class Sample(db.Model):
    __versioned__ = {}
    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(10), db.ForeignKey('patient.mrn'), index=True)
    igoid = db.Column(db.String(300), unique=True, nullable=True)
    investigator_sampleid = db.Column(db.String(300))
    sample_type = db.Column(db.String(300))
    species = db.Column(db.String(300), nullable=False)
    preservation = db.Column(db.String(300))
    tumor_normal = db.Column(db.String(300))
    tissue_source = db.Column(db.String(300))
    sample_origin = db.Column(db.String(300))
    specimen_type = db.Column(db.String(300))
    gender = db.Column(db.String(300))
    parent_tumortype = db.Column(db.String(300))
    tumortype = db.Column(db.String(300))
    tissue_location = db.Column(db.String(300))
    ancestor_sample = db.Column(db.String(300))
    donotuse = db.Column(db.Integer)
    assays = db.relationship('Assay', backref='sample', lazy=True, foreign_keys='Assay.idsample')
    fastq_data = db.relationship('Data', backref='sample', lazy=True, foreign_keys='SampleData.idsample')

class Assay(db.Model):
    __versioned__ = {}
    id = db.Column(db.Integer, primary_key=True, unique=True)
    idsample = db.Column(db.Integer, db.ForeignKey('sample.id'))
    recipe = db.Column(db.String(300))
    baitset = db.Column(db.String(300))
    igoid = db.Column(db.String(300), db.ForeignKey('sample.igoid'))


class Data(db.Model):
    __versioned__ = {}
    id = db.Column(db.Integer, primary_key=True, unique=True)
    idsample = db.Column(db.Integer, db.ForeignKey('sample.id'))
    fastq_path = db.Column(db.String(300))
    igoid = db.Column(db.String(300), db.ForeignKey('sample.igoid'))


class Sample(db.Model):
    __versioned__ = {}
    id = db.Column(db.Integer, unique=True)
    mrn = db.Column(db.String(300), db.ForeignKey('patient.mrn'), unique=True, primary_key=True)
    igoid = db.Column(db.String(300), unique=True, nullable=True)
    investigator_sampleid = db.Column(db.String(300))
    sample_type = db.Column(db.String(300))
    species = db.Column(db.String(300), nullable=False)
    preservation = db.Column(db.String(300))
    tumor_normal = db.Column(db.String(300))
    tissue_source = db.Column(db.String(300))
    sample_origin = db.Column(db.String(300))
    specimen_type = db.Column(db.String(300))
    gender = db.Column(db.String(300))
    parent_tumortype = db.Column(db.String(300))
    tumortype = db.Column(db.String(300))
    tissue_location = db.Column(db.String(300))
    ancestor_sample = db.Column(db.String(300))
    donotuse = db.Column(db.Integer)
    assays = db.relationship('Assay', backref='sample', lazy=True, foreign_keys='Assay.idsample')
    fastq_data = db.relationship('SampleData', backref='sample', lazy=True, foreign_keys='SampleData.idsample')


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
        db.session.flush()

    @staticmethod
    def info(message, user):
        applog = AppLog()
        applog.level = "INFO"
        applog.process = "root"
        applog.user = user
        applog.message = message
        db.session.add(applog)
        db.session.commit()
        db.session.flush()

    @staticmethod
    def warning(message, user):
        applog = AppLog()
        applog.level = "WARNING"
        applog.process = "root"
        applog.user = user
        applog.message = message
        db.session.add(applog)
        db.session.commit()
        db.session.flush()

    @staticmethod
    def error(message, user):
        applog = AppLog()
        applog.level = "ERROR"
        applog.process = "root"
        applog.user = user
        applog.message = message
        db.session.add(applog)
        db.session.commit()
        db.session.flush()


class SampleData:
    def __init__(self, igoid=None, mrn=None, investigator_sampleid=None, cmo_patientid=None, cmo_sampleid=None,
                 sample_type=None, species=None, preservation=None, tumor_normal=None,
                 tissue_source=None, sample_origin=None, specimen_type=None, gender=None, parent_tumortype=None,
                 tumortype=None,
                 tissue_location=None, ancestor_sample=None, donotuse=False, assay=None, fastq_data=None):
        self.igoid = igoid
        self.mrn = mrn
        self.investigator_sampleid = investigator_sampleid
        self.cmo_patientid = cmo_patientid
        self.cmo_sampleid = cmo_sampleid
        self.sample_type = sample_type
        self.species = species
        self.preservation = preservation
        self.tumor_normal = tumor_normal
        self.tissue_source = tissue_source
        self.sample_origin = sample_origin
        self.specimen_type = specimen_type
        self.gender = gender
        self.parent_tumortype = parent_tumortype
        self.tumortype = tumortype
        self.tissue_location = tissue_location
        self.ancestor_sample = ancestor_sample
        self.donotuse = donotuse
        self.assay = assay
        self.fastq_data = fastq_data


sa.orm.configure_mappers()
