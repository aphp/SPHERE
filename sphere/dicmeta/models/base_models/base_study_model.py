""" Create the base model of the table study"""
# pylint: disable=bad-whitespace, exec-used, eval-used, unused-import
from sqlalchemy import Column
# Type 'Text' use with extended_db
from sqlalchemy.types import String, Text

from sphere.dicmeta.models.core_model import CoreModel


# pylint: disable=line-too-long
class BaseStudyModel(CoreModel):
    """ Create study model """

    KEY = 'studyUID'
    ID = 'id'

    id               = Column('study_id',          CoreModel.ID_TYPE, primary_key=True)
    studyUID         = Column('study_uid',         String(64), nullable=False, index=True, unique=True)
    patientID        = Column('patient_uid',       String(64), nullable=False)
    dateStudy        = Column('date_study',        String(10))

    institutionName  = Column('institution_name',  String(256))
    accessionNumber  = Column('accession_number',  String(256))
    protocolName     = Column('protocol_name',     String(512))
    studyDescription = Column('study_description', String(512))

    for attribute, size_value in CoreModel.attributes_extended('study'):
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
        args = {'id': self.id,
                'patientID': self.patientID,
                'studyUID': self.studyUID,
                'dateStudy': self.dateStudy,
                'institutionName': self.institutionName,
                'patient_id': self.patient_id,
                'accessionNumber': self.accessionNumber,
                'protocolName': self.protocolName,
                'studyDescription': self.studyDescription}

        for field_name in self.extended_fields('study'):
            args[field_name] = eval("self." + eval("field_name"))

        return self.add_value_none(include_none, args)

    def __repr__(self):
        return "<Study(id='%s', studyUID='%s', patientID='%s'," \
               "dateStudy='%s')>" % (self.id, self.studyUID,
                                     self.patientID, self.dateStudy)

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
                msg += suffix+'studyUID\t\t: %s' % self.studyUID
            else:
                msg += suffix+'%s' % self.studyUID
            if data_level > 0:
                msg += suffix+'patientID\t\t: %s' % self.patientID
                msg += suffix+'dateStudy\t\t: %s' % self.dateStudy
                msg += suffix+'institutionName\t: %s' % self.institutionName
            if data_level > 1:
                msg += suffix+'patient_id\t\t: %s' % self.patient_id
                msg += suffix+'N series\t\t: %s' % len(self.series)
                msg += suffix+'N instances\t\t: %s' % len(self.instances)
        elif file_format == 'json':
            return self.json()
        elif file_format == 'csv':
            data = []
            if data_level > 1:
                data.append(self.id)
            data.append(self.studyUID)
            if data_level > 0:
                data.append(self.patientID)
                data.append(self.dateStudy)
                data.append(self.institutionName)
            if data_level > 1:
                data.append(self.patient_id)
                data.append(len(self.series))
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
        head.append('studyUID')
        if data_level > 0:
            head.append('patientID')
            head.append('patientID')
            head.append('institutionName')
        if data_level > 1:
            head.append('patient_id')
            head.append('N series')
            head.append('N instances')
        return ','.join(['"'+h+'"' for h in head])+'\n'
