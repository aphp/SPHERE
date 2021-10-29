"""
Search the paths of all DICOM
"""
from sphere.dicmeta.requests.file_storage_metadata_request import FileStorageMetadataDicomRequest
from sphere.dicmeta.database_pacs import DatabasePACS
from sphere import settings
from sphere.utilities.dicom_utils import all_dicom_instance_path
from sphere.utilities.utils_database import check_db_pacs
from sphere.logs.logs import LOG_TRANSACTION


class DicomPathCMove:
    """
    Returns the path of all DICOM files for a study
    """
    def __init__(self, db_pacs=None):
        self.db_pacs = DatabasePACS() if db_pacs is None else db_pacs
        self.file_storage_metadata_request = FileStorageMetadataDicomRequest(self.db_pacs)
        # self.ds = ds
        self.all_dicom = ['*', '', '?']
        self.__search_file = "The search is done in the file : \n"
        self.__search_database = "The search is done in the database : \n"

    @staticmethod
    def get_list_file_path(result, type_search):
        """
        Returns the path of all DICOM instances

        :param result: Result of search
        :type result: str
        :param type_search: Type of search (db or folder)

            list of possible value of type_search:
                - db
                - file

        :type type_search: str
        :return: List file path
        :rtype: dict
        """
        list_file_path = []
        if type_search == "db":
            for element in result:
                list_file_path.append(element.filePath)
        return list_file_path

    def get_list_dicom_path(
            self, patient_id, study_uid, series_uid, query_model):
        """
        Search the file in the file and return the path DICOM

        :param patient_id: The patient id
        :type patient_id: str
        :param study_uid: The study uid
        :type study_uid: str
        :param series_uid: The series uid
        :type series_uid: str
        :param query_model: The query model

        list of possible value of query_model:
                - PATIENT
                - STUDY
                - SERIES

        :type query_model: str
        :return: List path DICOM
        :rtype: list
        """
        def all_uid():
            return [path_dicom for path_dicom in dic_instance_path]

        dic_instance_path = all_dicom_instance_path(
            settings.FS_PATH_STORAGE, "dict")

        list_path_dicom = []
        if query_model == 'PATIENT':
            if patient_id:
                # all patients
                if patient_id in self.all_dicom and not study_uid \
                        and not series_uid:
                    list_path_dicom = all_uid()
                # One patient
                else:
                    for path, inst in dic_instance_path.items():
                        if inst.PatientID == patient_id:
                            list_path_dicom.append(path)
            else:
                list_path_dicom = all_uid()
        elif query_model == 'STUDY':
            if study_uid:
                # all study
                if study_uid in self.all_dicom and not patient_id \
                        and not series_uid:
                    list_path_dicom = all_uid()
                # All study for a patient
                elif study_uid in self.all_dicom and patient_id \
                        and not series_uid:
                    for path, inst in dic_instance_path.items():
                        if inst.PatientID == patient_id:
                            list_path_dicom.append(path)
                # One study
                else:
                    for path, inst in dic_instance_path.items():
                        if inst.StudyInstanceUID == study_uid:
                            list_path_dicom.append(path)
            else:
                list_path_dicom = all_uid()

        elif query_model == 'SERIES':
            if series_uid:
                # All series
                if series_uid in self.all_dicom and not patient_id \
                        and not study_uid:
                    list_path_dicom = all_uid()
                # All series for a patient
                elif series_uid in self.all_dicom and patient_id:
                    for path, inst in dic_instance_path.items():
                        if inst.PatientID == patient_id:
                            list_path_dicom.append(path)
                # All series for a study
                elif series_uid in self.all_dicom and study_uid:
                    for path, inst in dic_instance_path.items():
                        if inst.StudyInstanceUID == study_uid:
                            list_path_dicom.append(path)
                # One series
                else:
                    for path, inst in dic_instance_path.items():
                        if inst.SeriesInstanceUID == series_uid:
                            list_path_dicom.append(path)
            else:
                list_path_dicom = all_uid()
        else:
            LOG_TRANSACTION.error("The query model: %s not exits", query_model)

        return list_path_dicom

    # pylint: disable=invalid-name, no-else-return
    def path_found(self, ds, query_model):
        """
        Returns the path of all DICOM files

        :param ds: The dataset
        :type ds: str
        :param query_model: Query retrieve level DICOM

        list of possible value of query_model:
                - ``PATIENT``
                - ``STUDY``
                - ``SERIES``

        :type query_model: str
        :return: List of DICOM file paths
        :rtype: list
        """

        patient_id = ds.PatientID if 'PatientID' in ds else ''
        study_uid = ds.StudyInstanceUID if 'StudyInstanceUID' in ds else ''
        series_uid = ds.SeriesInstanceUID if 'SeriesInstanceUID' in ds else ''

        try:
            # if connection db PACS okay
            if check_db_pacs():
                if query_model == "PATIENT":
                    if patient_id not in self.all_dicom:  # If one patient
                        result =\
                            self.file_storage_metadata_request.get_by_patient_id(
                                patient_id)
                    else:  # If all patient
                        result = self.file_storage_metadata_request.get_all()
                elif query_model == "STUDY":
                    if patient_id:  # all study for a patient
                        result =\
                            self.file_storage_metadata_request.get_by_patient_id(
                                patient_id)
                    elif study_uid not in self.all_dicom:  # If one study
                        result = self.file_storage_metadata_request.get_by_study_uid(
                            study_uid)
                    else:  # If all study
                        result = self.file_storage_metadata_request.get_all()

                elif query_model == "SERIES":
                    # all series for a patient
                    if patient_id:
                        result =\
                            self.file_storage_metadata_request.get_by_patient_id(
                                patient_id)
                    # all series for a study
                    elif study_uid:
                        result = \
                            self.file_storage_metadata_request.get_by_study_uid(
                                study_uid)
                    elif series_uid not in self.all_dicom:  # If one series
                        result = \
                            self.file_storage_metadata_request.get_by_series_uid(
                                series_uid)
                    else:  # If all series
                        result = self.file_storage_metadata_request.get_all()
                else:
                    LOG_TRANSACTION.error(
                        'Error: we have not yet deal with the case where '
                        'query_model= %s', query_model)
                    return None
                print(self.__search_database)
                LOG_TRANSACTION.info(self.__search_database)
                if result:
                    return self.get_list_file_path(result, "db")
                else:
                    list_path_dicom = []

            else:  # check in file system
                print(self.__search_file)
                LOG_TRANSACTION.info(self.__search_file)
                list_path_dicom = self.get_list_dicom_path(
                    patient_id, study_uid, series_uid, query_model)
            msg = "\t Number of {0} : {1}".format(query_model,
                                                  len(list_path_dicom))
            print(msg)
            LOG_TRANSACTION.info(msg)
            return list_path_dicom
        except Exception as exc:
            LOG_TRANSACTION.exception(exc)
            print(self.__search_file)
            list_path_dicom = self.get_list_dicom_path(
                patient_id, study_uid, series_uid, query_model)
            msg = "\t Number of {0} : {1}".format(query_model,
                                                  len(list_path_dicom))
            print(msg)
            LOG_TRANSACTION.info(msg)
            return list_path_dicom
