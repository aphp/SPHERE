""" Create the model of the table study"""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from sphere.dicmeta.models.core_model import CoreModel
from sphere.dicmeta.models.base_models.base_study_model import BaseStudyModel
from sphere.dicmeta.models.base import DB_BASE_PACS, table_full_name


class StudyModel(DB_BASE_PACS, BaseStudyModel):
    """ Create study model """
    __tablename__ = 'study'

    id = Column(__tablename__+'_id', CoreModel.ID_TYPE, primary_key=True)

    patient_id = Column(
        CoreModel.ID_TYPE, ForeignKey(table_full_name('patient.patient_id')))
    patient = relationship(
        "PatientModel", back_populates="studies", cascade="all,delete")

    instances = relationship(
        "FileStorageMetadataDicomModel", back_populates="study", cascade="all,delete")
    series = relationship(
        "SeriesModel", back_populates="study", cascade="all,delete")
