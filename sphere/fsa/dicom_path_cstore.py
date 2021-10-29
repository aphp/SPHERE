"""
Search the paths of the instances for a list of patients, studies, or series
"""
# pylint: disable=broad-except
from sphere.dicmeta.requests.patient_request import PatientRequest
from sphere.dicmeta.requests.study_request import StudyRequest
from sphere.dicmeta.requests.series_request import SeriesRequest
from sphere.dicmeta.requests.file_storage_metadata_request import FileStorageMetadataDicomRequest
from sphere.dicmeta.database_pacs import DatabasePACS
from sphere import settings
from sphere.utilities.utils_database import check_db_pacs
from sphere.logs.logs import LOG_TRANSACTION


class DicomPathCStore:
    def __init__(self):
        self.db_pacs = DatabasePACS()
        self.patient_request = PatientRequest(self.db_pacs)
        self.study_request = StudyRequest(self.db_pacs)
        self.series_request = SeriesRequest(self.db_pacs)
        self.file_storage_metadata_request = FileStorageMetadataDicomRequest(self.db_pacs)

    @staticmethod
    def get_list_uid(result, type_uid):
        """
        Get list uid

        :param result: List of uids (patient_id, study_uid, series_uid or instances_uid)
        :type result: list
        :param type_uid: Type uid
        :type type_uid: str

            list of possible value:
                - ``patients``
                - ``studies``
                - ``series``
                - ``instances``
        :return: List of uids
        :rtype: list [str]
        """
        LOG_TRANSACTION.info("You put * in the file so you want all "
                             "instances of the all %s", type_uid)
        list_uid = [lis[0] for lis in result]
        LOG_TRANSACTION.info('There are %s %s in the database', len(list_uid),
                             type_uid)
        return list_uid

    def all_paths(self, model_name, list_uid):
        """
        Start the send of file DICOM

        :param model_name: The model name from the list_uid
        :type model_name: str

            list of possible value:
                - ``patient``
                - ``study``
                - ``series``
                - ``instance``
        :param list_uid: List uid (patient, study, series)
        :type list_uid: list [str]
        """
        list_instance_path = []
        try:
            if check_db_pacs():  # if connection db PACS okay
                # ll : list in list of object storage_metadata_model
                if model_name == "patient":
                    if list_uid[0] == '*':
                        # All patient id
                        list_uid = self.get_list_uid(
                            self.patient_request.get_all_patient_id(),
                            "patients")
                    ll_smm = self.file_storage_metadata_request.get_by_patient_id_list(list_uid)
                elif model_name == "study":
                    if list_uid[0] == '*':
                        # All study uid
                        list_uid = self.get_list_uid(
                            self.study_request.get_all_study_uid(),
                            "studies")
                    ll_smm = self.file_storage_metadata_request.get_by_study_uid_list(list_uid)
                elif model_name == "series":
                    if list_uid[0] == '*':
                        # All series uid
                        list_uid = self.get_list_uid(
                            self.series_request.get_all_series_uid(),
                            "series")
                    ll_smm = self.file_storage_metadata_request.get_by_series_uid_list(list_uid)
                elif model_name == "instance":
                    if list_uid[0] == '*':
                        # All instances uid
                        list_uid = self.get_list_uid(
                            self.file_storage_metadata_request.get_all_instance_uid(),
                            "instances")
                    ll_smm = [self.file_storage_metadata_request.get_by_instance_uid_list(list_uid)]
                else:
                    LOG_TRANSACTION.critical('Error: we have not yet deal with '
                                             'the case where model_name= %s',
                                             model_name)
                    raise ValueError('Unexpected model_name: %s' % model_name)

                flat_list_sto_mm = [item for sublist in ll_smm for item in sublist]
                for objet_smm in flat_list_sto_mm:
                    list_instance_path.append(objet_smm.filePath)
            else:
                LOG_TRANSACTION.error("I can't connect to the database")
            return list_instance_path
        except Exception as exc:
            LOG_TRANSACTION.exception(exc)
            return list_instance_path
