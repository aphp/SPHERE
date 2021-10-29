""" Settings SPHERE"""
# pylint: disable=invalid-name, unused-import, ungrouped-imports
import os
import logging
from logging.handlers import RotatingFileHandler

from colorlog import ColoredFormatter
import yaml
from yaml.scanner import ScannerError
from pydicom.uid import (
    ImplicitVRLittleEndian, ExplicitVRLittleEndian, ExplicitVRBigEndian,
    DeflatedExplicitVRLittleEndian, JPEGBaseline, JPEGExtended,
    JPEGLosslessP14, JPEGLossless, JPEGLSLossless, JPEGLSLossy,
    JPEG2000Lossless, JPEG2000, JPEG2000MultiComponentLossless,
    JPEG2000MultiComponent, RLELossless,
)

from pynetdicom.presentation import build_context
from pydicom._storage_sopclass_uids import VLPhotographicImageStorage


# Log of setting SPHERE
FORMATTER_WITH_COLOR = '%(log_color)s%(asctime)s :: %(name)-8s :: ' \
                       '%(levelname)-8s :: %(reset)s %(blue)s %(message)s'
FORMATTER_WITHOUT_COLOR = '%(asctime)s :: %(name)-8s :: %(levelname)-8s :: ' \
                          '%(message)s'
STREAM_LEVEL = logging.WARNING
FILE_LEVEL = logging.DEBUG
LOG_PATH_FOLDER = './log/'
# # create log folder is not existing
if not os.path.exists(LOG_PATH_FOLDER):
    os.makedirs(LOG_PATH_FOLDER)
PATH_FILE = os.path.join(LOG_PATH_FOLDER, 'settings.log')
MAX_BAYTES = 10485760  # 10MB
BACKUP_COUNT = 2


def setup_logger(logger_name, STREAM_LEVEL=logging.WARNING):
    """
    Return a logger with a default ColoredFormatter.

    :param logger_name: The logger name
    :type logger_name: str
    :return: logging
    :rtype: logging.Logger
    """

    formatter = ColoredFormatter(
        FORMATTER_WITH_COLOR,
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'bold_red,',
        }
    )

    logger = logging.getLogger(logger_name)
    # CONSOLE LOG
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(STREAM_LEVEL)

    # FILE LOG
    file_handler = RotatingFileHandler(PATH_FILE, 'a', MAX_BAYTES, BACKUP_COUNT)
    file_handler.setFormatter(formatter)

    logger.setLevel(FILE_LEVEL)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


LOG_SETTINGS = setup_logger('settings')
LOG_EXTENDED = setup_logger('extended_db', STREAM_LEVEL=logging.DEBUG)


# Read file Yaml
def load_config_file(path):
    """
    Load config file yaml

    :param path: The path of file YAML
    :type path: str
    :return: all param of PACS
    :rtype: dict
    """
    with open(path) as f:
        # use safe_load instead load
        try:
            params = yaml.safe_load(f)
        except ScannerError:
            msg = 'Wrong config file format; scanner problem'
            LOG_SETTINGS.error(msg)
            raise Exception(msg)
        except Exception as exc:
            msg = 'wrong config file format'
            LOG_SETTINGS.exception("%s \n %s", msg, exc)
            raise Exception(msg)
    return params


dict_contexts = {
    "onco_dermato": [build_context(VLPhotographicImageStorage, JPEGBaseline)]
}
