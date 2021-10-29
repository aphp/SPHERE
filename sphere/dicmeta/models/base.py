from sqlalchemy.ext.declarative import declarative_base

from sphere import settings

DB_BASE_PACS = declarative_base()
DB_BASE_LOGS = declarative_base()
SCHEMA = settings.DB_PARAMS['schema'] if 'schema' in settings.DB_PARAMS else None


def table_full_name(table_name):
    """
    Join schema and table name

    :param table_name: table name
    :type table_name: str
    :return: schema and table name
    :rtype: str
    """
    return '.'.join(filter(None, [SCHEMA, table_name]))
