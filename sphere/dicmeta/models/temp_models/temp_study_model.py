""" Create the temp model of the table study"""
from sqlalchemy import Column
from sqlalchemy.types import String

from sphere.dicmeta.models.core_model import CoreModel
from sphere.dicmeta.models.base_models.base_study_model import BaseStudyModel
from sphere.dicmeta.models.base import DB_BASE_PACS
from sphere import settings


class TempStudyModel(DB_BASE_PACS, BaseStudyModel):
    """ Create study model """
    __tablename__ = 'tmp_'+str(settings.SCP_PORT)+'_study'

    id = Column(__tablename__+'_id', CoreModel.ID_TYPE, primary_key=True)

    studyUID = Column('study_uid', String(64), nullable=False)
