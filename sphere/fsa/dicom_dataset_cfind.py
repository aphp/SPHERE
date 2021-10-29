"""
Search DICOM ans return list dataset
"""
# pylint:disable=eval-used, exec_used, unused-argument
import ast

from pydicom.dataset import Dataset

from sphere.dicmeta.requests.study_request import StudyRequest
from sphere.dicmeta.requests.patient_request import PatientRequest
from sphere.dicmeta.requests.series_request import SeriesRequest
from sphere.dicmeta.database_pacs import DatabasePACS
from sphere import settings
from sphere.utilities.dicom_utils import all_dicom_instance_path
from sphere.utilities.utils_database import check_db_pacs, read_copy_extended_db
from sphere.pacs.dict_cfind import DICT_SEARCH_FIND
from sphere.logs.logs import LOG_TRANSACTION


class DicomDatasetCFind():
    """ return list dataset of DICOM """
    def __init__(self, db_pacs=None):
        self.db_pacs = DatabasePACS() if db_pacs is None else db_pacs

        self.study_request = StudyRequest(self.db_pacs)
        self.patient_request = PatientRequest(self.db_pacs)
        self.series_request = SeriesRequest(self.db_pacs)
        self.all_dicom = ['*', '', '?', 'None']
        self.__search_file = "The search is done in the file : \n"
        self.__search_database = "The search is done in the database : \n"
        self.dict_extended = read_copy_extended_db()

    @staticmethod
    def check_attribute_dicom(ds, keyword, parents=None):
        """
        Create dataset

        :param ds: The dataset
        :type ds: :py:class:`pydicom.dataset.Dataset`
        :param keyword: The keyword of the dicom
        :type keyword: str
        :param parents: The parents of tag
        :type parents: str
        """
        try:
            if parents:
                parents_list_tags = parents.split(',')
                list_res_p = []
                for p_tag in parents_list_tags:
                    list_res_p.extend([str([p_tag[:4], p_tag[4:]]), str([0])])
                res = ''.join(list_res_p)[:-3]  # join and delete the last three

                return eval("ds." + res + ".value[0]." + keyword)
            else:
                return eval("ds." + keyword)
        except AttributeError:
            LOG_TRANSACTION.info("'dataset' object has no attribute %s", keyword)
            return None
        except Exception as exc:
            LOG_TRANSACTION.exception(exc)

    def create_dataset_db(self, data, query_model):
        """
        Create dataset

        :param data: The dataset if search with folder or the model
            if search with database
        :type data:
            :py:class:`sphere.dicmeta.models.patient_model.PatientModel` or
            :py:class:`sphere.dicmeta.models.study_model.StudyModel` or
            :py:class:`sphere.dicmeta.models.series_model.SeriesModel`
        :param query_model: the query model

            list of possible value of query_model:
                - PATIENT
                - STUDY
                - SERIES
        :type query_model: str
        :return: dataset
        :rtype: :py:class:`pydicom.dataset.Dataset`
        """
        identifier = Dataset()

        if query_model == "STUDY":
            identifier.StudyInstanceUID = data.studyUID
            identifier.PatientID = data.patientID
            identifier.StudyDate = data.dateStudy
            identifier.AccessionNumber = data.accessionNumber
            identifier.InstitutionName = data.institutionName
            identifier.StudyDescription = data.studyDescription
            self.add_attribute_extended_db(data, identifier, 'study', 'field_name')

            if settings.SEND_EXTENDED_DB and self.dict_extended and \
                    'study' in self.dict_extended.keys():
                # Patient
                res_p = self.patient_request.get_by_patient_id(
                    data.patientID)
                identifier.PatientName = res_p.patientName
                identifier.PatientBirthDate = res_p.patientBirthDate

        elif query_model == "PATIENT":  # PATIENT
            identifier.PatientName = data.patientName
            identifier.PatientID = data.patientID
            identifier.PatientSex = data.patientSex
            identifier.PatientBirthDate = data.patientBirthDate

            self.add_attribute_extended_db(data, identifier, 'patient', 'field_name')

        elif query_model == "SERIES":
            identifier.Modality = data.modality
            identifier.StudyInstanceUID = data.studyUID
            identifier.SeriesInstanceUID = data.seriesUID
            identifier.SeriesDescription = data.seriesDescription
            self.add_attribute_extended_db(data, identifier, 'series', 'field_name')

        return identifier

    def add_attribute_extended_db(self, data, identifier, table_name, key_name):
        """
        Add attribute in dataset 'indentifier'

        :param data: The dataset if search with folder or the model
            if search with database
        :type data: :py:class:`pydicom.dataset.Dataset` or
            :py:class:`sphere.dicmeta.models.patient_model.PatientModel` or
            :py:class:`sphere.dicmeta.models.study_model.StudyModel` or
            :py:class:`sphere.dicmeta.models.series_model.SeriesModel`
        :param identifier: The dataset
        :type identifier: :py:class:`pydicom.dataset.Dataset`
        :param table_name: The table name

            list of possible value:
                    - patient
                    - study
                    - series
        :type table_name: str
        :param key_name: The key name

            list of possible value:
                    - field_name
                    - keyword
        :type key_name: str
        """
        if settings.SEND_EXTENDED_DB and self.dict_extended and \
                table_name in self.dict_extended.keys():
            for tag, dic in self.dict_extended[table_name].items():
                try:
                    if key_name == 'field_name':  # with database
                        value = eval('data.' + dic[key_name])
                    else:  # keyword  no database so with file system
                        if 'parents' in dic:
                            value = self.check_attribute_dicom(data, dic[key_name], dic['parents'])
                        else:
                            value = self.check_attribute_dicom(data, dic[key_name])
                    var = self.create_var(value, dic)
                    if var:
                        exec(var)
                except Exception as exc:
                    LOG_TRANSACTION.exception("%s: %s \n %s", key_name, dic[key_name], exc)

    @staticmethod
    def create_var(value, dic):
        """
        Create variable

        :param value: Tha value of keyword (if dataset)or attribute (if models)
        :type value: str, int or float
        :param dic: The dictionary of all attribute (patient, study, or series)
        :type dic: dict
        :return:
        :rtype: str
        """
        var = ''
        if value is not None:
            if dic["value_representations"] == "SQ":
                LOG_TRANSACTION.warning("we cannot send this attributes '%s' "
                                        "because the value is equal to 'SQ'",
                                        dic["keyword"])
            elif dic["value_representations"] in ["DS", "FL", "FD", "IS", "OF",
                                                  "OW", "SL", "SS", "UL", "US",
                                                  "US or SS"]:
                # type float, int and Double
                var = "identifier." + dic["keyword"] + ' = ' + str(value)
            else:
                var = "identifier." + dic["keyword"] + ' = "' + str(value) + '"'
        else:
            LOG_TRANSACTION.warning("This attribute '%s' does not exists. So "
                                    "he was not sent.", dic["keyword"])

        return var

    def get_list_dataset_source(self, query_model, dict_find_fs):
        """
        Search dataset in file and return list dataset

        :param query_model: The query model

            list of possible value of query_model:
                - PATIENT
                - STUDY
                - SERIES
        :type query_model: str
        :param dict_find_fs: The dict find fs
        :type dict_find_fs: dict
        :return: list dataset
        :rtype: list [:py:class:`pydicom.dataset.Dataset`]
        """
        list_ds = all_dicom_instance_path(settings.FS_PATH_STORAGE, "list_ds")
        list_dataset_source = []
        string = ""
        if dict_find_fs:
            for keyword, value in dict_find_fs.items():
                string = string + " dataset." + keyword + " == '" + value + "' and"
            string = string[:-3]  # delete and
        else:
            string = "True"
        list_uid = []
        for dataset in list_ds:
            if query_model == "PATIENT":
                uid = dataset.PatientID
            elif query_model == "STUDY":
                uid = dataset.StudyInstanceUID
            else:  # SERIES
                uid = dataset.SeriesInstanceUID

            if eval(string) and uid not in list_uid:
                list_uid.append(uid)
                list_dataset_source.append(dataset)
        print("list_uid = {}".format(list_uid))

        list_dataset_target = []
        for dataset_source in list_dataset_source:
            list_dataset_target.append(
                self.create_dataset_fs(dataset_source, query_model))
        return list_dataset_target

    def create_dataset_fs(self, dataset_source, query_model):
        """
        Create dataset

        :param dataset_source: The dataset if search with folder
        :type dataset_source: :py:class:`pydicom.dataset.Dataset`
        :param query_model: the query model

            list of possible value of query_model:
                - PATIENT
                - STUDY
                - SERIES
        :type query_model: str
        :return: dataset
        :rtype: :py:class:`pydicom.dataset.Dataset`
        """
        dataset_target = Dataset()

        if query_model == "STUDY":
            dataset_target.StudyInstanceUID = self.check_attribute_dicom(dataset_source, 'StudyInstanceUID')
            dataset_target.PatientID = self.check_attribute_dicom(dataset_source, 'PatientID')
            dataset_target.ProtocolName = self.check_attribute_dicom(dataset_source, 'ProtocolName')

            self.add_attribute_extended_db(dataset_source, dataset_target, 'study', 'keyword')

        elif query_model == "PATIENT":
            dataset_target.PatientName = self.check_attribute_dicom(dataset_source, 'PatientName')
            dataset_target.PatientID = self.check_attribute_dicom(dataset_source, 'PatientID')
            dataset_target.PatientSex = self.check_attribute_dicom(dataset_source, 'PatientSex')
            dataset_target.PatientBirthDate = self.check_attribute_dicom(dataset_source, 'PatientBirthDate')

            self.add_attribute_extended_db(dataset_source, dataset_target, 'patient', 'keyword')

        elif query_model == "SERIES":
            dataset_target.Modality = self.check_attribute_dicom(dataset_source, 'Modality')
            dataset_target.StudyInstanceUID = self.check_attribute_dicom(dataset_source, 'StudyInstanceUID')
            dataset_target.SeriesInstanceUID = self.check_attribute_dicom(dataset_source, 'SeriesInstanceUID')
            dataset_target.SeriesDescription = self.check_attribute_dicom(dataset_source, 'SeriesDescription')

            self.add_attribute_extended_db(dataset_source, dataset_target, 'series', 'keyword')

        return dataset_target

    def get_dict_find(self, dataset, query_model):
        """
        Get dict find

        :param dataset: The dataset
        :type dataset: :py:class:`pydicom.dataset.Dataset`
        :param query_model: The query model

            list of possible value of query_model:
                - PATIENT
                - STUDY
                - SERIES
        :type query_model: str
        :return: The dict
        :rtype: dict
        """
        dict_find_db = {}
        dict_find_fs = {}
        dict_uid = DICT_SEARCH_FIND['UID']
        if "PATIENT" == query_model:
            dict_search = {**DICT_SEARCH_FIND['PATIENT'], **dict_uid}
        elif "STUDY" == query_model:
            dict_search = {**DICT_SEARCH_FIND['STUDY'], **dict_uid}
        else:
            dict_search = {**DICT_SEARCH_FIND['SERIES'], **dict_uid}

        for var, keyword in dict_search.items():
            if keyword in dataset:
                value = str(eval("dataset."+keyword))
                if value and value not in self.all_dicom:
                    dict_find_db[var] = value
                    dict_find_fs[keyword] = value

        LOG_TRANSACTION.info("dict_find_db = %s", dict_find_db)
        LOG_TRANSACTION.info("dict_find_fs = %s", dict_find_fs)

        return dict_find_db, dict_find_fs

    def ds_found(self, dataset, query_model, search_in_files):
        """
        Return list of dataset

        :param dataset: The dataset
        :type dataset: :py:class:`pydicom.dataset.Dataset`
        :param query_model: The query model

            list of possible value of query_model:
                - PATIENT
                - STUDY
                - SERIES
        :type query_model: str
        :param search_in_files: search in files (True | False)
        :type: bool
        :return: List of dataset
        :rtype: list [:py:class:`pydicom.dataset.Dataset`]
        """
        list_dataset = []
        dict_find_db, dict_find_fs = self.get_dict_find(dataset, query_model)

        try:
            # if connection db PACS okay
            if check_db_pacs():
                result = None
                if query_model == "PATIENT":
                    if dict_find_db:
                        result = self.patient_request.get_all_patient_with_filter(dict_find_db)
                    else:  # All patient
                        result = self.patient_request.get_all()
                elif query_model == "STUDY":
                    if dict_find_db:
                        result = self.study_request.get_all_study_with_filter(dict_find_db)
                    else:  # All study
                        result = self.study_request.get_all()
                elif query_model == "SERIES":
                    if dict_find_db:
                        result = self.series_request.get_all_series_with_filter(dict_find_db)
                    else:  # All series
                        result = self.series_request.get_all()
                else:
                    LOG_TRANSACTION.error(
                        'We have not yet deal with the case where '
                        'query_model= %s', query_model)

                if result:
                    LOG_TRANSACTION.info(self.__search_database)
                    # use by tests to check by what type of search launch
                    # the find
                    print(self.__search_database)  # use by test
                    LOG_TRANSACTION.debug("Result of query = %s", result)

                    list_dataset = []
                    if isinstance(result, list):
                        for element in result:
                            list_dataset.append(
                                self.create_dataset_db(element, query_model))
                    else:
                        list_dataset.append(
                            self.create_dataset_db(result, query_model))

            elif search_in_files:  # check in file system
                LOG_TRANSACTION.warning(
                    "We are allowed to search in the files if the database is "
                    "empty or if there is a connection problem")
                LOG_TRANSACTION.info(self.__search_file)
                # use by tests to check by what type of search launch the find
                print(self.__search_file)  # use by test

                list_dataset = self.get_list_dataset_source(
                    query_model, dict_find_fs)
            else:
                LOG_TRANSACTION.critical(
                    "The database is empty or there is a connection problem "
                    "and we are not authorized to search in the files")
            message_log = "Number of {0} : {1}".format(query_model,
                                                       len(list_dataset))
            LOG_TRANSACTION.info(message_log)
            return list_dataset
        except Exception as error:
            LOG_TRANSACTION.warning(error)
            LOG_TRANSACTION.info(self.__search_file)
            # use by tests to check by what type of search launch the find
            print(self.__search_file)  # use by test
            list_dataset = self.get_list_dataset_source(
                query_model, dict_find_fs)
            print("\t Number of {0} is {1}".format(query_model,
                                                   len(list_dataset)))
            return list_dataset
