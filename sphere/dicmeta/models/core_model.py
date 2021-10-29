# pylint: disable=eval-used
import json
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.types import Integer, DateTime, BigInteger

from sphere import settings
from sphere.logs.logs import LOG_DATABASE
from sphere.dicmeta.models.base import SCHEMA
from sphere.utilities.utils_database import read_copy_extended_db


class CoreModel:
    """ The core of model"""
    __schema__ = SCHEMA

    args = {}
    if settings.DB_ENGINE == 'postgresql':
        args['schema'] = settings.DB_PARAMS['schema']
    elif settings.DB_ENGINE == 'mysql':
        args['mysql_engine'] = 'myisam'

    __table_args__ = args

    ID_TYPE = Integer if settings.DB_ENGINE == 'sqlite' else BigInteger
    SCHEMA = settings.DB_PARAMS['schema'] if 'schema' in settings.DB_PARAMS else None

    d8ins = Column(DateTime, default=datetime.utcnow)
    d8maj = Column(DateTime)
    d8del = Column(DateTime)

    def __init__(self, **kwargs):
        self.create(**kwargs)

    def update(self, none_update=True, **kwargs):
        """
        Update value if not none or none_update is True

        :param none_update: True if you want update none otherwise False
        :type none_update: boo, optional
        :param kwargs: The dictionary of data
        :type kwargs: dict
        """
        for key, value in kwargs.items():
            if value is not None or none_update:
                setattr(self, key, value)
        self.d8maj = datetime.now()

    def create(self, **kwargs):
        """
        Create now line

        :param kwargs: The dictionary of data
        :type kwargs: dict
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.d8maj = datetime.now()

    # pylint: disable=no-member
    def table_full_name(self):
        """ Join schema and table name """
        return '.'.join(filter(None, [self.__schema__, self.__tablename__]))

    def json(self):
        """ Takes in a json object and returns a string."""
        if hasattr(self, 'dict_data'):
            return json.dumps(self.dict_data(), sort_keys=True)
        return ''

    @classmethod
    def attributes_extended(cls, table_name):
        """
        return list of attribute_extended and size_value

        :param table_name: The table name
        :type table_name: str
        :return: return list of attribute and size_value
        :rtype: list [list[str, str]]
        """
        json_extended = read_copy_extended_db()
        list_attributes = []
        if json_extended and table_name in json_extended.keys():
            for _tag, dic in json_extended[table_name].items():
                field_name = dic['field_name']
                size_value = ""
                if 'type' in dic:
                    type_value = dic['type']
                else:
                    type_value = 'String'
                if type_value == 'String':
                    if 'size' in dic:
                        size_value = dic['size']
                    else:
                        size_value = '64'

                attribute = ''
                if type_value == 'String':
                    attribute = eval("field_name") + " = Column('" + eval(
                        "field_name") + "', " + eval(
                            "type_value") + "(size_value))"
                elif type_value == 'Text':
                    attribute = eval("field_name") + " = Column('" + eval(
                        "field_name") + "', " + eval("type_value") + ")"
                else:
                    LOG_DATABASE.error(
                        "We don't treat this type '%s'. So we will "
                        "not add this field '%s' in the database",
                        type_value, field_name)
                if attribute:
                    list_attributes.append([attribute, size_value])

        return list_attributes

    @staticmethod
    def extended_fields(table_name):
        """
        Return all extended fields name

        :param table_name: Table name
        :type table_name: str
        :return: list of fields_name
        :rtype: list
        """
        json_extended = read_copy_extended_db()
        list_fields = []
        if json_extended and table_name in json_extended.keys():
            for _tag, dic in json_extended[table_name].items():
                list_fields.append(dic['field_name'])

        return list_fields

    @staticmethod
    def add_value_none(include_none, args):
        """
        Include value None

        :param include_none: Do you include None
        :type include_none: bool
        :param args: The dictionary
        :type args: dict
        :return: The dictionary
        :rtype: dict
        """
        if not include_none:
            return {k: v for k, v in args.items() if v is not None}
        return args

    @staticmethod
    def msg_suffix(data_level):
        """
        Return message and suffix

        :param data_level: Do you include None
        :type data_level: int
        :return: The message and suffix
        :rtype: tuple (str, str)
        """
        suffix = ''
        msg = ''
        if data_level > 0:
            msg += '-' * 30
            suffix = '\n- '
        return msg, suffix
