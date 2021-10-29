from sqlalchemy.types import Integer, BigInteger

from sphere import settings


class CoreView:

    args = {}
    if settings.DB_ENGINE == 'postgresql':
        args['schema'] = settings.DB_PARAMS['schema']
    elif settings.DB_ENGINE == 'mysql':
        args['mysql_engine'] = 'myisam'

    __table_args__ = (args)

    ID_TYPE = Integer if settings.DB_ENGINE == 'sqlite' else BigInteger
    SCHEMA = settings.DB_PARAMS['schema'] if 'schema' in settings.DB_PARAMS else None

    def create_view_request(self, or_replace=True):
        """
        Request to create a view

        :param or_replace: replace view (True | False)
        :type or_replace: bool, optional
        :return: The request
        :rtype: str
        """
        req = 'CREATE %s VIEW %s AS %s' % ('OR REPLACE' if or_replace else '',
                                           self.table_full_name(),
                                           self.definition)
        return req

    def drop_view_request(self, if_exists=True, cascade=True):
        """
        Request to drop a view

        :param if_exists: View exits or not (True | False)
        :type if_exists: bool, optional
        :param cascade: The cascade (True | False)
        :type cascade: bool, optional
        :return: The request
        :rtype: str
        """
        req = 'DROP VIEW %s %s %s' % ('IF EXISTS' if if_exists else '',
                                      self.table_full_name(),
                                      'CASCADE' if cascade else '')
        return req

    def create_view(self, engine):
        """
        Create view

        :param engine: The engine
        :type engine: sqlalchemy.engine.base.Engine
        """
        engine.execute(self.create_view_request())

    def drop_view(self, engine):
        """
        Drop view

        :param engine: The engine
        :type engine: sqlalchemy.engine.base.Engine
        """
        engine.execute(self.drop_view_request())

    def table_full_name(self):
        """
        Join schema and table name

        :return: schema and table name
        :rtype: str
        """
        SCHEMA = settings.DB_PARAMS['schema'] if 'schema' in settings.DB_PARAMS else None
        return '.'.join(filter(None, [SCHEMA, self.__tablename__]))
