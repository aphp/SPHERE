""" Create the base model of the table series"""
# pylint: disable=bad-whitespace, exec-used, eval-used, unused-import
from sqlalchemy import Column
# Type 'Text' use with extended_db
from sqlalchemy.types import String, Text, DateTime

from sphere.dicmeta.models.core_model import CoreModel


# pylint: disable=line-too-long
class BaseSeriesModel(CoreModel):
    """ Create series model """

    KEY = 'seriesUID'
    ID = 'id'

    seriesUID             = Column('series_uid',              String(64), nullable=False, index=True, unique=True)
    studyUID              = Column('study_uid',               String(64), nullable=False)
    patientID             = Column('patient_uid',             String(64), nullable=False)
    modality              = Column('modality',                String(10))
    manufacturer          = Column('manufacturer',            String(256))
    manufacturerModelName = Column('manufacturer_model_name', String(256))
    bodyPartExamined      = Column('body_part_examined',      String(256))
    seriesDate            = Column('series_date',             String(256))
    seriesDescription     = Column('series_description',      String(512))
    stationName           = Column('station_name',            String(256))
    dt_first_insertion    = Column(DateTime)
    dt_completion         = Column(DateTime)

    for attribute, size_value in CoreModel.attributes_extended('series'):
        exec(attribute)

    # pylint: disable=no-member
    def dict_data(self, include_none=False):
        """
        The dictionary of data

        :param include_none:  If you want to add None so that's True
            otherwise it's False
        :type include_none: bool
        :return: A dictionary
        :rtype: dict
        """
        args = {
            'id': self.id,
            'patientID': self.patientID,
            'studyUID': self.studyUID,
            'seriesUID': self.seriesUID,
            'modality': self.modality,
            'manufacturer': self.manufacturer,
            'manufacturerModelName': self.manufacturerModelName,
            'bodyPartExamined': self.bodyPartExamined,
            'seriesDate': self.seriesDate,
            'seriesDescription': self.seriesDescription,
            'stationName': self.stationName,
            'dt_first_insertion': self.dt_first_insertion,
            'dt_completion': self.dt_completion,
            'study_id': self.study_id,
            'patient_id': self.patient_id
        }
        for field_name in self.extended_fields('series'):
            args[field_name] = eval("self." + eval("field_name"))

        return self.add_value_none(include_none, args)

    def __repr__(self):
        return "<Series(id='%s', seriesUID='%s', studyUID='%s'," \
               "patientID='%s', modality='%s')>" % (self.id, self.seriesUID,
                                                    self.studyUID,
                                                    self.patientID,
                                                    self.modality)

    # pylint: disable=too-many-branches
    def display(self, data_level=0, file_format='txt', output_console=False,
                csv_text_delimiter=''):
        """
        Display or write the data

        :param data_level: The level of displaying or writing the data

            The possible value:

                - ``0`` - key (default)
                - ``1`` - minimal
                - ``2`` - full

        :type data_level: int, optional
        :param file_format: The file format

            The possible value:

                - txt (default)
                - csv
                - json

        :type file_format: str, optional
        :param output_console: Display in the console (True | False)
        :type output_console: bool, optional
        :param csv_text_delimiter: Delimiter of csv or txt file
        :type csv_text_delimiter: str, optional
        :return: The concatenate data
        :rtype: str
        """
        if file_format == 'txt':
            msg, suffix = self.msg_suffix(data_level)
            if data_level > 1:
                msg += suffix+'id\t\t\t: %s' % self.id
            if data_level > 0:
                msg += suffix+'seriesUID\t\t: %s' % self.seriesUID
            else:
                msg += suffix+'%s' % self.seriesUID
            if data_level > 0:
                msg += suffix+'studyUID\t\t: %s' % self.studyUID
                msg += suffix+'patientID\t\t: %s' % self.patientID
                msg += suffix+'modality\t\t: %s' % self.modality
            if data_level > 1:
                msg += suffix+'manufacturerModelName\t: %s' %\
                       self.manufacturerModelName
                msg += suffix+'bodyPartExamined\t: %s' % self.bodyPartExamined
                msg += suffix+'seriesDescription\t: %s' % self.seriesDescription
                msg += suffix+'seriesDate\t\t: %s' % self.seriesDate
                msg += suffix+'patient_id\t\t: %s' % self.patient_id
                msg += suffix+'study_id\t\t: %s' % self.study_id
                msg += suffix+'N instances\t\t: %s' % len(self.instances)
        elif file_format == 'json':
            return self.json()
        elif file_format == 'csv':
            data = []
            if data_level > 1:
                data.append(self.id)
            data.append(self.seriesUID)
            if data_level > 0:
                data.append(self.studyUID)
                data.append(self.patientID)
                data.append(self.modality)
            if data_level > 1:
                data.append(self.manufacturerModelName)
                data.append(self.bodyPartExamined)
                data.append(self.seriesDescription)
                data.append(self.seriesDate)
                data.append(self.patient_id)
                data.append(self.study_id)
                data.append(len(self.instances))
            return ','.join(
                [csv_text_delimiter+str(d)+csv_text_delimiter for d in data])
        if output_console:
            print(msg)
        return msg

    @staticmethod
    def header(data_level):
        """
        Return the header

        :param data_level: The level of displaying the header

            The possible value:

                - ``0`` - key
                - ``1`` - minimal
                - ``2`` - full

        :type data_level: int
        :return: The header
        :rtype: str
        """
        head = []
        if data_level > 1:
            head.append('id')
        head.append('instanceUID')
        if data_level > 0:
            head.append('studyUID')
            head.append('patientID')
            head.append('modality')
        if data_level > 1:
            head.append('manufacturerModelName')
            head.append('bodyPartExamined')
            head.append('seriesDescription')
            head.append('seriesDate')
            head.append('patient_id')
            head.append('study_id')
            head.append('N instances')
        return ','.join(['"'+h+'"' for h in head])+'\n'
