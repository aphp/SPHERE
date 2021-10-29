""" Request for the table series"""
from sphere.dicmeta.requests.request import Request


class SeriesRequest(Request):
    """ Request for series models"""

    def __init__(self, db):
        super().__init__(db)

        self.modelTable = self.db.SeriesModel

    def get_by_patient_id_list(self, list_id, dict_format=False):
        """
        Get by patient id list

        :param list_id: The list of patient ID
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
        :return: The data
        """
        patient_id = self.check_instance(patient, model_name='PatientModel', key=None)

        return self.request(
            self.db.PatientModel.patientID == patient_id).join(self.modelTable.patient).all()

    def get_by_patient_name_list(self, list_id, dict_format=False):
        """
        Get by patient id list

        :param list_id: The list of patient ID
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

        :param patient: The Patient ID
        :type patient: str
        :return: The object of patient
        :rtype: list [:py:class:`sphere.dicmeta.models.dicom_models.patient_model.PatientModel`]
        """
        patientName = self.check_instance(
            patient, model_name='PatientModel', key='patientName')

        return self.request(self.db.PatientModel.patientName.contains(patientName)).join(self.modelTable.study).all()

    def get_by_study_uid_list(self, list_id, dict_format=False):
        """
        Get by study uid list

        :param list_id: The list of study UID
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

        :param study: The study UID
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

        :param list_id: The list of series UID
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
        :return: The object of series
        :rtype: :py:class:`sphere.dicmeta.models.dicom_models.series_model.SeriesModel`
        """
        uid = self.check_instance(series, model_name='SeriesModel')
        return self.request(self.db.SeriesModel.seriesUID == uid).first()

    def get_all_series_uid(self):
        """
        Get all series_uid in the database

        :return: List of series_uid
        :rtype: list [(str)]
        """
        return self.request_no_filter(self.db.SeriesModel.seriesUID).all()

    def get_all_series_with_filter(self, dict_filter):
        """
        Get all series with filter in database

        :param dict_filter: The filter
        :param dict_filter: dict
        :return: List of series
        :rtype: list [(str)]
        """
        if "patientID" in dict_filter or "studyUID" in dict_filter:
            if "studyUID" in dict_filter:
                study_uid = dict_filter.pop('studyUID')
                result = self.request(
                    self.db.StudyModel.studyUID == study_uid).join(
                    self.modelTable.study).all()
            else:  # "patientID" in dict_filter
                patient_uid = dict_filter.pop('patientID')
                result = self.request(
                    self.db.PatientModel.patientID == patient_uid).join(
                    self.modelTable.patient).all()
            if dict_filter:
                list_series_uid = []
                if isinstance(result, list):
                    for obj in result:
                        list_series_uid.append(obj.seriesUID)
                else:
                    list_series_uid.append(result.seriesUID)
                dict_filter['seriesUID'] = list_series_uid
                result = self.request_filter_like(self.modelTable, dict_filter).all()
        else:
            result = self.request_filter_like(self.modelTable, dict_filter).all()
        return result
