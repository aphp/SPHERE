""" Search for DICOM objects (QIDO-RS) """
import os
import sys
import json

import pydicom

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)


from sphere.dicmeta.database_pacs import DatabasePACS
from sphere.api_rest.api_sphere_dicomweb.utils import return_list_uid, \
    filter_dataset, get_group_element_number
from sphere.api_rest.api_sphere_dicomweb.metadata_tags_configuration import \
    get_filter_columns, QS_FILTERS, parse_metadata_configuration
from sphere.logs.logs import LOG_API_DICOMWEB


class SearchOrmSqlalchemy:
    """ Search with ORM SqlAlchemy:
     * All studies
     * All series of one study
     * All instance of one study
     * All instances of one study and series
     * All instances
     """
    def __init__(self, session):
        self.db_pacs = DatabasePACS()
        self.session = session
        file_storage_metadata_model = self.db_pacs.FileStorageMetadataDicomModel()
        self.table_fsm = file_storage_metadata_model.table_full_name()

    # ======== Instance ======== #
    def all_instances(self, offset, limit, filters, includefield):
        """
        Returns all instance
        # link: /qidors/instances

        :param offset: Number of results that should be skipped
        :type offset: int, optional
        :param limit: Maximum number of results that should be returned
        :type limit: int, optional
        :param filters: Search filter criteria as key-value pairs, where *key* is a keyword
            or a tag of the attribute and *value* is the expected value that
            should match
        :type filters: dict{str: Any}, optional
        :param includefield:  0-n includefield / {attributeID} pairs allowed,
            where "all" indicates that all available attributes should be
            included for each response.
        :type includefield: str, optional
        :return: Return list instance uid
        :rtype: list
        """
        list_path = False
        if filters:
            filters = self.get_filter_patient_id(filters)
            columns_filters = get_filter_columns(filters, 'Instance')
            result = self.request_filter_like(
                self.db_pacs.FileStorageMetadataDicomModel, columns_filters).all()[offset:offset + limit]
        else:
            result = self.session.query(
                self.db_pacs.FileStorageMetadataDicomModel.filePath).all()[
                     offset:offset + limit]

            list_path = True
        self.db_pacs.clear_session(self.session)
        return self.dataset_list(result, 'instance', includefield, list_path)

    def all_instances_of_one_study(self, study_uid, offset, limit, filters, includefield):
        """
        Returns all instance of one study
        # link: /qidors/studies/{StudyInstanceUID}/instances

        :param study_uid: The study uid
        :type study_uid: str
        :param offset: Number of results that should be skipped
        :type offset: int, optional
        :param limit: Maximum number of results that should be returned
        :type limit: int, optional
        :param filters: Search filter criteria as key-value pairs, where *key* is a keyword
            or a tag of the attribute and *value* is the expected value that
            should match
        :type filters: dict{str: Any}, optional
        :param includefield:  0-n includefield / {attributeID} pairs allowed,
            where "all" indicates that all available attributes should be
            included for each response.
        :type includefield: str, optional
        :return: Return list metadata dataset
        :rtype: list
        """
        list_path = False
        if filters:
            filters = self.get_filter_patient_id(filters)
            filters['StudyInstanceUID'] = study_uid
            columns_filters = get_filter_columns(filters, 'Instance')
            result = self.request_filter_like(
                self.db_pacs.FileStorageMetadataDicomModel, columns_filters).all()[offset:offset + limit]
        else:
            result = self.session.query(
                self.db_pacs.FileStorageMetadataDicomModel.filePath).filter(
                self.db_pacs.FileStorageMetadataDicomModel.studyUID == study_uid).all()[
                     offset:offset + limit]
            list_path = True
        self.db_pacs.clear_session(self.session)
        return self.dataset_list(result, 'instance', includefield, list_path)

    def all_instances_of_one_study_and_series(self, study_uid, series_uid, offset, limit, filters, includefield):
        """
        Returns all series of one study and series
        link: /qidors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/instances

        :param study_uid: The study uid
        :type study_uid: str
        :param series_uid: The series uid
        :type series_uid: str
        :param offset: Number of results that should be skipped
        :type offset: int, optional
        :param limit: Maximum number of results that should be returned
        :type limit: int, optional
        :param filters: Search filter criteria as key-value pairs, where *key* is a keyword
            or a tag of the attribute and *value* is the expected value that
            should match
        :type filters: dict{str: Any}, optional
        :param includefield:  0-n includefield / {attributeID} pairs allowed,
            where "all" indicates that all available attributes should be
            included for each response.
        :type includefield: str, optional
        :return: Return list metadata dataset
        :rtype: list
        """
        list_path = False
        if filters:
            filters = self.get_filter_patient_id(filters)
            filters['StudyInstanceUID'] = study_uid
            filters['SeriesInstanceUID'] = series_uid
            columns_filters = get_filter_columns(filters, 'Instance')
            result = self.request_filter_like(
                self.db_pacs.FileStorageMetadataDicomModel, columns_filters).all()[offset:offset + limit]
        else:
            result = self.session.query(
                self.db_pacs.FileStorageMetadataDicomModel.filePath).filter(
                self.db_pacs.FileStorageMetadataDicomModel.studyUID == study_uid).filter(
                self.db_pacs.FileStorageMetadataDicomModel.seriesUID == series_uid).all()[
                     offset:offset + limit]
            list_path = True
        self.db_pacs.clear_session(self.session)
        return self.dataset_list(result, 'instance', includefield, list_path)

    # ========= Series ========== #
    def all_series(self, offset, limit, filters, includefield):
        """
        Returns all series
        # link: /qidors/series

        :param offset: Number of results that should be skipped
        :type offset: int, optional
        :param limit: Maximum number of results that should be returned
        :type limit: int, optional
        :param filters: Search filter criteria as key-value pairs, where *key* is a keyword
            or a tag of the attribute and *value* is the expected value that
            should match
        :type filters: dict{str: Any}, optional
        :param includefield:  0-n includefield / {attributeID} pairs allowed,
            where "all" indicates that all available attributes should be
            included for each response.
        :type includefield: str, optional
        :return: Return list series uid
        :rtype: list
        """
        if filters:
            filters = self.get_filter_patient_id(filters)
            columns_filters = get_filter_columns(filters, 'Series')
            result = self.request_filter_like(
                self.db_pacs.SeriesModel, columns_filters).all()

            list_series_uid = self.get_list_uid(result, "series")
        else:
            result = self.session.query(self.db_pacs.SeriesModel.seriesUID).all()
            list_series_uid = return_list_uid(result)
        results = []
        for series_uid in list_series_uid[offset:offset + limit]:
            result = self.session.query(
                self.db_pacs.FileStorageMetadataDicomModel.filePath).filter(
                self.db_pacs.FileStorageMetadataDicomModel.seriesUID == series_uid).first()
            results.append(result)
        self.db_pacs.clear_session(self.session)
        return self.dataset_list(results, 'series', includefield, True)

    def all_series_of_one_study(self, study_uid, offset, limit, filters, includefield):
        """
        Returns all series of one study
        # link: /qidors/studies/{StudyInstanceUID}/series

        :param study_uid: The study uid
        :type study_uid: str
        :param offset: Number of results that should be skipped
        :type offset: int, optional
        :param limit: Maximum number of results that should be returned
        :type limit: int, optional
        :param filters: Search filter criteria as key-value pairs, where *key* is a keyword
            or a tag of the attribute and *value* is the expected value that
            should match
        :type filters: dict{str: Any}, optional
        :param includefield:  0-n includefield / {attributeID} pairs allowed,
            where "all" indicates that all available attributes should be
            included for each response.
        :type includefield: str, optional
        :return: Return list series uid
        :rtype: list
        """
        if filters:
            filters = self.get_filter_patient_id(filters)
            filters['StudyInstanceUID'] = study_uid
            columns_filters = get_filter_columns(filters, 'Instance')
            result = self.request_filter_like(self.db_pacs.SeriesModel, columns_filters).all()
        else:
            result = self.session.query(
                self.db_pacs.SeriesModel).filter(
                    self.db_pacs.SeriesModel.studyUID == study_uid).all()

        list_series_uid = self.get_list_uid(result, "series")
        results = []
        for series_uid in list_series_uid[offset:offset + limit]:
            result = self.session.query(
                self.db_pacs.FileStorageMetadataDicomModel.filePath).filter(
                self.db_pacs.FileStorageMetadataDicomModel.seriesUID == series_uid).first()
            results.append(result)
        return self.dataset_list(results, 'series', includefield, True)

    # ========= Studies ========= #
    def all_studies(self, offset, limit, filters, includefield):
        """
        Returns all studies in database

        # link: /qidors/studies
        :param offset: Number of results that should be skipped
        :type offset: int, optional
        :param limit: Maximum number of results that should be returned
        :type limit: int, optional
        :param filters: Search filter criteria as key-value pairs, where *key* is a keyword
            or a tag of the attribute and *value* is the expected value that
            should match
        :type filters: dict{str: Any}, optional
        :param includefield:  0-n includefield / {attributeID} pairs allowed,
            where "all" indicates that all available attributes should be
            included for each response.
        :type includefield: str, optional
        :return: Return list metadata dataset
        :rtype: list
        """
        if filters:
            filters = self.get_filter_patient_id(filters)
            columns_filters = get_filter_columns(filters, 'Study')
            result = self.request_filter_like(self.db_pacs.StudyModel, columns_filters).all()
        else:
            result = self.session.query(self.db_pacs.StudyModel.studyUID).all()

        list_studies_uid = self.get_list_uid(result, "study")
        results = []
        for study_uid in list_studies_uid[offset:offset + limit]:
            result = self.session.query(
                self.db_pacs.FileStorageMetadataDicomModel.filePath).filter(
                self.db_pacs.FileStorageMetadataDicomModel.studyUID == study_uid).first()
            results.append(result)
        self.db_pacs.clear_session(self.session)
        return self.dataset_list(results, 'study', includefield, True)

    # ====== Other Function ===== #
    def request_filter_like(self, model,  dict_filter):
        """
        Create request with filter

        :param model: The models

            list of possible value of model:
                - `sphere.dicmeta.models.dicom_models.patient_model.PatientModel`
                - `sphere.dicmeta.models.dicom_models.study_model.StudyModel`
                - `sphere.dicmeta.models.dicom_models.series_model.SeriesModel`
        :type model: :py:class:`sqlalchemy.ext.declarative.api.DeclarativeMeta`
        :param dict_filter: The dict filter request

            Example of dict_filter:
            | {
            |     'dateStudy': '20030505',
            |     'studyDescription': 'Brain*'
            | }

        :type dict_filter: dict
        :return: The query
        :rtype: :py:class:`sqlalchemy.orm.query.Query`
        """
        list_del_key = []
        list_string = []

        for key, value in dict_filter.items():
            print(key, value)
            if "*" in value or isinstance(value, list) or \
                    ('-' in value and key in ["dateStudy", "dateSeries"]):
                if "*" in value:  # Implement the ``like`` operator
                    search = value.replace('*', '%')
                    string = "model." + key + ".like('" + search + "')"
                elif isinstance(value, list):  # Implement the ``in_`` operator
                    string = "model." + key + ".in_(" + str(value) + ")"
                else:  # Implement the ``between`` operator
                    date = value.split('-')
                    string = "model." + key + ".between ('" \
                             + str(date[0]) + "', '" + str(date[1]) + "')"

                list_string.append(string)
                list_del_key.append(key)
        # remove the keys where we have filters ``like`` or ``in_``
        for key in list(set(list_del_key)):
            del dict_filter[key]

        query_filter = "self.session.query(model).filter_by(**dict_filter).filter("
        for st in list_string:
            query_filter = query_filter + st + ","
        query_filter = query_filter + ").distinct()"

        sqlalchemy_orm_query = eval(query_filter)
        return sqlalchemy_orm_query

    def get_filter_patient_id(self, filters):
        """
        Get filter of patient_id

        :param filters: column filters
        :type filters: dict
        :return: the filter patient_id
        :rtype: dict
        """
        filter_by_model = self.get_filter_by_model(filters)
        for model, filter_m in filter_by_model.items():
            if model == "Patient":
                result = self.get_result_query('Patient', filter_m, self.db_pacs.PatientModel)
            elif model == "Study":
                result = self.get_result_query('Study', filter_m, self.db_pacs.StudyModel)
            elif model == "Series":
                result = self.get_result_query('Series', filter_m, self.db_pacs.SeriesModel)
            else:  # model == "Instance"
                result = self.get_result_query('Instance', filter_m, self.db_pacs.FileStorageMetadataDicomModel)
            if 'PatientID' in filters:
                list_patient_uid = self.get_list_uid(result, "patient")
                patient_uid = filters['PatientID']
                if isinstance(patient_uid, str):
                    patient_uid = [patient_uid]

                set_patient_uid = set(list_patient_uid) & set(patient_uid)
                filters.clear()
                filters['PatientID'] = list(set_patient_uid)
            else:
                filters.clear()
                filters['PatientID'] = self.get_list_uid(result, "patient")

        return filters

    @staticmethod
    def get_filter_by_model(filters):
        """
        get filter by model

        :param filters: List of filters
        :type filters:dict
        :return:filter by model
        :rtype:dict
        """
        _a, _b, keyword_by_model, tag_by_model = parse_metadata_configuration()
        filter_by_model = {}
        for key, value in filters.items():
            if key in keyword_by_model:
                model = keyword_by_model[key]
            elif key in tag_by_model:
                model = tag_by_model[key]
            else:
                list_keyword_tag = list(keyword_by_model) + list(tag_by_model)
                print("This keyword or tag '{}' does not exists in {}".format(
                    key, list_keyword_tag))
                model = ""
            if model:
                if model in filter_by_model:
                    filter_by_model[model] = {**filter_by_model[model],
                                              **{key: value}}
                else:
                    filter_by_model[model] = {key: value}

        return filter_by_model

    @staticmethod
    def get_list_uid(result, level):
        """
        Get list patient_id, study_uid, series_uid or instance_uid

        :param result:
        :type result:
        :param level: The level

            The possible value:
                - ``patient``
                - ``study``
                - ``series``
                - ``instance``

        :type level: str
        :return: Return list of uid
        :rtype: list
        """
        list_uid = []
        for i in result:
            if level == "patient":
                list_uid.append(i.patientID)
            elif level == "study":
                list_uid.append(i.studyUID)
            elif level == "series":
                list_uid.append(i.seriesUID)
            elif level == "instance":
                list_uid.append(i.filePath)

        return list_uid

    def get_result_query(self, table, filter_m, model):
        """
        Get result of query

        :param table: The table name

            The possible value:
                    - ``Patient``
                    - ``Study``
                    - ``Series``
                    - ``Instance``
        :type table: str
        :param filter_m: The filter
        :type filter_m: dict
        :param model: The model

            The possible value:
                - ``sphere.dicmeta.models.dicom_models.patient_model.PatientModel``
                - ``sphere.dicmeta.models.dicom_models.study_model.StudyModel``
                - ``sphere.dicmeta.models.dicom_models.series_model.SeriesModel``
                - ``sphere.dicmeta.models.dicom_models.file_storage_metadata_model.FileStorageMetadataDicomModel``

        :type model: :py:class:`sqlalchemy.ext.declarative.api.DeclarativeMeta`
        :return: The result of query
        :rtype:list
        """
        columns_filters = get_filter_columns(filter_m, table)
        result = self.request_filter_like(model, columns_filters).all()
        return result

    def dataset_list(self, result, level, includefield="all", list_path=False):
        """
        Get metadata of dataset for study, series and instance

        :param result: The result
        :type result: list [object ``sphere.dicmeta.models.dicom_models.file_storage_metadata_model.FileStorageMetadataDicomModel``]
            or list [path]
        :param includefield:  0-n includefield / {attributeID} pairs allowed,
            where "all" indicates that all available attributes should be
            included for each response. default = "all"
        :type includefield: str
        :param level: The level

            The possible value:
                - ``patient``
                - ``study``
                - ``series``
                - ``instance``
        :type level: str
        :param list_path: List of the path or object
        :type list_path: bool
        :return: The metadata
        :rtype:list [dict]
        """
        if list_path:
            dicom_file_path_list = return_list_uid(result)
        else:
            dicom_file_path_list = self.get_list_uid(result, "instance")
        LOG_API_DICOMWEB.debug("dicom_file_path_list = %s", dicom_file_path_list)

        list_metadata_dcm = []
        for dicom_file_path in dicom_file_path_list:
            try:
                # TODO if the file is missing the *File Meta Information* header.
                #  Ajoute force=True pour forcer la lecture même si aucun en-tête * File Meta Information * n'est trouvé.
                dataset = pydicom.dcmread(dicom_file_path, stop_before_pixels=True, force=True)
                if includefield == "all":
                    _ds = filter_dataset(dataset, QS_FILTERS[level])
                else:
                    list_tags = []
                    for tag in includefield.split(','):
                        list_tags.append(get_group_element_number(tag))
                    _ds = filter_dataset(dataset, list_tags)
                txt = _ds.to_json()
                metadata_json = json.loads(txt)
                list_metadata_dcm.append(metadata_json)
            except Exception as exc:
                LOG_API_DICOMWEB.exception(exc)
        LOG_API_DICOMWEB.debug(list_metadata_dcm)
        return list_metadata_dcm
