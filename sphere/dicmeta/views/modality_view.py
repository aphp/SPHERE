""" Create the model of the view tools_modality"""
from sqlalchemy import Column
from sqlalchemy.types import String, Integer, BigInteger

from sphere.dicmeta.models.dicom_models.series_model import SeriesModel
from sphere.dicmeta.models.dicom_models.file_storage_metadata_model import FileStorageMetadataDicomModel
from sphere.utilities.string_tools import pretty_size
from sphere.dicmeta.views.base import DB_BASE_VIEWS
from sphere.dicmeta.views.core_view import CoreView


class ModalityView(DB_BASE_VIEWS, CoreView):
    """ Create tools_modality model """
    __tablename__ = 'tools_modality'

    KEY = 'modality'
    ID = None
    # pylint: disable=bad-whitespace
    modality = Column('modality', String(64), nullable=False, primary_key=True)
    sumPatient  = Column('sum_patient',  Integer,    nullable=True)
    sumStudies  = Column('sum_studies',  Integer,    nullable=True)
    sumSeries   = Column('sum_series',   Integer,    nullable=True)
    sumInstance = Column('sum_instance', Integer,    nullable=True)
    size        = Column('size',         BigInteger)
    sumError    = Column('sum_error',    Integer)

    ORDER_BY = sumInstance.desc()

    definition = '''SELECT modality AS modality,
            count(distinct series.patient_id) AS sum_patient, 
            count(distinct series.study_id) AS sum_studies, 
            count(distinct series.series_id) AS sum_series,
            count(distinct file_storage_metadata_dicom.file_storage_metadata_dicom_id) AS sum_instance,
            SUM(filesize) AS size,
            SUM(storage_status) AS sum_error
             FROM %s join %s ON (file_storage_metadata_dicom.series_id=series.series_id) 
            GROUP BY modality
            ORDER BY sum_instance DESC;''' % (
                SeriesModel().table_full_name(),
                FileStorageMetadataDicomModel().table_full_name())

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
        args = {'modality': self.modality,
                'sumPatient': self.sumPatient,
                'sumStudies': self.sumStudies,
                'sumSeries': self.sumSeries,
                'sumInstance': self.sumInstance,
                'size': self.size,
                'sumError': self.sumError,
                }

        if not include_none:
            return {k: v for k, v in args.items() if v is not None}
        return args

    def __repr__(self):
        return "<ToolsModality(modality='%s', sumInstance='%s', size='%s', " \
               "sumError='%s')>" % (self.modality, self.sumInstance,
                                    self.size, self.sumError)

    def display(self, data_level=0, file_format='txt', output_console=False):
        """
        Display the modality

        :param data_level: The level of displaying or writing the data

            The possible value:

                - ``0`` - key (default)
                - ``1`` - minimal
                - ``2`` - full

        :type data_level: int, optional
        :param file_format: The file format
        :type file_format: str, optional
        :param output_console: Output console (True | False)
        :type output_console: bool, optional
        :return: The message
        :rtype: str
        """
        msg = ''
        if file_format == 'txt':
            msg += '%s' % self.modality
            if data_level > 1:
                msg += '\t(%s|%s|%s|%s)' % (self.sumPatient, self.sumStudies,
                                            self.sumSeries, self.sumInstance)
            else:
                msg += '\t%s' % self.sumInstance
            if data_level > 0:
                msg += '\t%s%%' % \
                       (float(self.sumError)/float(self.sumInstance)*100)
            if data_level > 1:
                msg += ' (%s)' % self.sumError

            msg += '\t %s' % pretty_size(float(self.size))

        if output_console:
            print(msg)
        return msg
