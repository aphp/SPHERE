""" Request for the table patient"""
from sphere.dicmeta.requests.request import Request


class PatientRequest(Request):
    """ Request for patient models"""

    def __init__(self, db):
        super().__init__(db)

        self.modelTable = self.db.PatientModel

    def get_by_patient_id_list(self, list_id, dict_format=False):
        """
        Get by patient id list

        :param list_id: List ids
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
        Return line of table patient where patient_id equal id

        :param patient: The patient ID
        :type patient: str
        :return: The object of patient
        :rtype: :py:class:`sphere.dicmeta.models.dicom_models.patient_model.PatientModel`
        """
        patient_id = self.check_instance(
            patient, model_name='PatientModel', key=None)
        return self.request(
            self.db.PatientModel.patientID == patient_id).first()

    def get_by_patient_name_list(self, list_id, dict_format=False):
        """
        Get by patient name list

        :param list_id: The list ids
        :type list_id: list
        :param dict_format: Do you want to return the result to the dictionary
            format (True | False)
        :type dict_format: bool, optional
        :return: The object patient
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
        patient_name = self.check_instance(
            patient, model_name='PatientModel', key='patientName')

        return self.request(
            self.db.PatientModel.patientName.contains(patient_name)).all()

    def get_by_study_uid_list(self, list_id, dict_format=False):
        """
        Get by study uid list

        :param list_id: The list ids
        :type list_id: list
        :param dict_format: Do you want to return the result to the dictionary
            format (True | False)
        :type dict_format: bool, optional
        :return: List of study object
        :rtype: list [:py:class:`sphere.dicmeta.models.dicom_models.study_model.StudyModel`]
        """
        return self.get_by_list(list_id=list_id, func=self.get_by_study_uid,
                                dict_format=dict_format)

    # You can send a study instance or studyUid
    def get_by_study_uid(self, study):
        """
        Get by study uid

        :param study: The study UID
        :type study: str
        :return: The object of study
        :rtype: :py:class:`sphere.dicmeta.models.dicom_models.study_model.StudyModel`
        """
        uid = self.check_instance(study, model_name='StudyModel')
        return self.request(
            self.db.StudyModel.studyUID == uid).join(self.modelTable.studies).first()

    def get_by_series_uid_list(self, list_id, dict_format=False):
        """
        Get by series uid list

        :param list_id: The list ids
        :type list_id: list
        :param dict_format: Do you want to return the result to the dictionary
            format (True | False)
        :type dict_format: bool, optional
        :return: The object of series
        :rtype:
        """
        return self.get_by_list(list_id=list_id, func=self.get_by_series_uid,
                                dict_format=dict_format)

    def get_by_series_uid(self, series):
        """
        Get by series uid

        :param series: The series UID
        :return: The object of series
        :rtype: :py:class:`sphere.dicmeta.models.dicom_models.series_model.SeriesModel`
        """
        uid = self.check_instance(series, model_name='SeriesModel')
        return self.request(
            self.db.SeriesModel.seriesUID == uid).join(self.modelTable.series).first()

    def get_all_patient_id(self):
        """
        Get all patient_id in the database

        :return: List of patient_id
        :rtype: list [(str)]
        """
        return self.request_no_filter(self.db.PatientModel.patientID).all()

    def get_all_patient_with_filter(self, dict_filter):
        """
        Get all patient with filter in database

        :param dict_filter: The series UID
        :param dict_filter: dict
        :return: List of patient_id
        :rtype: list [(str)]
        """
        if "studyUID" in dict_filter or "seriesUID" in dict_filter:
            if "seriesUID" in dict_filter:
                series_uid = dict_filter.pop('seriesUID')
                result = self.request(
                    self.db.SeriesModel.seriesUID == series_uid).join(
                    self.modelTable.series).first()
            else:  # "studyUID" in dict_filter
                study_uid = dict_filter.pop('studyUID')
                result = self.request(
                    self.db.StudyModel.studyUID == study_uid).join(
                    self.modelTable.studies).first()
            if dict_filter:
                dict_filter['patientID'] = result.patientID
                result = self.request_filter_like(self.modelTable, dict_filter).all()
        else:
            result = self.request_filter_like(self.modelTable, dict_filter).all()
        return result
