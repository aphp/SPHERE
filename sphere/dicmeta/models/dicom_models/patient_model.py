""" Create the model of the table patient"""
from sqlalchemy import Column
from sqlalchemy.orm import relationship

from sphere.dicmeta.models.base_models.base_patient_model import BasePatientModel
from sphere.dicmeta.models.core_model import CoreModel
from sphere.dicmeta.models.base import DB_BASE_PACS


class PatientModel(DB_BASE_PACS, BasePatientModel):
    """ Create patient model """
    __tablename__ = 'patient'

    id = Column(__tablename__+'_id', CoreModel.ID_TYPE, primary_key=True)

    instances = relationship(
        "FileStorageMetadataDicomModel", back_populates="patient", cascade="all,delete")
    series = relationship(
        "SeriesModel", back_populates="patient", cascade="all,delete")
    studies = relationship(
        "StudyModel", back_populates="patient", cascade="all,delete")
