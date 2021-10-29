from sqlalchemy import Column
from sqlalchemy.types import String, Integer, DateTime

from sphere.dicmeta.models.core_model import CoreModel


class CoreStorageMetadataModel(CoreModel):
    """ The core of model"""
    # storage_metadata
    storageMethod  = Column('storage_method', String(64),        nullable=False)
    filePath       = Column('file_path',      String(512),       nullable=False)
    filesize       = Column('filesize',       CoreModel.ID_TYPE, nullable=False)
    storageStatus  = Column('storage_status', Integer,           nullable=False)  # 0 = storage ok; 1 = fail storage
    dt_deb_storage = Column(DateTime)
    dt_end_storage = Column(DateTime)
