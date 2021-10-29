"""
Space Core access command
Function to parse argument line and execute requested user actions
"""

import sys
import argparse

from sphere.server import Server
from sphere.dicmeta.database_pacs import DatabasePACS
from sphere.command.command_file_access import CommandFileAccess
from sphere.utilities.log_tools import log_sphere_commands
from sphere.logs.logs import LOG_COMMAND_EVENT
from .command_monitor import CommandMonitor
from .command_database import CommandDatabase
from sphere import __version__
try:
    from version_pacs import __version__ as version_pacs
except:
    from sphere import __version_pacs__ as version_pacs


def pacs_server_run(kwargs):
    """
    Command line to init AE server for SCP and launch it

    :param kwargs: Parameters dictionary

        The list of parameters:

            | func      : The function name
            | action    : Type of action, possible value is ``runserver``

        Example of kwargs:
            | {
            |   'func'  : <function pacs_server_run at 0x7f6c29dee268>,
            |   'action': 'runserver'
            | }
    :type kwargs: dict
    """
    srv = Server()
    LOG_COMMAND_EVENT.info("Runserver the PACS '%s' ",
                           srv.ae.ae_title.decode("utf-8").strip())
    LOG_COMMAND_EVENT.debug("kwargs =  %s", kwargs)

    srv.run()


def cecho_action(kwargs):
    """
    Command line to init AE server for SCP and launch it

    :param kwargs: Parameters dictionary

        The list of parameters is:

            | func      : The function name
            | action    : Type of action, possible value is ``echo``
            | aec       : Application Entity target Name
            | ip        : The PACS internet protocol
            | port      : The port of PACS

        Example of kwargs:
            | {
            |   'func'  : <function cecho_action at 0x7f6cee0d16a8>,
            |   'action': 'echo',
            |   'aec'   : 'PACS1',
            |   'ip'    : '127.0.0.1'
            |   'port'  : 11111
            | }
    :type kwargs: dict
    """
    log_sphere_commands(LOG_COMMAND_EVENT, 'echo', kwargs)
    srv = Server()
    srv.send_cecho_request(**kwargs)
    # TODO : Ajouter un return code pour chaque type d'action,
    #  selon le statut final de l'action


def cstore_action(kwargs):
    """
    Create CSTORE AE and excute a c-store command for all file un folder
    DICOM repository

    :param kwargs: Parameters dictionary
        The list of parameters is:

            | func          : The function name
            | action        : Type of action, possible value is ``store``
            | ip            : The PACS internet protocol (required)
            | port          : The port of PACS (required)
            | aec           : Application Entity target Name (required)
            | source_paths     : Source to have the paths (required)

                The possible value:
                    - ``db`` database
                    - ``fs`` file system

            | model_name    : The model name (required if get_path = db)

                The possible value: ``patient``, ``study`` or ``series``

            | fileUID       : The path of the uid (required if get_path = db)
            | dicom_path    : The path of the dicom files (required if get_path = fs)
            | context       : The context (optional)
            | many_assoc    : Many or one assoc (True | False) [default: True] (optional)
            | verbose       : The verbose (optional)

                list of possible value of verbose:
                    - ``0`` quiet mode
                    - ``1`` verbose mode
                    - ``0`` ultra-verbose mode

        Example of kwargs:
            | {
            |   'func'       : <function cstore_action at 0x7f981e8c88c8>,
            |   'action'     : 'store',
            |   'ip'         : '127.0.0.1',
            |   'port'       : 11111,
            |   'aec'        : 'PACS1',
            |   'source_paths'  : 'db',
            |   'model_name' : 'study', (if get_path = db)
            |   'fileUID'    : 'study_uid.uid', (if get_path = db)
            |   'dicom_path' : '/home/oac/PACS/PACS2/data/', (if get_path = fs)
            |   'many_assoc' : True
            |   'verbose'    : 1
            | }

    :type kwargs: dict
    """
    log_sphere_commands(LOG_COMMAND_EVENT, 'store', kwargs)
    srv = Server()
    srv.send_cstore_request(**kwargs)
    # TODO : Ajouter un return code pour chaque type d'action,
    #  selon le statut final de l'action


def cfind_action(kwargs):
    """
    Launch the method send_cfind_request()

    :param kwargs: Parameters dictionary

        The list of parameters is:

            | func              : The function name
            | action            : Type of action, possible value is ``find``
            | ip                : The PACS internet protocol
            | port              : The port of PACS
            | qr_level          : The query level

                The possible value: ``PATIENT``, ``STUDY`` or ``SERIES``

            | patient_id        : The patient ID
            | output_filepath   : output file path
            | study_uid         : The study UID
            | series_uid        : The series UID
            | display_ds        : Display dataset (True | False) [default: False]
            | overwrite         : overwrite file uid if exists (True | False)

        Example of kwargs:
            | {
            |   'func'          : <function cfind_action at 0x7fbfcf780950>,
            |   'action'        : 'find',
            |   'ip'            : '127.0.0.1',
            |   'port'          : 11111,
            |   'aec'           : 'PACS1',
            |   'qr_level'      : 'PATIENT',
            |   'patient_id'    : '4305052317',
            |   'output_filepath': None,
            |   'study_uid'     : None,
            |   'series_uid'    : None,
            |   'overwrite'     : True,
            |   'display_ds'    : False
            | }

    :type kwargs: dict
    """
    log_sphere_commands(LOG_COMMAND_EVENT, 'find', kwargs)
    srv = Server()
    srv.send_cfind_request(**kwargs)
    # TODO : Ajouter un return code pour chaque type d'action,
    #  selon le statut final de l'action


def cmove_action(kwargs):
    """
    Launch the function send_cmove_request()

    :param kwargs: Parameters dictionary

        The list of parameters is:

            | func              : The function name
            | action            : Type of action, possible value is ``move``
            | ip                : The PACS internet protocol
            | port              : The port of PACS
            | qr_level          : The query level

                The possible value: ``PATIENT``, ``STUDY`` or ``SERIES``

            | aec               : Application Entity target Name
            | ae_cstore         : Application Entity to send CSTORE
            | patient_id        : The patient ID
            | study_uid         : The study UID
            | series_uid        : The series UID
            | file_uid          : The file UID
            | reloadStudy       : If True will reload the study already
                present in db if False won't (default False)

        Example of kwargs:
            | {
            |   'func'          : <function cmove_action at 0x7fcfd2bb8950>,
            |   'action'        : 'move',
            |   'ip'            : '127.0.0.1',
            |   'port'          : 11111,
            |   'qr_level'      : 'STUDY',
            |   'aec'           : 'PACS1',
            |   'ae_cstore'     : 'PACS3',
            |   'patient_id'    : None,
            |   'study_uid'     : None,
            |   'series_uid'    : None,
            |   'file_uid'      : None,
            |   'reloadStudy'   : False
            | }

    :type kwargs: dict
    """
    log_sphere_commands(LOG_COMMAND_EVENT, 'move', kwargs)
    srv = Server()
    srv.send_cmove_request(**kwargs)


def cmove_existing_action(kwargs):
    """
        Launch the function send_cmove_request()

        :param kwargs: Parameters dictionary

            The list of parameters is:

                | func              : The function name
                | action            : Type of action, possible value is ``move``
                | ip                : The PACS internet protocol
                | port              : The port of PACS
                | qr_level          : The query level

                    The possible value: ``PATIENT``, ``STUDY`` or ``SERIES``

                | aec               : Application Entity target Name
                | ae_cstore         : Application Entity to send CSTORE
                | patient_id        : The patient ID
                | study_uid         : The study UID
                | series_uid        : The series UID
                | file_study_uid    : The study file UID
                | reloadStudy       : If True will reload the study already
                    present in db if False won't (default False)

            Example of kwargs:
                | {
                |   'func'          : <function cmove_action at 0x7fcfd2bb8950>,
                |   'action'        : 'move',
                |   'ip'            : '127.0.0.1',
                |   'port'          : 11111,
                |   'qr_level'      : 'STUDY',
                |   'aec'           : 'PACS1',
                |   'ae_cstore'     : 'PACS3',
                |   'patient_id'    : None,
                |   'study_uid'     : None,
                |   'series_uid'    : None,
                |   'file_study_uid': None,
                |   'reloadStudy'   : False
                | }

        :type kwargs: dict
        """
    log_sphere_commands(LOG_COMMAND_EVENT, 'cmove_existing', kwargs)
    srv = Server()
    srv.send_cmove_existing_request(**kwargs)
    # TODO : Ajouter un return code pour chaque type d'action,
    #  selon le statut final de l'action


def assoc_action(kwargs):
    """
    Read association in association file and
    create server and
    add association and parameter then
    execute adapted action

    :param kwargs: A dictionary that contains (assoc)
    """
    log_sphere_commands(LOG_COMMAND_EVENT, 'assoc', kwargs)
    srv = Server()
    srv.send_assoc_request(assoc=kwargs['assoc'])


def database_action(kwargs):
    """
    Read association in association file and
    create server and
    add association and parameter then execute adapted action

    :param kwargs: Parameters dictionary

        The list of parameters is:

            | func      : The function name
            | action    : Type of action, possible value is ``database``
            | db_action : The action

                The possible value: ``create``, ``drop`` or ``clean``

        Example of kwargs:
            | {
            |   'func'      : <function database_action at 0x7f10c44fea60>,
            |   'action'    : 'database',
            |   'db_action' : 'clean'
            | }

    :type kwargs: dict
    """

    log_sphere_commands(LOG_COMMAND_EVENT, 'database', kwargs)
    dbp = DatabasePACS()
    action = kwargs['db_action']
    if "force_drop_db" in kwargs:
        f_drop = kwargs['force_drop_db']
    else:
        f_drop = None
    if action == 'create':
        dbp.create_tables()
    elif action == 'drop':
        dbp.drop_tables(f_drop)
    elif action == 'clean':
        dbp.clean_tables(f_drop)


def monitor_action(kwargs):
    """
    Run command monitor

    :param kwargs: Parameters dictionary

        The list of parameters is:

            | func      : Function name
            | action    : Type of action, possible value is ``monitor``
            | concept   : The concept

                The possible value: ``speed`` or ``modality``

            | data_level: The display level

                The possible value: ``full``, ``minimal`` or ``key``

        Example of kwargs:
            | {
            |   'func'      : <function monitor_action at 0x7f66dc2d8b70>,
            |   'action'    : 'monitor'
            |   'concept'   : 'speed',
            |   'data_level': 'full'
            | }

    :type kwargs: dict
    """
    log_sphere_commands(LOG_COMMAND_EVENT, 'monitor', kwargs)
    mon_cmd = CommandMonitor(**kwargs)
    mon_cmd.execute()


def request_action(kwargs):
    """
    Run command database

    :param kwargs: Parameters dictionary

        The list of parameters is:

            | func      : Function name
            | action    : Type of action, possible value is ``database``
            | db_action   : The action od database

                The possible value: ``check`` or ``find``

            | concept: The display level

                The possible value:
                    ``patient, study, series, fileStorageMetadataDicom``

            | data_level: The display level

                The possible value: ``full``, ``minimal`` or ``key``

            | attribute: The attribute

                The possible value:
                    ``seriesUID, studyUID, modality or patientID``

            | filter_value: The filter value

        Example of kwargs:
            | {
            |   'func': <function request_action at 0x7f7f12178ae8>,
            |   'action': 'database',
            |   'db_action': 'find',
            |   'data_level': 'full',
            |   'concept': 'study',
            |   'attribute': 'studyUID',
            |   'filter_value': 4305052317,
            |   'output_filepath': None,
            |   'force_overwrite': False,
            |   'file_format': None,
            |   'list_filepath': None,
            |   'header': False,
            |   'append': False
            | }

    :type kwargs: dict
    """
    log_sphere_commands(LOG_COMMAND_EVENT, 'request', kwargs)
    req_cmd = CommandDatabase(**kwargs)
    req_cmd.execute()


def data_action(kwargs):
    """
    Run command file access

    :param kwargs: Parameters dictionary

        The list of parameters is:

            | func      : Function namelist_study_uid
            | action    : Type of action, possible value is ``data``
            | data_action   : The data action

                The possible value: ``export``, ``index`` or ``index_study``

            | target_dir: The path of target directory
                ( exists if `data_action` equal ``export``)
            | list_study_uid: name file of list study uid
                ( exists if `data_action` equal ``index_study``)
            | d_load: The data of load
                ( exists if `data_action` equal ``index_study``)

        Example of kwargs: `data_action` equal ``export``
            | {
            |   'func'          : <function data_action at 0x7fe8d8b5d2f0>,
            |   'action'        : 'data',
            |   'data_action'   : 'export',
            |   'target_dir'    : 'file_uid'
            | }

    :type kwargs: dict
    """
    log_sphere_commands(LOG_COMMAND_EVENT, 'data', kwargs)
    req_cmd = CommandFileAccess(**kwargs)
    req_cmd.execute()


# pylint:disable=no-else-return
def str2bool(string):
    """
    Convert str to bool

    :param string: The string
    :type string: str
    :return: True or False
    :rtype: bool
    """
    if string.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif string.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def executeAction():
    """
    Read actions parameter execute needed action
    """
    parser = argparse.ArgumentParser(prog="sphere")
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('-vp', '--version_pacs', action='version',
                        help="Displays the version of Sphere with which the "
                             "PACS is created",
                        version='Version pacs : ' + version_pacs)
    subparsers = parser.add_subparsers(description='All subcommands of sphere',
                                       help='PACS action to realize',
                                       dest="action")

    # *********************************************************************** #
    # ******************** Sub Command for runserver ************************ #
    # *********************************************************************** #
    parser_runserver = subparsers.add_parser('runserver', help='RunServer ')
    parser_runserver.set_defaults(func=pacs_server_run)

    # *********************************************************************** #
    # ********************** Sub Command for cecho ************************** #
    # *********************************************************************** #
    parser_echo = subparsers.add_parser('echo', help='C-ECHO to a target PACS')
    parser_echo.set_defaults(func=cecho_action)
    positional_echo = parser_echo.add_argument_group('positional arguments')
    required_echo = parser_echo.add_argument_group('required arguments')
    optional_echo = parser_echo.add_argument_group('optional arguments')

    positional_echo.add_argument('ip', help='PACS target IP')
    positional_echo.add_argument('port', help='PACS target port', type=int)
    required_echo.add_argument(
        '-aec', '--ae_called', help='Application Entity target Name (AE)',
        required=True, const=None, dest='aec')

    optional_echo.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2],
                               dest='verbose',
                               help='Increase output verbosity; '
                                    '0=quiet mode, '
                                    '1=verbose mode, '
                                    '2=ultra-verbose mode')

    # *********************************************************************** #
    # ********************** Sub Command for store ************************** #
    # *********************************************************************** #
    parser_store = subparsers.add_parser(
        'store', help='C-STORE to a target PACS')
    parser_store.set_defaults(func=cstore_action)
    parser_store.add_argument('ip', help='PACS target IP')
    parser_store.add_argument('port', help='PACS target port', type=int)
    parser_store.add_argument(
        '-aec', '--ae_called', required=True,
        help='Application Entity target Name (AE)', const=None, dest='aec')
    parser_store.add_argument(
        '-sp', '--source_paths', required=True,
        help='Retrieve the paths of the instances of the database or '
             'the folder. choices db (database) or fs (file system).'
             'If db requires additional args model_name and fileUID.'
             'if fs requires additional args dicom_path.',
        const=None,
        choices=['db', 'fs'], dest='source_paths_db_fs')

    list_argv = sys.argv
    intersection_argv = {"db", "fs"} & set(list_argv)
    if 'db' in list_argv or intersection_argv == set():
        parser_store.add_argument(
            '-mn', '--model_name', nargs='?',
            help="What is the model_name of uid choices patient, study or "
                 "series [default: study]",
            const=None, default='study', choices=['patient', 'study', 'series',
                                                  'instance'],
            dest='model_name')
        group = parser_store.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '-fUID', '--fileUID',
            help='A file path that contains a list of uid',
            const=None, dest='uid_file_path')
        group.add_argument(
            '-UID', '--anyUID', nargs='?',
            help='Any Uid of (patient, study, series or instance) for the '
                 'research', const=None, dest='any_uid')

    if 'fs' in list_argv or intersection_argv == set():  # file system
        parser_store.add_argument(
            '-pd', '--dicom_path', required=True,
            help='The path to dicom directory or file',
            const=None, dest='path_dicom_dire_or_file')

    parser_store.add_argument(
        '-context', '--name_context', help="Name of the project's context",
        default=None, dest='context')
    parser_store.add_argument(
        '-ma', '--many_assoc', dest='many_assoc', default='True',
        help='Many associate [default: True]', type=str2bool)
    parser_store.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2],
                              dest='verbose', help='Increase output verbosity; '
                                                   '0=quiet mode, '
                                                   '1=verbose mode, '
                                                   '2=ultra-verbose mode')

    # *********************************************************************** #
    # *********************** Sub Command for move ************************** #
    # *********************************************************************** #
    parser_move = subparsers.add_parser('move', help='C-MOVE to a target PACS')
    parser_move.set_defaults(func=cmove_action)
    parser_move.add_argument('ip', help='PACS target IP')
    parser_move.add_argument('port', help='PACS target port', type=int)
    parser_move.add_argument(
        '-aec', '--ae_called', help='Application Entity target Name (AE)',
        required=True, const=None, dest='aec')
    parser_move.add_argument(
        '-aes', '--ae_cstore', help='Application Entity to send CSTORE (AE)',
        required=True, const=None, dest='ae_cstore')
    parser_move.add_argument(
        '-l', '--QRLevel', nargs='?', choices=['PATIENT', 'STUDY', 'SERIES'],
        help='Query Retrieve Level; [default: STUDY]', const=None,
        default='STUDY', dest='qr_level')
    parser_move.add_argument(
        '-paID', '--patientID', help='An patient Id for search', const=None,
        dest='patient_id')
    parser_move.add_argument(
        '-stUID', '--studyUID', help='An Study Uid for search', const=None,
        dest='study_uid')
    parser_move.add_argument(
        '-seUID', '--seriesUID', help='An series Uid for search',
        const=None, dest='series_uid')
    parser_move.add_argument(
        '-fUID', '--fileUID', help='A Uid file', const=None,
        dest='file_uid')
    parser_move.add_argument(
        '-DbUID', '--databaseUID', help='load done by the data base table'
                                        ' study_list if no arguments given'
                                        ' the last study_list loaded will'
                                        ' be used, you can also give an id_list'
                                        ' if done so the load will be based'
                                        ' on the list having the given id_list',
        const=None, dest='db_study_uid', nargs='?')
    parser_move.add_argument(
        '-rl', '--reloadStudy', help='boolean if True will reload the study'
                                     ' already  present in db if False won\'t'
                                     ' default set to True '
                                     ' /!\\ only working if the pacs runing the'
                                     ' cmove and the one one receiving the data'
                                     ' are the same or share the same database',
        default=True, dest='reload_study', nargs='?', type=str2bool)
    parser_move.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2],
                             dest='verbose', help='Increase output verbosity; '
                                                  '0=quiet mode, '
                                                  '1=verbose mode, '
                                                  '2=ultra-verbose mode')

    # *********************************************************************** #
    # ******************* Sub Command for move_existing ********************* #
    # *********************************************************************** #
    parser_move_existing = subparsers.add_parser('move_existing',
                                                 help='C-MOVE to a target PACS')
    parser_move_existing.set_defaults(func=cmove_existing_action)
    parser_move_existing.add_argument('ip', help='PACS target IP')
    parser_move_existing.add_argument('port', help='PACS target port', type=int)
    parser_move_existing.add_argument(
        '-aec', '--ae_called', help='Application Entity target Name (AE)',
        required=True, const=None, dest='aec')
    # FIND
    parser_move_existing.add_argument(
        '-ow', '--overwrite', help='overwrite file', dest='overwrite',
        type=str2bool)
    parser_move_existing.add_argument(
        '-l', '--QRLevel', nargs='?', help='Query Retrieve Level; '
                                           '[default: STUDY]', const=None,
        default='STUDY', dest='qr_level')
    # MOVE
    parser_move_existing.add_argument(
        '-aes', '--ae_cstore', help='Application Entity to send CSTORE (AE)',
        required=True, const=None, dest='ae_cstore')
    parser_move_existing.add_argument(
        '-o', '--output', help='Output file', const='.', dest='output_filepath',
        nargs='?')
    parser_move_existing.add_argument(
        '-paID', '--patientID', help='An patient Id for search', const=None,
        dest='patient_id')
    parser_move_existing.add_argument(
        '-stUID', '--studyUID', help='An Study Uid for search', const=None,
        dest='study_uid')
    parser_move_existing.add_argument(
        '-seUID', '--seriesUID', help='An series Uid for search',
        const=None, dest='series_uid')
    parser_move_existing.add_argument(
        '-fUID', '--fileUID', help='A Study Uid file', const=None,
        dest='file_study_uid')
    parser_move_existing.add_argument(
        '-DbUID', '--databaseUID', help='load done by the data base table'
                                        ' study_list if no arguments given'
                                        ' the last study_list loaded will'
                                        ' be used, you can also give an id_list'
                                        ' if done so the load will be based'
                                        ' on the list having the given id_list',
        const=None, dest='db_study_uid', nargs='?')
    parser_move_existing.add_argument(
        '-rl', '--reloadStudy', help='boolean if True will reload the study'
                                     ' already  present in db if False won\'t'
                                     ' default set to True '
                                     ' /!\\ only working if the pacs runing the'
                                     ' cmove and the one one receiving the data'
                                     ' are the same or share the same database',
        default=True, dest='reload_study', nargs='?', type=str2bool)
    parser_move_existing.add_argument("-v", "--verbosity", type=int,
                                      choices=[0, 1, 2],
                                      dest='verbose',
                                      help='Increase output verbosity; '
                                           '0=quiet mode, '
                                           '1=verbose mode, '
                                           '2=ultra-verbose mode')

    # *********************************************************************** #
    # *********************** Sub Command for find ************************** #
    # *********************************************************************** #
    parser_find = subparsers.add_parser('find', help='C-FIND to a target PACS')
    parser_find.set_defaults(func=cfind_action)
    parser_find.add_argument('ip', help='PACS target IP')
    parser_find.add_argument('port', help='PACS target port', type=int)
    parser_find.add_argument(
        '-aec', '--ae_called', help='Application Entity target Name (AE)',
        required=True, const=None, dest='aec')
    parser_find.add_argument(
        '-l', '--QRLevel', nargs='?', choices=['PATIENT', 'STUDY', 'SERIES'],
        help='Query Retrieve Level; [default: STUDY]', const=None,
        default='STUDY', dest='qr_level')
    parser_find.add_argument(
        '-stUID', '--studyUID', help='An Study Uid for search', const=None,
        dest='study_uid')
    parser_find.add_argument(
        '-paID', '--patientID', help='An patient Id for search', const=None,
        dest='patient_id')
    parser_find.add_argument(
        '-seUID', '--seriesUID', help='An series Uid for search', const=None,
        dest='series_uid')
    parser_find.add_argument(
        '-o', '--output', help='Output file', const='.', dest='output_filepath',
        nargs='?')
    parser_find.add_argument(
        '-d', '--display', help='display all dataset; [default: False]',
        dest='display_ds', default=False, type=str2bool)
    parser_find.add_argument(
        '-ow', '--overwrite', help='overwrite file', dest='overwrite',
        type=str2bool)

    parser_find.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2],
                             dest='verbose', help='Increase output verbosity; '
                                                  '0=quiet mode, '
                                                  '1=verbose mode, '
                                                  '2=ultra-verbose mode')

    # *********************************************************************** #
    # *********************** Sub Command for assoc ************************* #
    # *********************************************************************** #
    parser_assoc = subparsers.add_parser(
        'assoc', help='Use an predefined Assoc')
    parser_assoc.set_defaults(func=assoc_action)
    parser_assoc.add_argument(
        'assoc', help='Nom complet de l\'assoc ([target_pacs].[request])')

    # *********************************************************************** #
    # ********************* Sub Command for database ************************ #
    # *********************************************************************** #
    parser_database = subparsers.add_parser('database', help='Manage Database')
    subparsers_database = parser_database.add_subparsers(
        help='Database', dest="db_action")
    # --
    parser_database_clean = subparsers_database.add_parser(
        'clean', help='Drop and create database (WARNING : All database '
                      'entries will be definitely deleted)')
    parser_database_clean.set_defaults(func=database_action)
    parser_database_clean.add_argument(
        '-f', '--force', help='Force drop database', type=str2bool,
        dest='force_drop_db')
    # --
    parser_database_drop = subparsers_database.add_parser(
        'drop', help='Drop database (WARNING : All database entries will '
                     'be definitely deleted)')
    parser_database_drop.set_defaults(func=database_action)
    parser_database_drop.add_argument(
        '-f', '--force', help='Force drop database', type=str2bool,
        dest='force_drop_db')
    # --
    parser_database_create = subparsers_database.add_parser(
        'create', help='Create/Initialize Database')
    parser_database_create.set_defaults(func=database_action)

    # Sub Command for request
    # --
    parser_request_check = subparsers_database.add_parser(
        'check', help='Check if list find is find in database')
    parser_request_check.set_defaults(func=request_action)
    parser_request_check.add_argument(
        'concept',
        choices=['patient', 'study', 'series', 'fileStorageMetadataDicom'],
        help='choose object to find')
    parser_request_check.add_argument(
        'list_filepath',
        help='list of value in text file (one value by column)')
    parser_request_check.add_argument(
        'output_filepath', help='Output file', const='.', nargs='?',)
    parser_request_check.add_argument(
        '-oc', '--output-concept',
        choices=['patient', 'study', 'series', 'fileStorageMetadataDicom'],
        help='Export mode, if diff, only no find are write in output file',
        dest='output_concept')
    parser_request_check.add_argument(
        '-m', '--mode', choices=['diff', 'equal', 'detailled'],
        dest='check_mode', default='diff',
        help='Export mode, if diff, only no find are write in output file/equal'
             ' give all find/detailled (only if output concept is same of '
             'concept) return 1 or 0 in csv format; [default: diff]')

    parser_request_find = subparsers_database.add_parser(
        'find', help='Find an entry in database (DO NOT USE)')
    parser_request_find.set_defaults(func=request_action)
    parser_request_find.add_argument(
        '-o', '--output', help='Output file', const='.', dest='output_filepath',
        nargs='?',)
    parser_request_find.add_argument(
        '-f', '--force', help='Force write file', action='store_true',
        dest='force_overwrite')
    parser_request_find.add_argument(
        '-A', '--append', help='Append file', action='store_true',
        dest='append')
    parser_request_find.add_argument(
        '-H', '--header', help='Append header', action='store_true',
        dest='header')
    parser_request_find.add_argument(
        '-e', '--file-format', choices=['csv', 'json'], help='File format',
        const='csv', nargs='?', dest='file_format')
    parser_request_find.add_argument(
        '-d', '--display_level', choices=['full', 'minimal', 'key'],
        help='Display level; [default: key]', nargs='?', default='key', dest='data_level')
    parser_request_find.add_argument(
        'concept',
        choices=['patient', 'study', 'series', 'fileStorageMetadataDicom'],
        help='choose object to find')
    parser_request_find.add_argument(
        '-a', '--attribute',
        choices=['seriesUID', 'studyUID', 'modality', 'patientID'], nargs='?',
        default='studyUID', help='choose filtering column; [default: studyUID]',
        dest='attribute')
    parser_request_find.add_argument(
        '-V', '--value', help='choose filter value', dest='filter_value')
    parser_request_find.add_argument(
        '-l', '--value-list',
        help='list of value in text file (one value by column',
        dest='list_filepath')

    # *********************************************************************** #
    # ********************** Sub Command for monitor ************************ #
    # *********************************************************************** #
    parser_monitor = subparsers.add_parser('monitor', help='PACS statistics')
    parser_monitor.set_defaults(func=monitor_action)
    parser_monitor.add_argument(
        'concept', choices=['modality', 'speed'], help='choose metadata')
    parser_monitor.add_argument(
        '-d', '--display_level', choices=['full', 'minimal', 'key'],
        help='Display level', nargs='?', default='key', dest='data_level')

    # *********************************************************************** #
    # ************************ Sub Command for data ************************* #
    # *********************************************************************** #
    parser_data = subparsers.add_parser(
        'data', help='DICOM file management and export')
    subparsers_data = parser_data.add_subparsers(
        help='data', dest="data_action")
    parser_data.set_defaults(func=data_action)

    # Sub Command for index
    # --
    parser_data_index = subparsers_data.add_parser(
        'index',
        help='Index data Folder in database to regenerate DICOM database')
    parser_data_index.add_argument(
        '-rm', '--erase', help='boolean if True will erase the local files '
                               'from the local directory default set to False ',
        default=False, dest='erase', nargs='?', type=str2bool)

    parser_data_index.add_argument(
        '-d', '--directoryDicom', help='The DICOM files folder', const=None,
        dest='directory_dicom')

    # Sub Command for export
    # --
    parser_data_copy = subparsers_data.add_parser(
        'export', help='Copy data Folder to other destination')
    parser_data_copy.add_argument(
        'target_dir',
        help='Output folder to put data. If data with same local '
             'file path exist, itsn\'t, copy')

    # Sub Command for index_study
    # --
    parser_data_index_study = subparsers_data.add_parser(
        'index_study',
        help='Index file of study uid file in the database')
    parser_data_index_study.add_argument(
        'list_study_uid',
        help='list of value in text file (one value by column)')
    parser_data_index_study.add_argument(
        'd_load', help='date of the load of the list, in format, yyyy-mm-dd,\
         if none given the date of the day will be piked', nargs='?')

    # --
    parse = parser.parse_args()
    args = vars(parser.parse_args())

    parse.func(args)

    # TODO : Ameliorer l'action avec le traitement des lignes de commandes
    #  et help
    # TODO : retourner le code de l'action en fonction de la demande


if __name__ == '__main__':
    import sys
