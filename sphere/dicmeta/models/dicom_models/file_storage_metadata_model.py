""" Create the model of the table file_storage_metadata_dicom"""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from sphere.dicmeta.models.base_models.base_file_storage_metadata_dicom_model import \
    BaseFileStorageMetadataDicomModel
from sphere.dicmeta.models.core_model import CoreModel
from sphere.dicmeta.models.base import DB_BASE_PACS
from sphere.dicmeta.models.base import table_full_name
try:
    from sphere.settings import START_ANNOTATION
except ImportError:
    START_ANNOTATION = False


class FileStorageMetadataDicomModel(DB_BASE_PACS, BaseFileStorageMetadataDicomModel):
    """ Create instances model """
    __tablename__ = 'file_storage_metadata_dicom'

    id = Column(__tablename__+'_id', CoreModel.ID_TYPE, primary_key=True)

    series_id = Column(
        CoreModel.ID_TYPE, ForeignKey(table_full_name('series.series_id')))
    series = relationship(
        "SeriesModel", back_populates="instances", cascade="all,delete")

    study_id = Column(
        CoreModel.ID_TYPE, ForeignKey(table_full_name('study.study_id')))
    study = relationship(
        "StudyModel", back_populates="instances", cascade="all,delete")

    patient_id = Column(
        CoreModel.ID_TYPE, ForeignKey(table_full_name('patient.patient_id')))
    patient = relationship(
        "PatientModel", back_populates="instances", cascade="all,delete")

    if START_ANNOTATION:
        relationship_ma = relationship(
            "MappingAnnotationModel",
            uselist=False,
            back_populates="relationship_file_sm",
            cascade="all,delete")
