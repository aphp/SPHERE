""" Settings of SPHERE"""
# pylint: disable=ungrouped-imports
import copy
import os
import sys

import requests
from requests.exceptions import ConnectionError
from pynetdicom import StoragePresentationContexts

from sphere.logs.logs import default_config_logs
from sphere.logs.logs import LoggingConfig
from sphere.utilities.msg import message_critical, message_param
from sphere.utilities.log_tools import logging_dict
from sphere.utilities.string_tools import str2bool
from sphere.utilities.check_param_settings import CheckParamSettings

try:
    from app.settings import load_config_file
except (TabError, IndentationError) as error:
    raise Exception(error)
except ImportError:  # for generate the autodoc (sphinx)
    from sphere.builder.setup_models.app.settings import load_config_file

try:
    # pylint: disable=import-error
    from app.settings import LOG_SETTINGS
except ImportError:
    LOG_SETTINGS = default_config_logs(list_logger_name=['settings'])
    LOG_SETTINGS.warning("Use the default configuration for settings logs")
except Exception as exc:
    raise Exception(exc)

PATH_FILE_LOGGING_CONFIG_SPHERE = './app/logging_config.yml'
PATH_FILE_SETTINGS_SPHERE = './app/settings.yml'
PATH_FILE_EXTENDED_DB = './app/extended_db.yml'

if __name__ == "sphere":
    # TODO Ameliorer l'import de sys
    load_config_file(sys.argv[1])
else:
    try:
        PARAMS = load_config_file(PATH_FILE_SETTINGS_SPHERE)
        logging_dict(LOG_SETTINGS, PARAMS,
                     "This is the dictionary of parameters: ")
    except FileNotFoundError:  # for generate the autodoc (sphinx)
        DS_DIR = os.path.dirname(__file__)
        PARAMS = load_config_file(
            os.path.join(DS_DIR, 'builder/setup_models/app/settings.yml'))
    except Exception as exc:
        MSG = " problem reading files settings.yml"
        LOG_SETTINGS.exception("%s \n %s ", MSG, exc)
        raise Exception(MSG)

    try:
        EXTENDED = load_config_file(PATH_FILE_EXTENDED_DB)
    except FileNotFoundError:
        LOG_SETTINGS.warning("This file '%s' does not exists in PACS, so no "
                             "extended db.", PATH_FILE_EXTENDED_DB)
        EXTENDED = {}
    except Exception as exc:
        LOG_SETTINGS.exception(exc)
        EXTENDED = {}

CHECK_PARAM = CheckParamSettings(PARAMS, LOG_SETTINGS)

###############################################################################
# -_-_-_-_-_-_-_-_-_-_-_-_-_-_- ApplicationEntity -_-_-_-_-_-_-_-_-_-_-_-_-_- #
###############################################################################
# ## ADD SERVER CONTEXT
LOG_SETTINGS.info('{:_^70}'.format('Parameters of ApplicationEntity (ae)'))
try:
    SCP_PORT = int(os.getenv('DICOM_PORT', PARAMS['port']))
    SCP_AET = os.getenv('DICOM_AET', PARAMS['AET'].strip())
    LOG_SETTINGS.debug(message_param('AET', SCP_AET))
    LOG_SETTINGS.debug(message_param('port', SCP_PORT))
except Exception as exc:
    MSG = 'You need to define at least one port and AETITLE of this server PACS'
    LOG_SETTINGS.exception("%s \n %s", MSG, exc)
    raise Exception(MSG)

# Parameters of ApplicationEntity (ae)

REQUIRE_CALL_AET = CHECK_PARAM.check_bool('ae_params.required_call_aet', False)
MAX_ASSOC_IDLE_SECOND = CHECK_PARAM.check_number('ae_params.max_assoc_idle_second', 50)
MAX_ASSOC = CHECK_PARAM.check_number('ae_params.max_assoc', 50)
PDU_SIZE = CHECK_PARAM.check_number('ae_params.pdu_size', 0)
ACSE_TIMEOUT = CHECK_PARAM.check_number('ae_params.acse_timeout', 120)
DIMSE_TIMEOUT = CHECK_PARAM.check_number('ae_params.dimse_timeout', 120)
NETWORK_TIMEOUT = CHECK_PARAM.check_number('ae_params.network_timeout', 120)

###############################################################################
# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- DIMSE -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- #
###############################################################################
LOG_SETTINGS.info('{:_^70}'.format('Parameters of DIMSE'))

SCP_SERVICES = CHECK_PARAM.check_str('scp_services', ['c-echo'])
NB_THREAD = int(os.getenv('THREAD_NUMBER', CHECK_PARAM.check_number('thread.number', 4)))
# Search DICOM in file if database is empty (True| False)
SEARCH_FILE = CHECK_PARAM.check_bool('search_in_file', False)
SEND_EXTENDED_DB = CHECK_PARAM.check_bool('send_extended_db_of_find', False)
PENDING_RESPONSES_MOVE = CHECK_PARAM.check_bool('pending_responses_move', False)

SLEEP_IN_STORE = os.getenv('SLEEP_IN_STORE', CHECK_PARAM.check_number('sleep_in_store', 0) * 60)
# -_-_-The context -_-_- #
DICT_CONTEXTS = {"default": StoragePresentationContexts}
LOCAL_CONTEXT = CHECK_PARAM.check_str('context', 'default')

try:
    from app.settings import dict_contexts  # pylint: disable=ungrouped-imports

    DICT_CONTEXTS.update(dict_contexts)
except ImportError:
    print('No extra contexts defined')

###############################################################################
# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- DICOM STORAGE -_-_-_-_-_-_-_-_-_-_-_-_-_-_- #
###############################################################################
# # storage paths
# DEFAULT VALUE IS FS
LOG_SETTINGS.info('{:_^70}'.format('Parameters of DICOM STORAGE'))

STORAGE_METHOD = os.getenv('STORAGE_METHOD', CHECK_PARAM.check_str('storage_method', 'FS'))
# DEFAULT VALUE .tmp_data -> is .tmp_data folder not exist create folder
TMP_PATH_STORAGE = CHECK_PARAM.check_path_folder('tmp_path', '.tmp_data')

LIST_STORAGES = ['FS', 'HDFS', 'HBASE', 'MIXED']
if STORAGE_METHOD.upper() == 'FS':
    try:
        FS_PATH_STORAGE = os.getenv('FS_DATA_PATH', CHECK_PARAM.check_path_folder('fs.path', './data'))
        # if the file does not exist create it
        if not os.path.isdir(FS_PATH_STORAGE):
            os.mkdir(FS_PATH_STORAGE)
    except Exception as exc:
        MSG = 'You need to define at least one of this storage method : %s ', \
              LIST_STORAGES
        LOG_SETTINGS.exception("%s \n %s", MSG, exc)
        raise Exception(MSG)

elif STORAGE_METHOD.upper() == 'HDFS':
    HDFS_PATH_STORAGE = os.getenv('HDFS_DATA_PATH', CHECK_PARAM.check_path_folder('hdfs.path', './hdfs_data'))
    TAR_SIZE = CHECK_PARAM.check_number('tar_size', 10)

elif STORAGE_METHOD.upper() == 'HBASE':
    HBASE_PATH_STORAGE = os.getenv('HBASE_DATA_PATH', CHECK_PARAM.check_path_folder('hbase.path', './hbase_data'))

else:
    MSG = 'You need to define at least one of this storage method : %s ', \
          LIST_STORAGES
    LOG_SETTINGS.critical(MSG)
    raise Exception(MSG)

# DEFAULT VALUE IS ./app/white_list; if folder not exist ERROR
FS_PATH_WHITE_LIST = os.getenv('WHITELIST_PATH', CHECK_PARAM.check_path_folder('path_white_list', './app/white_list'))

if not os.path.isdir(FS_PATH_WHITE_LIST):
    LOG_SETTINGS.error("You need to define a path for white list of this "
                       "server PACS. This path '%s' does not exits (The "
                       "parameter is 'path_white_list' )", FS_PATH_WHITE_LIST)

# -_-_-_-_-_-_-_-_-_-_-_ HDFS -__-_-_-_-_-_-_-_-_-_ #
START_MOVE_HDFS = CHECK_PARAM.check_bool('hdfs.start_move_hdfs', False)

if START_MOVE_HDFS:
    FREE_HARD_DRIVE = CHECK_PARAM.check_number('hdfs.free_hard_drive', 50)
    TIME_SLEEP_THREAD_HDFS = CHECK_PARAM.check_number('hdfs.time_sleep_thread_hdfs', 10)
    TIME_SLEEP_HDFS = CHECK_PARAM.check_number('hdfs.time_slep_hdfs', 50)
    NUMBER_STUDY = CHECK_PARAM.check_number('hdfs.number_uid', 5)
    REMOVE_FILE = CHECK_PARAM.check_bool('hdfs.remove_file', True)
    PATH_FILE_CSV_HDFS = CHECK_PARAM.check_path_folder('hdfs.path_file_csv_hdfs', './data/')
    NAME_FILE_CSV_HDFS = CHECK_PARAM.check_path_file('hdfs.name_file_csv_hdfs', "uid.txt")
    PATH_SCRIPT = CHECK_PARAM.check_file_exists('hdfs.path_script')

###############################################################################
# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- DATABASE _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- #
###############################################################################
LOG_SETTINGS.info('{:_^70}'.format("Parameters of DATABASE"))

DB_ENGINE = os.getenv('DB_ENGINE', CHECK_PARAM.check_str('db.engine', "postgresql"))
if DB_ENGINE not in ['postgresql', 'sqlite']:
    MSG = 'You need to define at least one engine: postgresql or sqlite'
    LOG_SETTINGS.critical(MSG)
    raise Exception(MSG)

if DB_ENGINE == 'postgresql':
    try:
        DB_PARAMS = {
            'ip': os.getenv('POSTGRE_HOST', CHECK_PARAM.check_str('db.params.ip', "None")),
            'port': int(os.getenv('POSTGRE_PORT', CHECK_PARAM.check_number('db.params.port', 5432))),
            'database': os.getenv('POSTGRE_NAME', CHECK_PARAM.check_str('db.params.database', "None")),
            'schema': os.getenv('POSTGRE_SCHEMA', CHECK_PARAM.check_str('db.params.schema', "None")),
            'login': os.getenv('POSTGRE_LOGIN', CHECK_PARAM.check_str('db.params.login', "None")),
            'password': os.getenv('POSTGRE_PASSWORD', CHECK_PARAM.check_str('db.params.password', "None"))
        }

        COPY_DB_PARAM = copy.deepcopy(DB_PARAMS)
        EMPTY_DB_PARAM = CHECK_PARAM.empty_db_param(COPY_DB_PARAM)
        LOG_SETTINGS.debug(message_param('db.params', EMPTY_DB_PARAM))
    except Exception as exc:
        MSG = 'You must define for postgresql engine: ip, port, ' \
              'database, schema, login, password.'
        LOG_SETTINGS.exception("%s \n %s", MSG, exc)
        raise Exception(MSG)

elif DB_ENGINE == 'sqlite':
    try:
        DB_PARAMS = {
            'filepath': os.getenv('SQLITE_FILEPATH', PARAMS['db']['params']['filepath'])
        }

        LOG_SETTINGS.debug(message_param('db.params', DB_PARAMS))

    except Exception as exc:
        MSG = 'You need to define at least one file path for ' \
              'sqlite engine'
        LOG_SETTINGS.exception("%s \n %s", MSG, exc)
        raise Exception(MSG)

DB_ENGINE_POOL_SIZE = CHECK_PARAM.check_number('db.engine_pool_size', 20)
DB_ENGINE_POOL_OVERFLOW = CHECK_PARAM.check_number('db.engine_pool_overflow', 90)
DB_ENGINE_POOL_RECYCLE = CHECK_PARAM.check_number('db.engine_pool_recycle', 70)
DB_ENGINE_POOL_TIMEOUT = CHECK_PARAM.check_number('db.engine_pool_timeout', 10)
DB_SAVE_DELAY = CHECK_PARAM.check_number('db.save_delay', 5)
DB_VERBOSE_ERROR = CHECK_PARAM.check_bool('db.verbose_error', False)

PATH_COPY_EXTENDED = CHECK_PARAM.check_path_file('name_file_copy_extended_db', './app/.copy_extended.json')

################################################################################
# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- API REST -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-__ #
################################################################################
LOG_SETTINGS.info('{:_^70}'.format("Parameters of API ANNOTATION"))

START_API = str2bool(os.getenv('API_SERVER_ENABLED', CHECK_PARAM.check_bool('api.start', False)))
if START_API:
    IP_API = os.getenv('API_SERVER_LISTENING_IP', CHECK_PARAM.check_str('api.ip', '127.0.0.1'))
    PORT_API = int(os.getenv('API_SERVER_LISTENING_PORT', CHECK_PARAM.check_number('api.port', 5555)))

    L_ALLOWED_HOSTS = CHECK_PARAM.check_list_from_env("ALLOWED_HOSTS",
                                                      CHECK_PARAM.check_str('api.allowed_hosts', ['127.0.0.1']))
    # ***** Start api
    PATH_MANAGE_API_ANNO = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'api_rest/manage.py')
    LOG_SETTINGS.debug('Path manage api annotation = %s', PATH_MANAGE_API_ANNO)

    if os.environ.get('_'):
        PATH_VENV_PYTHON = os.environ.get('_')
    else:
        PATH_VENV_PYTHON = os.path.join(os.environ.get('PATH').split(':')[0],
                                        'python')
    LOG_SETTINGS.debug("PATH_VENV_python = %s", PATH_VENV_PYTHON)

    NAME_FILE_PID_SERVER_API = "pid_server_api"

    COMMAND_RUN_API = PATH_VENV_PYTHON + " -u " + \
                      PATH_MANAGE_API_ANNO + ' runserver ' + \
                      IP_API + ':' + str(PORT_API) + \
                      ' & echo "$!" >  ' + NAME_FILE_PID_SERVER_API

    LOG_SETTINGS.debug("COMMAND_RUN_API = %s", COMMAND_RUN_API)

    START_DICOMWEB = str2bool(os.getenv('API_DICOMWEB_ENABLED', CHECK_PARAM.check_bool('api.dicomweb.start', False)))
    LOG_SETTINGS.debug("START_DICOMWEB = %s", str(START_DICOMWEB))

    START_ANNOTATION = str2bool(os.getenv('API_ANNOTATION_ENABLED', CHECK_PARAM.check_bool('api.annotation.start', False)))
    LOG_SETTINGS.debug("START_ANNOTATION = %s", str(START_ANNOTATION))

    if START_DICOMWEB:
        API_DECOMPRESS_PIXELS = str2bool(os.getenv("API_DECOMPRESS_PIXELS",
                                            CHECK_PARAM.check_bool('api.dicomweb.decompress_pixels', False)))
        LOG_SETTINGS.debug("API_DECOMPRESS_PIXELS = %s", API_DECOMPRESS_PIXELS)

        API_JWT_VALIDATION = str2bool(os.getenv("API_JWT_VALIDATION",
                                            CHECK_PARAM.check_bool('api.dicomweb.jwt_validate', False)))
        LOG_SETTINGS.debug("API_JWT_VALIDATION = %s", str(API_JWT_VALIDATION))


        API_JWT_VALIDATION_URL = os.getenv("API_JWT_VALIDATION_URL",
                                           CHECK_PARAM.check_str('api.dicomweb.jwt_validate_url', "http://localhost"))
        LOG_SETTINGS.debug("API_JWT_VALIDATION_URL = %s", API_JWT_VALIDATION_URL)

    if START_ANNOTATION:
        ANNOTATION_PATH_FOLDER = os.getenv('ANNOTATION_PATH',
                                           CHECK_PARAM.check_path_folder('api.annotation.path_data',
                                                                         './data_annotation'))

        ####################################
        # Internal: I use the basic module of python uuid
        # External: I only search from API uuid_generator
        # Mixed : I search from API uuid_generator or I use the basic module of
        # python uuid if I can't generate the id with API uuid_generator.

        LIST_CHOICE_UUID = ['INTERNAL', 'EXTERNAL', 'MIXED']
        TYPE_UUID_GENERATOR = CHECK_PARAM.check_str_in_list(
            'api.annotation.type_uuid_generator', 'INTERNAL', LIST_CHOICE_UUID)

        ####################################
        # param 'api.annotation.url_uuid_generator'

        URL_UUID = None
        if TYPE_UUID_GENERATOR != 'INTERNAL':
            try:
                try:
                    URL_UUID = PARAMS['api']['annotation']['url_uuid_generator']
                    if requests.get(URL_UUID).ok:
                        LOG_SETTINGS.debug(
                            message_param('api.annotation.url_uuid_generator', URL_UUID))
                    else:
                        if TYPE_UUID_GENERATOR == "MIXED":
                            LOG_SETTINGS.error(requests.get(URL_UUID).content)
                            LOG_SETTINGS.warning("I will use the basic python "
                                                 "uuid and not uuid_generator")
                except ConnectionError as error:
                    LOG_SETTINGS.exception(error)
                    if TYPE_UUID_GENERATOR == "MIXED":
                        LOG_SETTINGS.warning("I will use the basic python uuid "
                                             "and not uuid_generator")
                    else:
                        LOG_SETTINGS.error(
                            "This url '%s' is disable so no insertion in "
                            "database. You must modify this "
                            "'type_uuid_generator' parameter with 'INTERNAL' "
                            "or 'MIXED' if you want to add the annotations.",
                            URL_UUID)

            except KeyError:
                LOG_SETTINGS.error(
                    "The 'api.annotation.url_uuid_generator' "
                    "parameter does not exists in settings file.")
            except Exception as exc:
                LOG_SETTINGS.exception(exc)
                LOG_SETTINGS.critical(message_critical('api.annotation.ip', str))
                sys.exit()
else:
    START_DICOMWEB = False
    START_ANNOTATION = False

###############################################################################
# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- VERBOSE -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- #
###############################################################################
LOG_SETTINGS.info('{:_^70}'.format("Parameters of VERBOSE"))

VERBOSE_CONSOLE_LEVEL = CHECK_PARAM.check_number('console_verbose_level', 1)
VERBOSE_DATABASE_LEVEL = CHECK_PARAM.check_number('database_verbose_level', 0)

###############################################################################
# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_ LOG _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- #
###############################################################################
LOG_SETTINGS.info('{:_^70}'.format("Parameters of LOG"))

# The default logs if we have a problem with the logging configuration file
LOG_PATH_FOLDER = CHECK_PARAM.check_path_folder('log.path_folder', './log/')

CREATE_FILE_UID = CHECK_PARAM.check_bool('log.create_file_uid', False)

if CREATE_FILE_UID:
    FILE_NAME_UID = CHECK_PARAM.check_path_file('log.file_name_uid', 'study_series_instances.uid')
DEFAULT_LOG = CHECK_PARAM.check_bool('log.default_log', True)
LOG_PATH_MAIN = CHECK_PARAM.check_path_file('log.file_log_main', 'main.log')

LIST_LOG_LEVEL = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
LOG_STREAM_LEVEL = os.getenv('LOG_STREAM_LEVEL',
                             CHECK_PARAM.check_level_log('log.log_stream_level', 'WARNING', LIST_LOG_LEVEL))
LOG_FILE_LEVEL = os.getenv('LOG_FILE_LEVEL', CHECK_PARAM.check_level_log('log.log_file_level', 'DEBUG', LIST_LOG_LEVEL))
COLOR_MESSAGE = CHECK_PARAM.check_bool('log.color_message', True)

if COLOR_MESSAGE:
    DEFAULT_FORMATTER = '%(log_color)s%(asctime)s :: %(name)-20s :: ' \
                        '%(levelname)-8s :: %(reset)s %(blue)s %(message)s'
    FORMATTER = CHECK_PARAM.check_str('log.formatter_color', DEFAULT_FORMATTER)

else:
    DEFAULT_FORMATTER = '%(asctime)s :: %(name)-20s :: %(levelname)-8s :: ' \
                        '%(message)s'
    FORMATTER = CHECK_PARAM.check_str('log.formatter', DEFAULT_FORMATTER)

PATH_FILE_LOG = LOG_PATH_FOLDER + 'config_logging.log'
LOG_PATH_CONFIG_LOGGING = CHECK_PARAM.check_path_file('log.file_log_config_logging', PATH_FILE_LOG)
MAX_BAYTES = CHECK_PARAM.check_number('log.max_baytes', 10485760)
BACKUP_COUNT = CHECK_PARAM.check_number('log.backup_count', 2)

###############################################
# -_-_-_-_-_-_-_- DEFAULT LOG _-_-_-_-_-_-_-_ #
###############################################

LOG_CONFIG_LOGGING = default_config_logs(list_logger_name=["config_logging"],
                                         path_file=LOG_PATH_CONFIG_LOGGING)

# Config log with logging_config.yml
LOGGING_CONFIG = LoggingConfig(log_config_logging=LOG_CONFIG_LOGGING,
                               path_config=PATH_FILE_LOGGING_CONFIG_SPHERE,
                               default_log=DEFAULT_LOG)
STATUS_LOG = LOGGING_CONFIG.setup_logging()

if not STATUS_LOG and DEFAULT_LOG:  # if not logging_config
    LIST_LOGGER_NAME = ['command_event',
                        'pacs.access_list', 'pacs.event_sphere',
                        'pacs.transaction_dicom', 'pacs.file_dicom',
                        'pacs.database', 'pacs.code_python', 'pynetdicom']
    default_config_logs(list_logger_name=LIST_LOGGER_NAME,
                        path_file=LOG_PATH_MAIN,
                        stream_level=LOG_STREAM_LEVEL,
                        file_level=LOG_FILE_LEVEL,
                        formatter=FORMATTER,
                        max_baytes=MAX_BAYTES,
                        backup_count=BACKUP_COUNT)

###############################################
# -_-_-_-_-_-_ END DEFAULT LOG -_-_-_-_-_-_-_ #
###############################################
