""" Create the temp model of the table series"""
from sqlalchemy import Column
from sqlalchemy.types import String

from sphere.dicmeta.models.core_model import CoreModel
from sphere.dicmeta.models.base_models.base_series_model import BaseSeriesModel
from sphere.dicmeta.models.base import DB_BASE_PACS
from sphere import settings


class TempSeriesModel(DB_BASE_PACS, BaseSeriesModel):
    """ Create series model """
    __tablename__ = 'tmp_'+str(settings.SCP_PORT)+'_series'

    id = Column(__tablename__+'_id', CoreModel.ID_TYPE, primary_key=True)

    seriesUID = Column('series_uid', String(64), nullable=False)
