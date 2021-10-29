""" Create the base model of the table instance"""
# pylint: disable=bad-whitespace, line-too-long, exec-used, eval-used
from sqlalchemy import Column
# Type 'Text' use with extended_db
from sqlalchemy.types import String, Text

from sphere.dicmeta.models.core_model import CoreModel
from sphere.dicmeta.models.core_storage_metadata_model import CoreStorageMetadataModel
from sphere.utilities.string_tools import pretty_size


# pylint: disable=line-too-long
class BaseFileStorageMetadataDicomModel(CoreStorageMetadataModel):
    """ Create instances model """

    KEY = 'instanceUID'
    ID = 'id'

    instanceUID = Column('instance_uid',   String(64), nullable=False, index=True, unique=True)
    seriesUID   = Column('series_uid',     String(64), nullable=False)
    studyUID    = Column('study_uid',      String(64), nullable=False)
    patientID   = Column('patient_uid',    String(64), nullable=False)

    for attribute, size_value in CoreModel.attributes_extended('instance'):
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
            'instanceUID': self.instanceUID,
            'series_id': self.series_id,
            'study_id': self.study_id,
            'patient_id': self.patient_id,
            # Storage
            'storageMethod': self.storageMethod,
            'filePath': self.filePath,
            'filesize': self.filesize,
            'storageStatus': self.storageStatus,
            'dt_deb_storage': str(self.dt_deb_storage),
            'dt_end_storage': str(self.dt_end_storage)
        }

        for field_name in self.extended_fields('instance'):
            args[field_name] = eval("self." + eval("field_name"))

        return self.add_value_none(include_none, args)

    def __repr__(self):
        return "<file_storage_metadata_dicom (id='{}', instanceUID='{}', " \
               "seriesUID='{}', studyUID='{}', patientID='{}', " \
               "storageMethod='{}', file_path='{}')>".format(
                self.id, self.instanceUID,self.seriesUID, self.studyUID,
                self.patientID, self.storageMethod, self.filePath)

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
                msg += '%s' % self.instanceUID
            else:
                msg += '\n- instanceUID\t\t: {}'.format(self.instanceUID)
            if data_level > 0:
                msg += suffix + 'patientID\t\t: {}'.format(self.patientID)
                msg += suffix + 'studyUID\t\t: {}'.format(self.studyUID)
                msg += suffix + 'seriesUID\t\t: {}'.format(self.seriesUID)
                msg += suffix + 'filePath \t\t: {}'.format(self.filePath)
                msg += suffix + 'storageMethod\t\t: {}'.format(self.storageMethod)
                msg += suffix + 'filesize\t\t: {}'.format(pretty_size(self.filesize))
            if data_level > 1:
                msg += suffix + 'patient_id\t\t: {}'.format(self.patient_id)
                msg += suffix + 'study_id\t\t: {}'.format(self.study_id)
                msg += suffix + 'series_id\t\t: {}'.format(self.series_id)
                msg += suffix + 'storageStatus\t\t: {}'.format(self.storageStatus)
                msg += suffix + 'dt_deb_storage\t: {}'.format(self.dt_deb_storage)
                msg += suffix + 'dt_end_storage\t: {}'.format(self.dt_end_storage)
        elif file_format == 'json':
            return self.json()
        elif file_format == 'csv':
            data = []
            if data_level > 1:
                data.append(self.id)
            data.append(self.instanceUID)
            if data_level > 0:
                data.append(self.patientID)
                data.append(self.studyUID)
                data.append(self.seriesUID)
                data.append(self.filePath)
                data.append(self.storageMethod)
                data.append(self.filesize)
            if data_level > 1:
                data.append(self.patient_id)
                data.append(self.study_id)
                data.append(self.series_id)
                data.append(self.storageStatus)
                data.append(self.dt_deb_storage)
                data.append(self.dt_end_storage)
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
            head.append('patientID')
            head.append('studyUID')
            head.append('seriesUID')
            head.append('filePath')
            head.append('storageMethod')
            head.append('filesize')
        if data_level > 1:
            head.append('patient_id')
            head.append('study_id')
            head.append('series_id')
            head.append('storageStatus')
            head.append('dt_deb_storage')
            head.append('dt_end_storage')
        return ','.join(['"'+h+'"' for h in head])+'\n'
