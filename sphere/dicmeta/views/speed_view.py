""" Create the model of the view tools_speed"""
from sqlalchemy import Column
from sqlalchemy.types import Float

from sphere.dicmeta.models.dicom_models.file_storage_metadata_model import FileStorageMetadataDicomModel
from sphere.utilities.string_tools import pretty_size
from sphere.dicmeta.views.base import DB_BASE_VIEWS
from sphere.dicmeta.views.core_view import CoreView


class SpeedView(DB_BASE_VIEWS, CoreView):
    """ Create tools_speed model """
    __tablename__ = 'tools_speed'

    KEY = None
    ID = None

    time = Column('time', Float, nullable=False, primary_key=True)
    file = Column('file', Float, nullable=False, primary_key=True)
    size = Column('size', Float, nullable=True)

    definition = '''SELECT
    extract(epoch from MAX(dt_end_storage) - MIN(dt_end_storage)) AS time,
    COUNT(1)/ extract(epoch from MAX(dt_end_storage) - MIN(dt_end_storage)) 
    AS file, 
    SUM(filesize)/ extract(epoch from MAX(dt_end_storage) - MIN(dt_end_storage)) 
    :: bigint AS size
    FROM (SELECT * FROM %s ORDER BY d8ins DESC LIMIT 500) AS instance_storage_metadata;
    ''' % (FileStorageMetadataDicomModel().table_full_name())

    def __init__(self):
        self.view = self.metadata

    def dict_data(self, include_none=False):
        """
        The dictionary of data

        :param include_none:  If you want to add None so that's True
            otherwise it's False
        :type include_none: bool
        :return: A dictionary
        :rtype: dict
        """
        args = {'file': self.file,
                'size': self.size,
                }

        if not include_none:
            return {k: v for k, v in args.items() if v is not None}
        return args

    def __repr__(self):
        return "<ToolsSpeed(file='%s', size='%s')>" % (self.file, self.size)

    def display(self, data_level=0, file_format='txt', output_console=False):
        """
        Display file/s, size/s and time of send the DICOM in database

        :param data_level: The level of displaying or writing the data

            The possible value:

                - ``0`` - key (default)
                - ``1`` - minimal
                - ``2`` - full

        :type data_level: int, optional
        :param file_format: The file format
        :type file_format: str, optional
        :param output_console: output console (True | False)
        :type output_console: bool, optional
        :return: The message
        :rtype: str
        """
        msg = ''
        if file_format == 'txt':
            if data_level == 0:
                msg += '%s/s' % (pretty_size(float(self.size)))
            if data_level > 0:
                msg += 'file/s \t: %3.2f\nsize/s \t: %s' % (
                    self.file, pretty_size(float(self.size)))
            if data_level > 1:
                msg += '\ntime\t: %3.2f s' % self.time

        if output_console:
            print(msg)
        return msg
