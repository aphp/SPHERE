""" Create the model of the table study"""
# pylint: disable=bad-whitespace
from sqlalchemy import Column
from sqlalchemy.types import String, Integer

from sphere.dicmeta.models.core_model import CoreModel
from sphere.dicmeta.models.base import DB_BASE_PACS


class StudyListModel(DB_BASE_PACS, CoreModel):
    """ Create study model """
    __tablename__ = 'study_list'

    KEY = 'id'
    ID = 'id'

    id        = Column('ids', CoreModel.ID_TYPE, primary_key=True)
    study_uid = Column('study_uid', String(64), nullable=False)
    id_list   = Column('id_list', Integer, nullable=False)
    d_load    = Column('d_load', String(16), nullable=False)

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
                'study_uid': self.study_uid,
                'id_list': self.id_list,
                'd_load': self.d_load,}
        if not include_none:
            return {k: v for k, v in args.items() if v is not None}
        return args

    def __repr__(self):
        return "<StudyListModel(id='%s', study_uid='%s', id_list='%s'," \
               "d_load='%s')>" % (self.id, self.study_uid,
                                  self.id_list, self.d_load)

    def display(
            self, data_level=0, file_format='txt', output_console=False,
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
            suffix = ''
            msg = ''
            if data_level > 0:
                msg += '-'*30
                suffix = suffix+'\n- '
            if data_level > 1:
                msg += suffix+'id\t\t\t: %s' % self.id
                msg += suffix+'studyUID\t\t: %s' % self.study_uid
            else:
                msg += suffix+'%s' % self.study_uid
            if data_level > 0:
                msg += suffix+'id_list\t\t: %s' % self.id_list
                msg += suffix+'dateLoad\t\t: %s' % self.d_load
            if data_level > 1:
                msg += suffix+'id_list\t\t: %s' % self.id_list
        elif file_format == 'json':
            return self.json()
        elif file_format == 'csv':
            data = []
            if data_level > 1:
                data.append(self.id)
            data.append(self.study_uid)
            if data_level > 0:
                data.append(self.id_list)
                data.append(self.d_load)
            if data_level > 1:
                data.append(self.id_list)
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
        head.append('study_uid')
        if data_level > 0:
            head.append('id_list')
            head.append('d_load')
        if data_level > 1:
            head.append('id_list')
        return ','.join(['"'+h+'"' for h in head])+'\n'
