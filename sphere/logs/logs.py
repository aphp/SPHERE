""" Functions of logs"""
# pylint: disable=invalid-name, too-many-branches
import os
import logging
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler

import yaml
from colorlog import ColoredFormatter

from sphere.utilities.log_tools import logging_dict


def get_logger(logger_name):
    """
    Get logger

    :param logger_name: Logger name
    :type logger_name: str
    :return: logger
    :rtype: :py:class:`logging.Logger`
    """
    logger = logging.getLogger(logger_name)
    return logger


LOG_COMMAND_EVENT = get_logger('command_event')
# pacs
LOG_EVENT_SPHERE = get_logger('pacs.event_sphere')
LOG_ACCESS = get_logger('pacs.access_list')
LOG_TRANSACTION = get_logger('pacs.transaction_dicom')
LOG_FILE_DICOM = get_logger('pacs.file_dicom')
LOG_DATABASE = get_logger('pacs.database')
LOG_CODE_PYTHON = get_logger('pacs.code_python')

# API
LOG_API_ANNOTATION = get_logger('api_annotation')
LOG_API_DICOMWEB = get_logger('api_dicomweb')

# Command index
LOG_CMD_INDEX = get_logger('index_data')


# -_-_-_-_-_-_-_-_-_-_- Default log settings -_-_-_-_-_-_-_-_-_-#
FORMATTER = '%(log_color)s%(asctime)s :: %(levelname)-8s :: %(name)-20s ' \
            ' :: %(reset)s %(blue)s %(message)s'
STREAM_LEVEL = logging.WARNING
FILE_LEVEL = logging.DEBUG
PATH_FILE = './log/settings.log'
MAX_BAYTES = 10485760  # 10MB
BACKUP_COUNT = 2


def default_config_logs(**kwargs):
    """
    The default configuration for all logs

    :param kwargs: Parameters dictionary

        The list of parameters is:

            | logger_name      : The logger name
            | path_file        : The path file
            | stream_level     : The logger level of stream
                The possible value to return:
                    | - ``NOTSET``    0
                    | - ``DEBUG``     10
                    | - ``INFO``      20
                    | - ``WARNING``   30 (default)
                    | - ``ERROR``     40
                    | - ``CRITICAL``  50
            | file_level          : The logger level of file
                The possible value to return:
                    | - ``NOTSET``    0
                    | - ``DEBUG``     10 (default)
                    | - ``INFO``      20
                    | - ``WARNING``   30
                    | - ``ERROR``     40
                    | - ``CRITICAL``  50
            | formatter       : The formatter
            | max_baytes      : The max baytes of file
            | backup_count    : the backup_count

        Example of kwargs:
            | {
            |   'stream_level': 30,
            |   'path_file': './log/config_logging.log',
            |   'formatter': '%(asctime)s :: %(levelname)-8s :: %(message)s',
            |   'max_baytes': 10485760,
            |   'backup_count': 2,
            |   'logger_name': 'config_logging',
            |   'file_level': 10
            | }

    :type kwargs: dict
    :return: The logging
    :rtype: logging.Logger
    """
    # logger_name
    list_logger_name = kwargs.get('list_logger_name')

    # path_file
    if not kwargs.get('path_file'):
        path_file = PATH_FILE
    else:
        path_file = kwargs.get('path_file')

    # stream_level
    if not kwargs.get('stream_level'):
        stream_level = STREAM_LEVEL
    else:
        stream_level = kwargs.get('stream_level')

    # file_level
    if not kwargs.get('file_level'):
        file_level = FILE_LEVEL
    else:
        file_level = kwargs.get('file_level')

    # formatter
    if not kwargs.get('formatter'):
        formatter = FORMATTER
    else:
        formatter = kwargs.get('formatter')

    # max_baytes
    if not kwargs.get('max_baytes'):
        max_baytes = MAX_BAYTES
    else:
        max_baytes = kwargs.get('max_baytes')

    # backup_count
    if not kwargs.get('backup_count'):
        backup_count = BACKUP_COUNT
    else:
        backup_count = kwargs.get('backup_count')

    color_formatter = ColoredFormatter(
        formatter,
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red,',
        }
    )

    for logger_name in list_logger_name:
        logger = get_logger(logger_name)
        # CONSOLE LOG
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(color_formatter)
        stream_handler.setLevel(stream_level)

        # FILE LOG
        file_handler = RotatingFileHandler(path_file, 'a', max_baytes,
                                           backup_count)
        file_handler.setFormatter(color_formatter)

        logger.setLevel(file_level)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        if len(list_logger_name) == 1:
            return logger


class LoggingConfig:  # pylint: disable=too-few-public-methods
    """ Log of logging config"""
    def __init__(self, **kwargs):
        self.path_config = kwargs.get('path_config')
        self.default_log = kwargs.get('default_log')
        self.log_config_logging = kwargs.get('log_config_logging')

    def setup_logging(self):
        """Read file config and setup logging. """
        status_log = True
        try:
            if os.path.exists(self.path_config):
                with open(self.path_config, 'rt') as f:
                    try:
                        dict_config = yaml.safe_load(f.read())
                        logging_dict(self.log_config_logging, dict_config, 'dict_config')
                        self.log_config_logging.info("Start configure logging "
                                                     "using a dictionary")
                        dictConfig(dict_config)
                        self.log_config_logging.info("End configure logging "
                                                     "using a dictionary")
                    except Exception as error:
                        status_log = False
                        self.log_config_logging.exception(error)
                        if self.default_log:
                            self.log_config_logging.error(
                                "Error in Logging Configuration. Using "
                                "default logs")
                        else:
                            self.log_config_logging.warning(
                                "Error in Logging Configuration. No logging")
            else:
                status_log = False
                if self.default_log:
                    self.log_config_logging.error(
                        "This file '%s' does not exist. Failed to load "
                        "configuration file. Using default logs",
                        self.path_config)
                else:
                    self.log_config_logging.warning(
                        "This file '%s' does not exist. Failed to load "
                        "configuration file. No logging", self.path_config)
        except Exception as exc:
            if self.default_log:
                self.log_config_logging.exception("Using default logs \n %s",
                                                  exc)
            else:
                self.log_config_logging.exception("No logging \n %s", exc)

        return status_log
