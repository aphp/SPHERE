from sre_compile import isstring

from sphere.dicmeta.database import Database
from sphere.logs.logs import LOG_DATABASE


class Request:

    def __init__(self, db):

        if not isinstance(db, Database) and not issubclass(db, Database):
            raise Exception('db must be instance of database inherited class')

        self.db = db

    def request(self, filter_req):
        """
        Create request

        :param filter_req: The filter request
        :type filter_req: bool #:py:class:`sqlalchemy.sql.elements.BinaryExpression`
        :return: The query
        :rtype: :py:class:`sqlalchemy.orm.query.Query`
        """
        session = self.db.create_session()
        return session.query(
            self.modelTable).filter(filter_req).distinct()

    def request_filter(self, model,  filter_req):
        """
        Create request with filter

        :param model: The models

            list of possible value of model:
                - `sphere.dicmeta.models.dicom_models.patient_model.PatientModel`
                - `sphere.dicmeta.models.dicom_models.study_model.StudyModel`
                - `sphere.dicmeta.models.dicom_models.series_model.SeriesModel`
        :type model: :py:class:`sqlalchemy.ext.declarative.api.DeclarativeMeta`
        :param filter_req: The dict filter request
        :type filter_req: dict
        :return: The query
        :rtype: :py:class:`sqlalchemy.orm.query.Query`
        """
        session = self.db.create_session()
        res = session.query(model).filter_by(**filter_req).distinct()
        return res

    def request_no_filter(self, request):
        """
        Create request

        :param request: The request
        :type request: :py:class:`sqlalchemy.sql.elements.BinaryExpression`
        :return: The query
        :rtype: :py:class:`sqlalchemy.orm.query.Query`
        """
        session = self.db.create_session()
        return session.query(request).distinct()

    # Check instance to find
    def check_instance(self, instance, model_name=None, key=None):
        """
        Check instance

        :param instance: The instance
        :type instance:
        :param model_name: Model name
        :type model_name: str, optional
        :param key: The key
        :type key: str, optional
        :return:
        """
        # If study is StudyModel instance, it must be define in db model
        if hasattr(self.db, model_name) and \
                getattr(self.db, model_name) is not None and \
                isinstance(instance, getattr(self.db, model_name)):
            model_class = getattr(self.db, model_name)
            if key is None:
                return getattr(instance, getattr(model_class, 'KEY'))
            else:
                if hasattr(instance, key):
                    return getattr(instance, key)
                txt_except = "In %s Class, %s key not find " % (model_name, key)
                raise Exception(txt_except)

        elif isstring(instance):
            return instance
        else:
            raise Exception(
                "You must send a %s or <string> key to find function")

    @staticmethod
    def get_by_list(list_id, func, attr=None, dict_format=False):
        """
        list off object (PatientModel, StudyModel, SeriesModel or FileStorageMetadataDicomModel)

        :param list_id: The list uid (patient_id, study_uid, series_uid or instances_uid)
        :type list_id: list [str]
        :param func: The function

            list of possible value:
                - get_by_patient_id
                - get_by_patient_name
                - get_by_study_uid
                - get_by_series_uid
        :type func: function
        :param attr:
        :type attr:
        :param dict_format: Do you want to return the result to the dictionary
            format (True | False)
        :type dict_format: bool, optional
        :return:
        :rtype: list
        """
        res = {} if dict_format else []

        if dict_format and attr is None:
            raise Exception(
                'If you want receive dict, you need to define key attribute')

        for uid in list_id:
            tmp = func(uid)

            if dict_format:
                res[getattr(tmp, attr)] = tmp
            else:
                res.append(tmp)

        return res

    def get_all(self):
        """
        Get all data of table

        :return: The data
        :rtype: object
        """
        session = self.db.create_session()
        req = session.query(self.modelTable).\
                          distinct()
        if hasattr(self.modelTable, 'ORDER_BY'):
            req = req.order_by(getattr(self.modelTable, 'ORDER_BY'))
        return req.all()

    def get_by(self, col_filter, val_filter):
        """
        get by

        :param col_filter:
        :type col_filter:
        :param val_filter:
        :type val_filter:
        :return:
        :rtype:
        """
        session = self.db.create_session()
        return session.query(
            self.modelTable).filter(col_filter == val_filter).distinct()

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
            if "*" in value or isinstance(value, list):
                if "*" in value:  # Implement the ``like`` operator
                    search = value.replace('*', '%')
                    string = "model." + key + ".like('" + search + "')"
                else:  # Implement the ``in_`` operator
                    string = "model." + key + ".in_(" + str(value) + ")"
                list_string.append(string)
                list_del_key.append(key)
        # remove the keys where we have filters ``like`` or ``in_``
        for key in list(set(list_del_key)):
            del dict_filter[key]

        session = self.db.create_session()
        query_filter = "session.query(model).filter_by(**dict_filter).filter("
        for st in list_string:
            query_filter = query_filter + st + ","
        query_filter = query_filter + ").distinct()"

        LOG_DATABASE.info("query_filter = %s", query_filter)
        sqlalchemy_orm_query = eval(query_filter)
        #print("Sqlalchemy.orm.query = {}".format(sqlalchemy_orm_query))
        return sqlalchemy_orm_query
