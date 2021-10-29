""" Create the base model of the table patient"""
# pylint: disable=bad-whitespace, exec-used, eval-used, unused-import
from sqlalchemy import Column
# Type 'Text' use with extended_db
from sqlalchemy.types import String, Text

from sphere.dicmeta.models.core_model import CoreModel


# pylint: disable=line-too-long
class BasePatientModel(CoreModel):
    """ Create patient model """

    KEY = 'patientID'
    ID = 'id'

    patientID        = Column('patient_uid',        String(64), nullable=False, index=True, unique=True)
    patientName      = Column('patient_name',       String(128))
    patientSex       = Column('patient_sex',        String(64))
    patientBirthDate = Column('patient_birth_date', String(64))

    for attribute, size_value in CoreModel.attributes_extended('patient'):
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
            'patientName': self.patientName,
            'patientSex': self.patientSex,
            'patientBirthDate': self.patientBirthDate}

        for field_name in self.extended_fields('patient'):
            args[field_name] = eval("self." + eval("field_name"))

        return self.add_value_none(include_none, args)

    def __repr__(self):
        return "<Patient(id='%s', patientID='%s', patientName='%s'," \
               "patientSex='%s')>" % (self.id, self.patientID,
                                      self.patientName, self.patientSex)

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
            if data_level == 0:
                msg += '%s' % self.patientID
            else:
                msg += suffix+'patientID\t\t: %s' % self.patientID
            if data_level > 0:
                msg += suffix+'patientName\t\t: %s' % self.patientName
                msg += suffix+'patientSex\t\t: %s' % self.patientSex
                msg += suffix+'patientBirthDate\t: %s' % self.patientBirthDate
            if data_level > 1:
                msg += suffix+'N study\t\t: %s' % len(self.studies)
                msg += suffix+'N series\t\t: %s' % len(self.series)
                msg += suffix+'N instances\t\t: %s' % len(self.instances)
        elif file_format == 'json':
            return self.json()
        elif file_format == 'csv':
            data = []
            if data_level > 1:
                data.append(self.id)
            data.append(self.patientID)
            if data_level > 0:
                data.append(self.patientName)
                data.append(self.patientSex)
                data.append(self.patientBirthDate)
            if data_level > 1:
                data.append(len(self.studies))
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
        head.append('patientID')
        if data_level > 0:
            head.append('patientName')
            head.append('patientSex')
            head.append('patientBirthDate')
        if data_level > 1:
            head.append('N study')
            head.append('N series')
            head.append('N instances')
        return ','.join(['"'+h+'"' for h in head])+'\n'
