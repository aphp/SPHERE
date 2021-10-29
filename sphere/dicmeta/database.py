""" The methods of the database """
# pylint: disable=superfluous-parens
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy import func
from sqlalchemy.sql import exists

from sphere import settings
from sphere.utilities.utils_database import create_file_json
from sphere.logs.logs import LOG_DATABASE


class Database:

    def __init__(self):
        self.sgbd = settings.DB_ENGINE
        self.engine = self.create_engine()
        self.session = None

    def create_engine(self):
        """ Create engine"""
        if self.sgbd == 'postgresql' or self.sgbd == 'pgsql':
            return create_engine("postgresql://%s:%s@%s:%s/%s" %
                                 (settings.DB_PARAMS['login'],
                                  settings.DB_PARAMS['password'],
                                  settings.DB_PARAMS['ip'],
                                  settings.DB_PARAMS['port'],
                                  settings.DB_PARAMS['database']),
                                 pool_recycle=settings.DB_ENGINE_POOL_RECYCLE,
                                 pool_size=settings.DB_ENGINE_POOL_SIZE,
                                 max_overflow=settings.DB_ENGINE_POOL_OVERFLOW,
                                 pool_timeout=settings.DB_ENGINE_POOL_TIMEOUT)

        if self.sgbd is None or self.sgbd == 'sqlite':
            return create_engine(
                'sqlite:///'+settings.DB_PARAMS['filepath']+'.db',
                connect_args={'check_same_thread': False})

    def create_tables(self):
        """ Create Tables """
        create_file_json(settings.EXTENDED)
        self.metadata_table.create_all(self.engine, checkfirst=True)
        if self.sgbd == 'postgresql' or self.sgbd == 'pgsql':
            self.create_views()
        LOG_DATABASE.info('I create all tables.')

    def create_views(self):
        """ Create view """
        for _k, view in self.views.items():
            view.create_view(self.engine)

    def all_tables(self, schema=None):
        """
        Return all tables of database

        :param schema: The schema
        :type schema: str , default None
        :return: Return list of all tables.
        :rtype: list[str]
        """
        if schema:
            list_tables = self.engine.table_names(schema=schema)
        else:
            list_tables = self.engine.table_names()
        return list_tables

    def delete_all_table(self, schema=None):
        """
        Delete all table in database

        :param schema: The schema
        :type schema: str , default None
        """
        session = self.create_session()
        try:
            list_tables = self.all_tables(schema)
            for table in list_tables:
                if schema:
                    request = 'DROP TABLE IF EXISTS {}.{} CASCADE;'.format(schema, table)
                else:
                    request = 'DROP TABLE IF EXISTS {} CASCADE;'.format(table)
                print(request)
                session.execute(request)
                session.commit()
            LOG_DATABASE.warning("Because we have an exception when we launched"
                                 " the drop. So I delete all table in this "
                                 "schema '%s', with DROP CASCADE.",
                                 schema)
            self.clear_session(session)
        except Exception as exc:
            LOG_DATABASE.error(exc)

    def drop_tables(self, f_drop):
        """
        Drop tables

        :param f_drop: Force drop database or no
        :type f_drop: bool, None (True | False)
        :return: True if we deleted the database else it is False
        :rtype: bool
        """
        if f_drop is None:
            yes_no = input("Are you sure you want to drop or clean a database"
                           " ? 'yes' or 'no': ")
            while yes_no not in ["yes", 'no']:
                yes_no = input("You have to type 'yes' or 'no':")
        else:
            yes_no = "yes" if f_drop is True else "no"

        if yes_no == 'yes':
            if self.sgbd == 'postgresql' or self.sgbd == 'pgsql':
                self.drop_views()
            try:
                self.metadata_table.drop_all(self.engine)
            except Exception as exc:
                LOG_DATABASE.error(exc)
                schema = settings.DB_PARAMS['schema']
                self.delete_all_table(schema)
            LOG_DATABASE.info("I delete all tabes of database.")
            return True
        else:
            LOG_DATABASE.info("I do'nt delete any tables of database")
            return False

    def drop_views(self):
        """ Drop view """
        for _k, view in self.views.items():
            view.drop_view(self.engine)

    def clean_tables(self, f_drop):
        """
        Drop and create tables

        :param f_drop: Force drop database or no
        :type f_drop: bool, None (True | False)
        """
        is_delete = self.drop_tables(f_drop)
        if is_delete:
            self.create_tables()

    def init_session(self, reload_force=False):
        """
        Initialize session

        :param reload_force: the reload_force (True | False)
        :type reload_force: bool, optional
        """
        if reload_force:
            self.clear_session()
        if self.session is None:
            self.session = self.create_session()

    def create_session(self):
        """
        Create session

        :return: The session
        :rtype: sqlalchemy.orm.session.Session
        """
        Session = scoped_session(sessionmaker(bind=self.engine))
        return Session()

    @staticmethod
    def clear_session(session):
        """
        Clean session

        :param session: The session
        :type session: sqlalchemy.orm.session.Session
        """
        session.close()
        # session.expunge_all()

    def table_exists(self, tablename, schema):
        """
        Check if table exists or not in schema

        :param tablename: The table name
        :type tablename: str
        :param schema: The schema name
        :type schema: str
        :return: True if table name exists else False
        :rtype: bool
        """
        ret = self.engine.dialect.has_table(self.engine, tablename, schema)
        LOG_DATABASE.info('Table "%s" exists: %s', tablename, ret)
        return ret

    def study_uid_exist(self, study_uid, model):
        """
        StudyUID exist

        :param study_uid: The studyUID to look for in the table
        :type study_uid: str
        :param model: The model so the table in which we should search
            the studyUID
        :type model: class
        :return: True if studyUId exist False otherwise
        :rtype:  bool
        """

        try:
            attr = getattr(model.__class__, 'studyUID')
            sess = self.create_session()
            res = sess.query(exists().where(attr == study_uid)).scalar()
            self.clear_session(sess)
        except Exception as err:
            raise(Exception(str(err)))
        return res

    def check_uid_exist(self, uid, model, attribute):
        """
        check if uid exist

        :param uid: The UID to look for in the table
        :type uid: str
        :param model: The model so the table in which we should search
            the patientUID, studyUID or seriesUID
        :type model: class
        :param attribute: The attribute
        :type attribute: class
        :return: True if uid exist False otherwise
        :rtype:  bool
        """

        try:
            attr = getattr(model.__class__, attribute)
            sess = self.create_session()
            res = sess.query(exists().where(attr == uid)).scalar()
            self.clear_session(sess)
        except Exception as err:
            raise(Exception(str(err)))
        return res

    def get_by_key(self, model_instance, model=None):
        """
        Get by Key

        :param model_instance: The model instance

            Example of model_instance: (StudyModel, SeriesModel, ...)

        :type model_instance: object
        :param model: The model
        :type model: class, optional
        :return: The model
        :rtype: class

            Example of result:
                | ``<Study(id='1',``
                | ``studyUID=
                    '1.2.124.113532.10.160.160.59.20081013.90623.2087268',``
                | ``patientID='4608001679',``
                | ``dateStudy='20081013')>``
        """
        try:
            if model is None:
                model = model_instance.__class__
            if isinstance(model_instance, model):
                key = getattr(model_instance, model.KEY)
        except Exception as err:
            raise(Exception(str(err) +
                            "\n\nIf 'model' is null in getBy Method, you need "
                            "to send object instance instead of key"))

        if key is not None:
            try:
                sess = self.create_session()
                res = sess.query(model).filter(
                    getattr(model, model.KEY) == key).first()
                self.clear_session(sess)
            except Exception as err:
                raise(Exception(str(err)))
            return res
        return None

    def get_by_id(self, model_instance, model=None, id_only=False):
        """
        Get by id

        :param model_instance: The model instance

            Example of model_instance: (StudyModel, SeriesModel, ...)

        :type model_instance: object or int
        :param model: The model
        :type model: class, optional
        :param id_only: True if return ID else return class
        :type id_only: bool, optional
        :return: The model
        :rtype: str, class or None
        """
        try:
            if model is None:
                model = model_instance.__class__
            if isinstance(model_instance, model):
                db_id = getattr(model_instance, model.ID)
        except Exception as err:
            raise(Exception(str(err) +
                            "\n\nIf 'model' is null in getBy Method, you need "
                            "to send object instance instead of db_id"))

        if db_id is not None:
            try:
                sess = self.create_session()
                data = sess.query(model).filter(
                    getattr(model, model.ID) == db_id).first()
                self.clear_session(sess)
            except Exception as err:
                raise(Exception(str(err)))
            return getattr(data, model.ID) if id_only else data

        return None

    def buffer_model(self, data):
        """
            Add data to a buffer previously created.
        """

    def insert(self, model_instance, nested_level=0):
        """
        Insert the model instance

        :param model_instance: The data list
        :type model_instance: object
        :param nested_level: The nested level
        :type nested_level: int, optional
        """
        session = self.create_session()
        session.add(model_instance)
        try:
            session.commit()
            LOG_DATABASE.info("Insertion goes well")
        except Exception as error:
            LOG_DATABASE.exception(error)
            LOG_DATABASE.warning("Error in database access. Retry %s "
                                 "time (Process stopped for 500 ms)",
                                 str(nested_level+1))
            self.clear_session(session)
            if nested_level < 2:
                self.insert(model_instance, nested_level=nested_level+1)

        self.clear_session(session)

    def create_or_update_model(
            self, data, check_key=True, update=False, nested_level=0, **kwargs):
        """
        Create or update model

        :param data: The data list
        :type data:
            :py:class:`object sphere.dicmeta.models.study_model.StudyModel`,
            :py:class:`sphere.dicmeta.models.series_model.SeriesModel`,
            :py:class:`sphere.dicmeta.models.patient_model.PatientModel`,
            :py:class:`sphere.dicmeta.models.file_storage_metadata_model.FileStorageMetadataDicomModel`
        :param check_key: Check key
        :type check_key: bool, optional
        :param update: Update or not the data (True | False)
        :type update: bool, optional
        :param nested_level: The nested level
        :type nested_level: int, optional
        :param kwargs: The dictionary of data (not used)
        :type kwargs: dict
        :return: Return ID
        :rtype: int
        """
        # On cherche par defaut par ID sinon par Key
        session = self.create_session()
        db_data = \
            self.get_by_id(data) if not check_key else self.get_by_key(data)
        if db_data is not None:
            if update:
                db_data.update(**data.dict_data())
            data = db_data
        else:
            session.add(data)
        try:
            session.commit()
        except Exception as error:
            LOG_DATABASE.exception(error)
            if settings.DB_VERBOSE_ERROR:
                print(error)
            print("Error in database access. Retry " + str(nested_level+1) +
                  " time (Process stopped for 500 ms)")
            self.clear_session(session)
            if nested_level < 2:
                return self.create_or_update_model(
                    data=data, check_key=check_key, update=update,
                    nested_level=nested_level+1, **kwargs)
            else:
                return None

        id = int(getattr(data, data.__class__.ID))
        self.clear_session(session)

        return id

    def get_max_value(self, model, key):
        """
        Get the max value of a column in a table

        :param model: The model and so the table name to look at
        :type model: :py:class:`sphere.dicmeta.models.study_list_model.StudyListModel`
        :param key: the attribute of the model and so the column name to look at
        :type key: str
        :return: the max value of the column in the specified table
        :rtype: int
        """
        session = self.create_session()
        if model is not None and key is not None:
            try:
                attr = getattr(model.__class__, key)
                max_value = session.query(func.max(attr)).scalar()
                self.clear_session(session)
                if max_value is None:
                    max_value = 0
                return max_value
            except Exception as error:
                print(' {0} Error in getting the max value of  {1}.{2}'.format(
                    error, str(model), str(key)))
        else:
            print(
                "Error you need to specify the model's and the "
                "atribute's names")

    def get_model_filter(self, model, filter_field, filter_value):
        """
        Get the list of element for a model filtered
        on filter_field = filter_value

        :param model: The model and so the table name to look at
        :type model: class sphere.dicmeta.models.study_list_model.StudyListModel
        :param filter_field: the attribute of the model and so the column name
            to look at
        :type filter_field: str
        :filter_value: the value to look for in the filter_value
        :type filter_value: str

        :rtype: list of instance of model
        """
        session = self.create_session()
        if model is not None and filter_field is not None \
                and filter_value is not None:
            try:
                res = session.execute(
                    'SELECT study_uid FROM  ' + settings.DB_PARAMS['schema'] +
                    '.' + model.__tablename__ + ' WHERE ' + filter_field +
                    ' = ' + str(filter_value))
                self.clear_session(session)
            except Exception as err:
                raise(Exception(str(err)))
            return res
        else:
            print(
                "Error you need to specify the model and the "
                "filter_field, and filter_value")
