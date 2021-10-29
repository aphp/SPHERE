"""
Create the query dataset with pydicom
"""
# pylint: disable=invalid-name
from pydicom.dataset import Dataset

from sphere.utilities.file import read_file_return_list
from sphere.dicmeta.database import Database
from sphere.dicmeta.models.dicom_models.patient_model import PatientModel
from sphere.dicmeta.models.dicom_models.study_model import StudyModel
from sphere.dicmeta.models.dicom_models.series_model import SeriesModel

from sphere.dicmeta.database_pacs import DatabasePACS
from sphere.logs.logs import LOG_TRANSACTION


class QueryDataset:
    """ create the query dataset"""

    def __init__(self):
        self.qr_level = 'STUDY'

    @staticmethod
    def create_dataset(data_set, **kwargs):
        """
        Create dataset

        :param data_set: The dataset
        :type data_set: str
        :param kwargs: The arguments of the cfind or cmove command.
            Kwargs comments in the function "cfind_action() or cmove_action()"
            exists in "parser.py"
        :type kwargs: dict

        """
        LOG_TRANSACTION.info("Start Create dataset")
        patient_id = kwargs['patient_id'] if 'patient_id' in kwargs and kwargs[
            'patient_id'] is not None else None

        study_uid = kwargs['study_uid'] if 'study_uid' in kwargs and kwargs[
            'study_uid'] is not None else None

        series_uid = kwargs['series_uid'] if 'series_uid' in kwargs and kwargs[
            'series_uid'] is not None else None

        if kwargs["qr_level"] == "PATIENT":
            if patient_id:
                data_set.PatientID = patient_id
                if study_uid and not series_uid:
                    data_set.StudyInstanceUID = study_uid
                elif study_uid and series_uid:
                    data_set.StudyInstanceUID = study_uid
                    data_set.SeriesInstanceUID = series_uid
                elif series_uid:
                    data_set.SeriesInstanceUID = series_uid
            elif study_uid:
                data_set.PatientID = "*"
                data_set.StudyInstanceUID = study_uid
            elif series_uid:
                data_set.PatientID = "*"
                data_set.SeriesInstanceUID = series_uid
            else:
                data_set.PatientID = "*"
        elif kwargs["qr_level"] == "STUDY":
            if study_uid:
                data_set.StudyInstanceUID = study_uid
                if patient_id:
                    data_set.PatientID = patient_id
                elif series_uid:
                    data_set.SeriesInstanceUID = series_uid
            elif patient_id:
                data_set.StudyInstanceUID = '*'
                data_set.PatientID = patient_id
            elif series_uid:
                data_set.StudyInstanceUID = "*"
                data_set.SeriesInstanceUID = series_uid
            else:
                data_set.StudyInstanceUID = '*'

        elif kwargs["qr_level"] == "SERIES":
            if series_uid:
                data_set.SeriesInstanceUID = series_uid
                if patient_id:
                    data_set.PatientID = patient_id
                elif study_uid:
                    data_set.StudyInstanceUID = study_uid
            elif patient_id:
                data_set.PatientID = patient_id
                data_set.SeriesInstanceUID = '*'
            elif study_uid:
                data_set.SeriesInstanceUID = "*"
                data_set.StudyInstanceUID = study_uid
            else:
                data_set.SeriesInstanceUID = '*'
        else:
            LOG_TRANSACTION.critical("We can't search with this qr_level '%s'",
                                     kwargs["qr_level"])
        LOG_TRANSACTION.info("End Create dataset")

    @staticmethod
    def __display(list_dataset):
        """
        Display list dataset DICOM

        :param list_dataset: The list of dataset
        :type list_dataset: list [:py:class:`pydicom.dataset.Dataset`]
        """
        for dataset in list_dataset:
            print('\nqr_level     :' + str(dataset.QueryRetrieveLevel))
            if 'StudyInstanceUID' in dataset:
                print('study_uid    :' + str(dataset.StudyInstanceUID))
            if 'PatientID' in dataset:
                print('patient_id   :' + str(dataset.PatientID))
            if "SeriesInstanceUID" in dataset:
                print('SeriesInstanceUID  :' + str(dataset.SeriesInstanceUID))
            print("*" * 40)
        print('\n\n')

    @staticmethod
    def list_ds_patient(list_patient_id, qr_level, reload_uid):
        """
        Create list dataset of all patient_uid

        :param list_patient_id: List patient id
        :type list_patient_id: list
        :param qr_level: The he query level
                    The possible value: ``PATIENT``
        :type qr_level: str
        :param reload_uid: If True reload uid else no
        :type reload_uid: bool
        :return: The list of dataset
        :rtype: list [:py:class:`pydicom.dataset.Dataset`]
        """
        list_ds = []
        for patient_uid in list_patient_id:
            data_set = Dataset()
            data_set.QueryRetrieveLevel = qr_level
            if reload_uid is not True:
                db = Database()
                exist = db.check_uid_exist(patient_uid, PatientModel(), "patientID")
                if not exist:
                    data_set.PatientID = patient_uid
                    list_ds.append(data_set)
            else:
                data_set.PatientID = patient_uid
                list_ds.append(data_set)
        return list_ds

    @staticmethod
    def list_ds_study(list_study_uid, qr_level, reload_uid):
        """
        Create list dataset of all study_uid

        :param list_study_uid: List study uid
        :type list_study_uid: list [str]
        :param qr_level: The he query level
                    The possible value: ``STUDY``
        :type qr_level: str
        :param reload_uid: If True reload uid else no
        :type reload_uid: bool
        :return: The list of dataset
        :rtype: list [:py:class:`pydicom.dataset.Dataset`]
        """
        list_ds = []
        for study_uid in list_study_uid:
            data_set = Dataset()
            data_set.QueryRetrieveLevel = qr_level
            if reload_uid is not True:
                db = Database()
                exist = db.check_uid_exist(study_uid, StudyModel(), "studyUID")
                if not exist:
                    data_set.StudyInstanceUID = study_uid
                    list_ds.append(data_set)
            else:
                data_set.StudyInstanceUID = study_uid
                list_ds.append(data_set)
        return list_ds

    @staticmethod
    def list_ds_series(list_series_uid, qr_level, reload_uid):
        """
        Create list dataset of all series_uid

        :param list_series_uid: List series uid
        :type list_series_uid: list[str]
        :param qr_level: The he query level
                    The possible value: ``SERIES``
        :type qr_level: str
        :param reload_uid: If True reload uid else no
        :type reload_uid: bool
        :return: The list of dataset
        :rtype: list [:py:class:`pydicom.dataset.Dataset`]
        """
        list_ds = []
        for series_uid in list_series_uid:
            data_set = Dataset()
            data_set.QueryRetrieveLevel = qr_level
            if reload_uid is not True:
                db = Database()
                exist = db.study_uid_exist(series_uid, SeriesModel(), "seriesUID")
                if not exist:
                    data_set.SeriesInstanceUID = series_uid
                    list_ds.append(data_set)
            else:
                data_set.SeriesInstanceUID = series_uid
                list_ds.append(data_set)
        return list_ds

    def create_query_ds(self, **kwargs):
        """
        Create query dataset for cfind or cmove

        :param kwargs: The arguments of the cfind or cmove command.
            Kwargs comments in the function "cfind_action() or cmove_action()"
            exists in "parser.py"
        :type kwargs: dict
        :return: The dataset
        :rtype: list [:py:class:`pydicom.dataset.Dataset`] or :py:class:`pydicom.dataset.Dataset`
        """
        list_ds = []
        LOG_TRANSACTION.info("Start create query dataset for 'c%s'",
                             kwargs['action'])

        def qr_level():
            n_data_set = Dataset()
            if 'qr_level' in kwargs and kwargs['qr_level']is not None:
                self.qr_level = kwargs['qr_level']
            n_data_set.QueryRetrieveLevel = self.qr_level
            return n_data_set

        if 'file_uid' in kwargs and kwargs['file_uid'] is not None:
            qr_level = str(kwargs['qr_level'])
            file_path = str(kwargs['file_uid'])
            reload_study = bool(kwargs['reload_study'])
            list_uid = read_file_return_list(file_path)

            if list_uid:
                if qr_level == "PATIENT":
                    list_ds = self.list_ds_patient(list_uid, qr_level, reload_study)
                if qr_level == "STUDY":
                    list_ds = self.list_ds_study(list_uid, qr_level, reload_study)
                if qr_level == "SERIES":
                    list_ds = self.list_ds_series(list_uid, qr_level, reload_study)

            else:
                LOG_TRANSACTION.critical("This '%s' file is empty. So we can't "
                                         "launch cmove", file_path)
        elif 'db_study_uid' in kwargs and kwargs['db_study_uid'] is not None:
            if kwargs['db_study_uid'] == 'last':
                db_pacs = DatabasePACS()
                study_list_model = db_pacs.StudyListModel()
                id_list = db_pacs.get_max_value(study_list_model, 'id_list')
            else:
                try:
                    if kwargs['db_study_uid'].isnumeric():
                        id_list = kwargs['db_study_uid']
                    else:
                        LOG_TRANSACTION.critical(
                            'The given param have to be an integer')
                        raise Exception('The given param have to be an integer')
                except Exception as error:
                    LOG_TRANSACTION.critical(error)
                    raise Exception(error)
            db_pacs = DatabasePACS()
            study_list_model = db_pacs.StudyListModel()
            study_list = db_pacs.get_model_filter(
                study_list_model, 'id_list', id_list)
            for row in study_list:
                data_set = qr_level()
                data_set.StudyInstanceUID = row[0]
                list_ds.append(data_set)
        else:
            data_set = qr_level()
            self.create_dataset(data_set, **kwargs)
            list_ds.append(data_set)

        self.__display(list_ds)
        LOG_TRANSACTION.info("End create query dataset for 'c%s'",
                             kwargs['action'])
        if kwargs["action"] == "find":
            LOG_TRANSACTION.debug("Cfind;  data_set= ")
            for line in data_set:
                LOG_TRANSACTION.debug(line)
            return data_set
        LOG_TRANSACTION.debug("Cmove; We have %s  dataset; list_ds= ",
                              len(list_ds))
        for dataset in list_ds:
            for line in dataset:
                LOG_TRANSACTION.debug(line)
        return list_ds
