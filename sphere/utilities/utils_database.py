"""
Connect from a database
"""
# pylint: disable=too-many-locals
import json
import psycopg2

from sphere.settings import EXTENDED, PATH_COPY_EXTENDED, DB_PARAMS
from sphere.logs.logs import LOG_DATABASE


def connect_postgresql(**kwargs):
    """
    Connect to a schemas from a postgresql database

    :param kwargs: The host

        Example of kwargs:
            | {
            |   'host': '10.172.146.19',
            |   'port': 5432,
            |   'dbname': 'pacs',
            |   'user': 'user',
            |   'password': 'password'
            | }

    :type kwargs: dict
    :return: Will return a cursor object, you can use this cursor to perform
        queries
    :rtype: :py:class:`psycopg2.extensions.cursor`
    """
    try:
        # get a connection, if a connect cannot be made an exception will
        # be raised here
        conn = psycopg2.connect(**kwargs)
        # conn.cursor will return a cursor object, you can use this cursor
        # to perform queries
        cursor = conn.cursor()
        return cursor
    except psycopg2.OperationalError as error:
        LOG_DATABASE.error(error)
        return None


# pylint: disable=no-else-return
def check_db_pacs(check_exists_data=True):
    """
    Check the database of PACS

    :param check_exists_data:  Check if we have data in the database
    :type check_exists_data: bool
    :return: Return True if all is OK else return False
    :rtype: bool
    """
    settings_db = DB_PARAMS
    try:
        host = settings_db['ip']
        port = settings_db['port']
        dbname = settings_db['database']
        user = settings_db['login']
        password = settings_db['password']
        schema = settings_db['schema']
    except TypeError as error:
        LOG_DATABASE.error(error)
        return False

    # check user
    query_user = "SELECT EXISTS(SELECT * FROM pg_catalog.pg_roles WHERE " \
                 "rolname = '" + user + "')"

    # check schema
    query_schema = "SELECT EXISTS(SELECT schema_name FROM " \
                   "information_schema.schemata WHERE schema_name = " \
                   "'" + schema + "')"

    # Check table

    query_tables = \
        "SELECT table_name FROM   information_schema.tables  WHERE  " \
        "table_schema = '" + schema + "' and table_name in ('study', " \
                                      "'series', 'patient', " \
                                      "'file_storage_metadata_dicom')"

    # check if data exits in table instances
    def query_count_table(table_name):
        return "SELECT count(*) FROM  " + schema + "."\
                        + table_name

    kwargs = {"host": host, "port": port, "dbname": dbname, "user": user,
              "password": password}
    cursor = connect_postgresql(**kwargs)
    if cursor:
        cursor.execute(query_user)
        result_user = cursor.fetchall()
        res_bool_user = bool(result_user[0][0])
        if res_bool_user:
            cursor.execute(query_schema)
            result_schema = cursor.fetchall()
            res_bool_schema = bool(result_schema[0][0])
            if res_bool_schema:
                cursor.execute(query_tables)
                result_table = cursor.fetchall()
                list_table = []
                for table in result_table:
                    list_table.append(table[0])
                if list_table:
                    if check_exists_data:
                        try:
                            cursor.execute(
                                query_count_table("file_storage_metadata_dicom"))
                            count_ligne = cursor.fetchone()[0]
                            if count_ligne:
                                return True
                            else:
                                LOG_DATABASE.warning("The tables are empty")
                        except psycopg2.ProgrammingError as error:
                            LOG_DATABASE.error(error)
                            return False
                    else:
                        return True
                else:
                    LOG_DATABASE.error("I connect to the database but there are"
                                       " no tables [patient, study, series, "
                                       "file_storage_metadata_dicom]")
            else:
                LOG_DATABASE.error("Schema do not exist so no database")
        return False
    else:
        LOG_DATABASE.error("No database in this PACS")
        return False


def create_file_json(data):
    """
    Create file json

    :param data: The data
    :type data: dict
    """
    try:
        with open(PATH_COPY_EXTENDED, 'w') as file:
            json.dump(data, file)
        LOG_DATABASE.info("Create file %s", PATH_COPY_EXTENDED)
    except Exception as exc:
        LOG_DATABASE.exception("I did not create the copy_extended_db file. "
                               "\n %s", exc)


def read_copy_extended_db():
    """
    Read file copy_extended_db and return result

    :return: The data
    :rtype: dict
    """
    try:
        with open(PATH_COPY_EXTENDED) as json_file:
            data = json.load(json_file)
            return data
    except FileNotFoundError:
        if EXTENDED:
            LOG_DATABASE.warning("This file '%s' not exits. I used file "
                                 "extended_db.yml", PATH_COPY_EXTENDED)
        else:
            LOG_DATABASE.info('This file %s not exits', PATH_COPY_EXTENDED)
        return EXTENDED
    except Exception as exc:
        if EXTENDED:
            LOG_DATABASE.exception("I'm using this 'extended_db.yml' file "
                                   "and not '%s'\n %s", PATH_COPY_EXTENDED, exc)
        return EXTENDED
