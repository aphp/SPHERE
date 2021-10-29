""" Create the temp model of the table patient"""
from sqlalchemy import Column
from sqlalchemy.types import String

from sphere.dicmeta.models.base_models.base_patient_model import BasePatientModel
from sphere.dicmeta.models.core_model import CoreModel
from sphere.dicmeta.models.base import DB_BASE_PACS
from sphere import settings


class TempPatientModel(DB_BASE_PACS, BasePatientModel):
    """ Create patient model """
    __tablename__ = 'tmp_'+str(settings.SCP_PORT)+'_patient'

    id = Column(__tablename__+'_id', CoreModel.ID_TYPE, primary_key=True)

    patientID = Column('patient_uid', String(64), nullable=False)
