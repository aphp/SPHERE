""" Create the temp model of the table instance"""
from sqlalchemy import Column
from sqlalchemy.types import String

from sphere.dicmeta.models.base_models.base_file_storage_metadata_dicom_model import \
    BaseFileStorageMetadataDicomModel
from sphere.dicmeta.models.core_model import CoreModel
from sphere.dicmeta.models.base import DB_BASE_PACS
from sphere import settings


class TempFileStorageMetadataModel(DB_BASE_PACS, BaseFileStorageMetadataDicomModel):
    """ Create instances model """
    __tablename__ = 'tmp_'+str(settings.SCP_PORT)+'_file_storage_metadata'

    id = Column(__tablename__+'_id', CoreModel.ID_TYPE, primary_key=True)

    instanceUID = Column('instance_uid', String(64), nullable=False)
