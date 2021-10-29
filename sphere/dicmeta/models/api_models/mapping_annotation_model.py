""" Create the model of the table study"""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import String
from sqlalchemy.orm import relationship


from sphere.dicmeta.models.core_model import CoreModel
from sphere.dicmeta.models.base import DB_BASE_PACS
from sphere.dicmeta.models.base import table_full_name


class MappingAnnotationModel(DB_BASE_PACS, CoreModel):
    """ Create mapping_annotation model """
    __tablename__ = 'mapping_annotation'

    KEY = 'id'
    ID = 'id'

    id = Column(__tablename__+'_id', CoreModel.ID_TYPE, primary_key=True)

    uid_dicom_source = Column('uid_dicom_source', String(64), nullable=False)
    level_dicom_source = Column('level_dicom_source', String(16), nullable=False)
    uid_annotation = Column('uid_annotation', String(64), nullable=False, index=True, unique=True)

    file_storage_metadata_dicom_id = Column(
        CoreModel.ID_TYPE,
        ForeignKey(table_full_name('file_storage_metadata_dicom.file_storage_metadata_dicom_id')))
    relationship_file_sm = relationship(
        "FileStorageMetadataDicomModel",
        uselist=False, back_populates="relationship_ma", cascade="all,delete")

    def dict_data(self, include_none=False):
        """
        The dictionary of data

        :param include_none:  If you want to add None so that's True
            otherwise it's False
        :type include_none: bool, optional
        :return: A dictionary
        :rtype: dict
        """
        args = {'id': self.id,
                'uid_dicom_source': self.uid_dicom_source,
                'level_dicom_source': self.level_dicom_source,
                'uid_annotation': self.uid_annotation,
                'storage_metadata_id': self.file_storage_metadata_dicom_id}
        if not include_none:
            return {k: v for k, v in args.items() if v is not None}
        return args

    def __repr__(self):
        return "<MappingAnnotationModel(id='%s', uid_dicom_source='%s'," \
               "level_dicom_source='%s', uid_annotation='%s')>" % (
                self.id, self.uid_dicom_source, self.level_dicom_source,
                self.uid_annotation)
