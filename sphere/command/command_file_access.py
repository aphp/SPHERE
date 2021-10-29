""" Command of file"""
# pylint: disable=invalid-name
import datetime
import re

from sphere.dicmeta.database_pacs import DatabasePACS
from sphere.fsa.file_system_access import FileSystemAccess
from sphere.fsa.file_system import FileSystem
from sphere.utilities.file import read_file_return_list


class CommandFileAccess:
    """ Command of file access (export and index)"""

    def __init__(self, **kwargs):
        self.db = DatabasePACS()
        self.action = kwargs['data_action']
        self.erase = False
        self.target_dir = None
        self.dicom_folder = None
        self.initialize_args(**kwargs)
        self.fsa = FileSystemAccess()
        self.fs = FileSystem()

    def initialize_args(self, **kwargs):
        """
        Initialize attribute of file access

        :param kwargs: Parameters dictionary

            The list of parameters is:

                | func      : Function namelist_study_uid
                | action    : Type of action, possible value is ``data``
                | data_action   : The data action

                    The possible value: ``export``, ``index`` or ``index_study``

                | target_dir: The path of target directory
                    ( exists if `data_action` equal ``export``)
                | list_study_uid: name file of list study uid
                    ( exists if `data_action` equal ``index_study``)
                | d_load: The data of load
                    ( exists if `data_action` equal ``index_study``)

            Example of kwargs: data_action equal ``export``
                | {
                |   'func'          : <function data_action at 0x7fe8d8b5d2f0>,
                |   'action'        : 'data',
                |   'data_action'   : 'export',
                |   'target_dir'    : 'file_uid'
                | }

        :type kwargs: dict
        """
        if self.action == 'index':
            if 'directory_dicom' in kwargs:
                self.dicom_folder = kwargs.get('directory_dicom')
        if self.action == 'export':
            if 'target_dir' in kwargs:
                self.target_dir = kwargs['target_dir']

        if self.action == 'index':
            if 'erase' in kwargs:
                self.erase = kwargs['erase']

        if self.action == 'index_study':
            if 'list_study_uid' in kwargs:
                self.list_study_uid = kwargs['list_study_uid']
            else:
                self.list_study_uid = None
            if 'd_load' in kwargs and kwargs['d_load'] is not None:
                if re.match(
                        r"([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))",
                        kwargs['d_load']):
                    self.d_load = kwargs['d_load']
                else:
                    raise Exception('the date format is not yyyy-mm-dd, '
                                    'be careful 1999-8-5 is not working you '
                                    'have to write 1999-08-05')
            else:
                self.d_load = datetime.date.today()

    def execute(self):
        """ Execute the action (export or index)"""
        if self.action == 'export':
            self.fs.duplicate_folder(self.target_dir)

        elif self.action == 'index':
            if self.dicom_folder:
                self.fsa.index_dicom_folder(self.erase, self.dicom_folder)
            else:
                self.fsa.index_dicom_folder(self.erase)

        elif self.action == 'index_study' and self.list_study_uid:
            db_pacs = DatabasePACS()
            study_model = db_pacs.StudyListModel()
            id_list = db_pacs.get_max_value(study_model, 'id_list')
            try:
                int(id_list)
                id_list = id_list + 1
            except Exception as error:
                print(error)
            for uid in read_file_return_list(self.list_study_uid):
                study_model = db_pacs.StudyListModel()
                study_model.id_list = id_list
                study_model.d_load = self.d_load
                study_model.study_uid = uid
                _study_id = db_pacs.create_or_update_model(
                    study_model, check_key=False, update=True, nested_level=2)
