""" Create the model of the table series"""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from sphere.dicmeta.models.core_model import CoreModel
from sphere.dicmeta.models.base_models.base_series_model import BaseSeriesModel
from sphere.dicmeta.models.base import DB_BASE_PACS
from sphere.dicmeta.models.base import table_full_name


class SeriesModel(DB_BASE_PACS, BaseSeriesModel):
    """ Create series model """
    __tablename__ = 'series'

    id = Column(__tablename__+'_id', CoreModel.ID_TYPE, primary_key=True)

    study_id = Column(
        CoreModel.ID_TYPE, ForeignKey(table_full_name('study.study_id')))
    study = relationship(
        "StudyModel", back_populates="series", cascade="all,delete")

    patient_id = Column(
        CoreModel.ID_TYPE, ForeignKey(table_full_name('patient.patient_id')))
    patient = relationship(
        "PatientModel", back_populates="series", cascade="all,delete")

    instances = relationship(
        "FileStorageMetadataDicomModel", back_populates="series", cascade="all,delete")
