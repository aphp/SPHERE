""" Request for the table file_storage_metadata_dicom"""
from .request import Request


class FileStorageMetadataDicomRequest(Request):

    def __init__(self, db):
        super().__init__(db)

        self.modelTable = self.db.FileStorageMetadataDicomModel

    def get_by_patient_id_list(self, list_id, dict_format=False):
        """
        Get by patient id list

        :param list_id: The list ids
        :type list_id: list
        :param dict_format: Do you want to return the result to the dictionary
            format (True | False)
        :type dict_format: bool, optional
        :return: List of patient object
        :rtype: list [:py:class:`sphere.dicmeta.models.dicom_models.patient_model.PatientModel`]
        """
        return self.get_by_list(list_id=list_id, func=self.get_by_patient_id,
                                dict_format=dict_format)

    def get_by_patient_id(self, patient):
        """
        Get by patient id

        :param patient: The patient ID
        :type patient: str
        :return: The object of patient
        :rtype: :py:class:`sphere.dicmeta.models.dicom_models.patient_model.PatientModel`
        """
        id = self.check_instance(patient, model_name='PatientModel', key=None)

        return self.request(self.db.PatientModel.patientID == id).join(self.modelTable.patient).all()

    def get_by_patient_name_list(self, list_id, dict_format=False):
        """
        Get by patient name list

        :param list_id: The list ids
        :type list_id: list
        :param dict_format: Do you want to return the result to the dictionary
            format (True | False)
        :type dict_format: bool, optional
        :return: List of patient object
        :rtype: list [:py:class:`sphere.dicmeta.models.dicom_models.patient_model.PatientModel`]
        """
        return self.get_by_list(list_id=list_id, func=self.get_by_patient_name,
                                dict_format=dict_format)

    def get_by_patient_name(self, patient):
        """
        Get by patient name

        :param patient: The patient ID
        :type patient: str
        :return: The object of patient
        :rtype: :py:class:`sphere.dicmeta.models.dicom_models.patient_model.PatientModel`
        """
        patientName = self.check_instance(
            patient, model_name='PatientModel', key='patientName')

        return self.request(
            self.db.PatientModel.patientName.contains(patientName).join(self.modelTable.patient)).all()

    def get_by_study_uid_list(self, list_id, dict_format=False):
        """
        Get by study uid list

        :param list_id: List of study uid
        :type list_id: list
        :param dict_format: Do you want to return the result to the dictionary
            format (True | False)
        :type dict_format: bool, optional
        :return: List of study object
        :rtype: list [:py:class:`sphere.dicmeta.models.dicom_models.study_model.StudyModel`]
        """
        return self.get_by_list(list_id=list_id, func=self.get_by_study_uid,
                                dict_format=dict_format)

    # You can send a study instanc or studyUid
    def get_by_study_uid(self, study):
        """
        Get by study uid

        :param study: Study UID
        :type study: str
        :return: The object of study
        :rtype: :py:class:`sphere.dicmeta.models.dicom_models.study_model.StudyModel`
        """
        uid = self.check_instance(study, model_name='StudyModel')
        return self.request(
            self.db.StudyModel.studyUID == uid).join(self.modelTable.study).all()

    def get_by_series_uid_list(self, list_id, dict_format=False):
        """
        Get by series uid list

        :param list_id: List of series UID
        :type list_id: list
        :param dict_format: Do you want to return the result to the dictionary
            format (True | False)
        :type dict_format: bool, optional
        :return: List of series object
        :rtype: list [:py:class:`sphere.dicmeta.models.dicom_models.series_model.SeriesModel`]
        """
        return self.get_by_list(list_id=list_id, func=self.get_by_series_uid,
                                dict_format=dict_format)

    def get_by_series_uid(self, series):
        """
        Get by series uid

        :param series: The series UID
        :type series: str
        :return: The object of series
        :rtype: :py:class:`sphere.dicmeta.models.dicom_models.series_model.SeriesModel`
        """
        uid = self.check_instance(series, model_name='SeriesModel')
        return self.request(self.db.SeriesModel.seriesUID == uid).join(self.modelTable.series).all()

    def get_by_instance_uid_list(self, list_id, dict_format=False):
        """
        Get by instance uid list

        :param list_id: List of instances UID
        :type list_id: list
        :param dict_format:
        :type dict_format: dict, optional
        :return: List of instance object
        :rtype: list [:py:class:`sphere.dicmeta.models.dicom_models.file_storage_metadata_model.FileStorageMetadataDicomModel`]
        """
        return self.get_by_list(list_id=list_id, func=self.get_by_instance_uid,
                                dict_format=dict_format)

    def get_by_instance_uid(self, instance):
        """
        Get by instance uid

        :param instance: The instances UID
        :type instance: str
        :return: The object of instance
        :rtype: :py:class:`sphere.dicmeta.models.dicom_models.file_storage_metadata_model.FileStorageMetadataDicomModel`
        """
        uid = self.check_instance(instance, model_name='FileStorageMetadataDicomModel')
        return self.request(self.db.FileStorageMetadataDicomModel.instanceUID == uid).first()

    def get_all_instance_uid(self):
        """
        Get all instance_uid in the database

        :return: List of instance_uid
        :rtype: list [(str)]
        """
        return self.request_no_filter(self.db.FileStorageMetadataDicomModel.instanceUID).all()