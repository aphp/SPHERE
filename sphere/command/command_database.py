""" Command of database """
# pylint: disable=eval-used, unused-import
from collections import Iterable
from os.path import isfile

from sphere.utilities.file import read_file_return_list
from sphere.dicmeta.database_pacs import DatabasePACS
from sphere.utilities.string_tools import upper_first_letter, replace_id_uid
from sphere.dicmeta.requests.patient_request import PatientRequest
from sphere.dicmeta.requests.study_request import StudyRequest
from sphere.dicmeta.requests.series_request import SeriesRequest
from sphere.dicmeta.requests.file_storage_metadata_request import FileStorageMetadataDicomRequest


class CommandDatabase:
    """ Method of database"""
    DATA_LEVEL = {'full': 2, 'minimal': 1, 'key': 0}

    def __init__(self, **kwargs):
        self.db = DatabasePACS()

        self.action = kwargs['db_action']

        self.output_format = 'txt'

        self.initialize_attribute(**kwargs)

    def initialize_attribute(self, **kwargs):
        """
        Initialize attribute od database

        :param kwargs: Parameters dictionary

            The list of parameters is:

                | func      : Function name
                | action    : Type of action, possible value is ``database``
                | db_action   : The action od database

                    The possible value: ``check`` or ``find``

                | concept: The display level

                    The possible value:
                        ``patient, study, series, fileStorageMetadataDicom``

                | data_level: The display level

                    The possible value: ``full``, ``minimal`` or ``key``

                | attribute: The attribute

                    The possible value:
                        | - ``seriesUID``
                        | - ``studyUID``
                        | - ``modality``
                        | - ``patientID``

                | filter_value: The filter value

            Example of kwargs:
                | {
                |   'func': <function request_action at 0x7f7f12178ae8>,
                |   'action': 'database',
                |   'db_action': 'find',
                |   'data_level': 'full',
                |   'concept': 'study',
                |   'attribute': 'studyUID',
                |   'filter_value': 4305052317,
                |   'output_filepath': None,
                |   'force_overwrite': False,
                |   'file_format': None,
                |   'list_filepath': None,
                |   'header': False,
                |   'append': False
                | }

        :type kwargs: dict

        """
        if 'concept' in kwargs and kwargs['concept'] in \
                ['patient', 'study', 'series', 'fileStorageMetadataDicom']:
            self.concept = kwargs['concept']
        else:
            raise Exception('Please define a "concept" model valid')

        if 'output_filepath' in kwargs:
            self.output_filepath = kwargs['output_filepath']
        else:
            self.output_filepath = None

        if 'list_filepath' in kwargs:
            self.list_filepath = kwargs['list_filepath']
        else:
            self.list_filepath = None

        if self.action == 'find':
            if 'data_level' in kwargs and kwargs['data_level'] in self.DATA_LEVEL:
                self.data_level = self.DATA_LEVEL[kwargs['data_level']]
            else:
                raise Exception('Please define a "data level" compatible')

            if 'append' in kwargs:
                self.output_append = kwargs['append']
            else:
                self.output_append = False

            if 'header' in kwargs:
                self.output_header = kwargs['header']
            else:
                self.output_header = False

            if 'file_format' in kwargs and (kwargs['file_format'] is None or
                                            kwargs['file_format'] in
                                            ['txt', 'csv', 'json']):
                if kwargs['file_format'] is not None:
                    self.output_format = kwargs['file_format']
            else:
                raise Exception('Please define a "output-format" compatible')

            if 'filter_value_list' in kwargs and 'filter_value' in kwargs and \
                    kwargs['filter_value'] is not None and \
                    kwargs['filter_value_list'] is not None:
                raise Exception(
                    'You could not give a value and a value list in arguments')
            elif 'filter_value_list' in kwargs and \
                    kwargs['filter_value_list'] is not None:
                if not isfile(kwargs['filter_value_list']):
                    txt_except = \
                        'File %s not found' % (kwargs['filter_value_list'])
                    raise Exception(txt_except)
                self.value_filepath = kwargs['filter_value_list']
            elif 'filter_value' in kwargs and \
                    kwargs['filter_value'] is not None:
                self.filter_value = kwargs['filter_value']
            # Si pas de valeur dans list alors par defaut c'est *
            else:
                self.filter_value = '*'

            if 'attribute' in kwargs and kwargs['attribute'] in \
                    ['seriesUID', 'studyUID', 'modality', 'patientID']:
                self.filter = kwargs['attribute']
            else:
                raise Exception(
                    'Please define a "attribute" filter column valid')

        if self.action == 'check':
            if 'output_concept' in kwargs and kwargs['output_concept'] in \
                    ['patient', 'study', 'series', 'fileStorageMetadataDicom']:
                self.output_concept = kwargs['output_concept']
            else:
                self.output_concept = self.concept

            if 'check_mode' in kwargs and kwargs['check_mode'] in \
                    ['diff', 'equal', 'detailled']:
                self.mode = kwargs['check_mode']
            else:
                raise Exception('Please define a "mode" compatible')

    def execute(self):
        """ Execute the action find and or check """
        if self.action == 'find':
            self.execute_find()
        if self.action == 'check':
            self.execute_check()

    def execute_find(self):
        """ Execute find"""
        try:
            self.classRequest = eval(upper_first_letter(self.concept)+'Request')
        except:
            txt = "Class Request " + upper_first_letter(self.concept) +\
                  'Request' + " not find"
            raise Exception(txt)
        req = self.classRequest(self.db)

        if self.filter_value in ['*', '?', ' ', '']:
            res = req.get_all()
        else:
            res = eval(
                'req.'+'get_by_' + replace_id_uid(self.filter) +
                '(\''+self.filter_value+'\')')

        self.output_data(res)

    def execute_check(self):
        """ Execute check"""
        data = self.check_value({id: self.check(id) for id in read_file_return_list(self.list_filepath)})
        if self.output_filepath is not None:
            file = open(self.output_filepath, 'w')
            data.append('')
            if self.output_filepath is not None:
                file.write('\n'.join(data))
        else:
            print('\n'.join(data))

    def check_value(self, dict_data):
        """
        Check if value is None or not and return key or value
        Return key if mode equal to 'diff' and value is None
        Return value if  mode different from 'diff' and value is not None

        :param dict_data: The data
        :type dict_data: dict
        :return: The list of id
        :rtype: list
        """
        list_id = []
        if self.mode == 'diff':
            for key, value in dict_data.items():
                if value is None:
                    list_id.append(key)
        else:
            for key, value in dict_data.items():
                if value is not None:
                    list_id.append(value)
        return list_id

    def check(self, identifier):
        """
        Check if id exists in table and return the data

        :param identifier: The identifier (id)
        :type identifier: str
        :return: The data
        :rtype: bool or None
        """
        req_class = eval(upper_first_letter(self.concept)+'Request(self.db)')
        tab = req_class.modelTable()
        val = eval(
            'req_class.get_by_' + replace_id_uid(tab.KEY)+'("'+identifier+'")')

        if val is None:
            return None
        elif hasattr(val, tab.KEY):
            return getattr(val, tab.KEY)
        else:
            txt_except = '% s not found for %' % (tab.KEY, val.__name__)
            raise Exception(txt_except)

    def output_data(self, data):
        """
        Display the data

        :param data: The data
        :type data: list
        """
        if data is None or (isinstance(data, (list,)) and len(data) < 1):
            # raise Exception('No db entries founded')
            print('No db entries founded')
            return
        try:
            if isinstance(data, Iterable):
                line_data = []
                for d in data:
                    line_data.append(d.display(
                        self.data_level, self.output_format,
                        output_console=True if self.output_filepath is None else False))
                if self.output_format == 'json':
                    format_data = \
                        '{"StorageMetadata":[' + ','.join(line_data) + ']}'
                else:
                    format_data = '\n'.join(line_data)
            else:
                format_data = data.display(
                    self.data_level, self.output_format,
                    output_console=True if self.output_filepath is None else False)

            if self.output_filepath is not None:
                self.write_data(format_data)

        except Exception as error:
            print(error)
            txt = "No display method for data " +\
                  upper_first_letter(self.concept)
            raise Exception(txt)

    def write_data(self, data):
        """
        Create file and write data

        :param data: The data
        :type data: str
        """
        mod = 'a' if self.output_append and self.output_format == 'csv' else 'w'

        file = open(self.output_filepath, mod)

        if self.output_format == 'csv':
            if self.output_append:
                file.write('\n')

        if self.output_header and not self.output_append:
            file.write(
                self.classRequest(self.db).modelTable().header(self.data_level)
            )

        file.write(data)

        file.close()
