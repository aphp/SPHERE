""" The server """
import os
import sys
import subprocess
from time import sleep

import psutil

from sphere.pacs.ae import SphereAE
from sphere.dicmeta.thread import ThreadDatabase, g_queue_to_load
from sphere.utilities.msg import term_bold, term_green, term_red, TERMINAL_MESSAGE
from sphere.utilities.utils_database import check_db_pacs
from sphere.utilities.file import read_file_txt
from sphere import settings
from sphere.api_rest import utils
from sphere.logs.logs import LOG_API_ANNOTATION, LOG_TRANSACTION


class Server:
    """ The method os server"""
    def __init__(self):
        self.g_queue_to_load = g_queue_to_load
        self.ae = SphereAE(g_queue_to_load)  # pylint: disable=invalid-name

    def run(self):
        """ Run server """
        self.thread_db_save = ThreadDatabase(1, 'thread_db_save', 1)
        self.ae.initialize_callback_action()
        if settings.START_API:
            self.run_api_rest()  # Start API rest
        try:
            if not check_db_pacs(check_exists_data=False):
                LOG_TRANSACTION.info("The thread_db_save thread is not running.")
            else:
                self.thread_db_save.start()  # Start thread_db_save
                sleep(0.1)

            self.display_server_status()
            self.ae.start()
        except Exception as exc:
            LOG_TRANSACTION.exception(exc)
        print("\nDICOM Server {} has been stopped".format(
            self.ae.ae_title.decode('utf-8')))
        if settings.START_API:
            self.pkill_process_api_rest()  # kill API rest
        self.thread_db_save.stop_thread()

    @staticmethod
    def run_api_rest():
        """ start Api rest """
        try:
            cmd = settings.COMMAND_RUN_API
            LOG_API_ANNOTATION.debug("The command to launch the API is: %s", cmd)
            # Check if the API is already launched or not
            if utils.check_api_connect():
                LOG_API_ANNOTATION.info(
                    "Server API is not open; We will launch the API")
                try:
                    _process = subprocess.Popen(
                        cmd, shell=True, stderr=subprocess.STDOUT,
                        executable='/bin/bash')

                    # A little time to check if the API is connect or not
                    sleep(15)
                    if utils.check_api_connect():
                        LOG_API_ANNOTATION.error(
                            "I think we have a problem with the command '%s'; "
                            "the server is not launching and check stdout of "
                            "API", cmd)
                except KeyboardInterrupt:
                    LOG_API_ANNOTATION.info(" Exit manually")
                    print(" Exit manually")
                    try:
                        sys.exit(1)  # this always raises SystemExit
                    except SystemExit:
                        msg = "sys.exit() worked as expected"
                        LOG_API_ANNOTATION.warning(msg)
                        print(msg)
                    except Exception as error:
                        print("Something went horribly wrong")
                        LOG_API_ANNOTATION.warning(error)
                except Exception as error:
                    LOG_API_ANNOTATION.exception(error)
                LOG_API_ANNOTATION.info("API is launched")
            else:
                LOG_API_ANNOTATION.warning("Server API is open")
        except Exception as error:
            LOG_API_ANNOTATION.exception(error)

    @staticmethod
    def pkill_process_api_rest():
        """ pkill process api rest"""
        LOG_API_ANNOTATION.info("Start pkill process API")
        pid_api = read_file_txt(settings.NAME_FILE_PID_SERVER_API)
        if pid_api is not None:
            # If api is open or pid_api exists
            pid_exists = psutil.pid_exists(int(pid_api))  # utils.check_pid(int(pid_api))
            if not utils.check_api_connect() or pid_exists:
                if utils.check_api_connect():  # If api is not open
                    LOG_API_ANNOTATION.warning("The API is not launched ")
                else:  # Server API is open and pid_api exits
                    if pid_exists:
                        LOG_API_ANNOTATION.debug("A process with pid %s exists ",
                                                 str(pid_api).replace('\n', ''))
                        cmd_pkill = "pkill -P " + str(pid_api)
                        LOG_API_ANNOTATION.debug("kill this pid '%s' with this "
                                                 "command '%s' ",
                                                 pid_api.replace('\n', ''),
                                                 cmd_pkill.replace('\n', ''))
                        os.system(cmd_pkill)
                        LOG_API_ANNOTATION.debug("Process kill")
                        os.system("rm  " + settings.NAME_FILE_PID_SERVER_API)
                    else:
                        LOG_API_ANNOTATION.error("A process with pid %s does "
                                                 "not exist in list of process",
                                                 pid_api)
            else:
                LOG_API_ANNOTATION.warning("Server API is not open")
        else:
            if utils.check_api_connect():
                LOG_API_ANNOTATION.warning("This file '%s'does not exit and "
                                           "Server API is not open",
                                           settings.NAME_FILE_PID_SERVER_API)
            else:
                LOG_API_ANNOTATION.warning(
                    "Server API is open but I donet killed API beceause "
                    "this file '%s'does not exit and or it is lanchund with "
                    "a other PACS",
                    settings.NAME_FILE_PID_SERVER_API)

    def send_cecho_request(self, **kwargs):
        """
        Run the scu_cecho_action()

        :param ip: The IP
        :type ip: str
        :param port: The port
        :type port: str
        :param aec: Application Entity target Name
        :type aec: str, optional
        """
        self.ae.scu_cecho_action(**kwargs)

    def send_cstore_request(self, **kwargs):
        """
        Run the scu_cstore_action

        :param kwargs: The arguments of the cstores command. Kwargs comments in
            the function "cstore_action()" exists in "parser.py"
        :type kwargs: dict
        :return: function/method reference call for scu_cstore_action
        """
        self.ae.scu_cstore_action(**kwargs)

    def send_cfind_request(self, **kwargs):
        """
        Run the method scu_cfind_action()

        :param kwargs: The arguments of the cfind command. Kwargs comments in
            the function "cfind_action()" exists in "parser.py"
        :type kwargs: dict
        :return: function/method reference call for scu_cfind_action
        """
        self.ae.scu_cfind_action(**kwargs)

    def send_cmove_request(self, **kwargs):
        """
        Run the method scu_cmove_action()

        :param kwargs: The arguments of the cmove command. Kwargs comments in
            the function "cmove_action()" exists in "parser.py"
        :type kwargs: dict
        :return: function/method reference call for scu_cmove_action
        """
        self.ae.scu_cmove_action(**kwargs)

    def send_cmove_existing_request(self, **kwargs):
        """
        Run the method scu_cmove_list_action()

        :param kwargs: The arguments of the cmove_existing command. Kwargs comments in
            the function "cmove_existing_action()" exists in "parser.py"
        :type kwargs: dict
        :return: function/method reference call for scu_cmove_existing_action
        """
        self.ae.scu_cmove_existing_action(**kwargs)

    def send_assoc_request(self, assoc):
        """
        Send assoc request

        :param assoc: The assoc
        :type assoc: str
        """
        # TODO revoir le passage de kwargs
        req = assoc_request_parser(assoc)
        target = req['target']
        action = req['action']

        if target in settings.ASSOCIATIONS:
            con_info = settings.ASSOCIATIONS[target]
        else:
            # TODO Create rease Exception pour ce if
            print('ERROR : "'+target+'" Not find in association.yml')
            sys.exit()
        if action in con_info['requests']:
            act_info = con_info['requests'][action]
        else:
            # TODO Create rease Exception pour ce if
            print(
                'ERROR : "'+action+'" Not find in requests for "' + target +
                '" association in association.yml')
            sys.exit()

        if act_info['action'] == 'scu_cecho':
            self.send_cecho_request(
                ip=con_info['ip'], port=con_info['port'], aec=con_info['aet'])
        if act_info['action'] == 'scu_cfind':
            print("TODO CFIND ASSOC")
        if act_info['action'] == 'scu_cstore':
            print("TODO CSTORE ASSOC")
        if act_info['action'] == 'scu_cmove':
            print("TODO CMOVE ASSOC")

    def display_server_status(self):
        """ Display server status """
        print(TERMINAL_MESSAGE.format(
            scp_ae_title=self.ae.ae_title.decode('utf-8'),
            scp_ae_port=term_bold(self.ae.port),
            scp_service_cecho=service_status('c-echo'),
            scp_service_cstore=service_status('c-store'),
            scp_service_cfind=service_status('c-find'),
            scp_service_cmove=service_status('c-move'),
            service_thread_db_save=self.thread_db_save.state,
            extended_db=term_bold(term_green('ON')) if settings.EXTENDED else term_bold(term_red('OFF')),
            sphere_dicomweb=on_or_off(settings.START_DICOMWEB),
            api_annotation=on_or_off(settings.START_ANNOTATION)
            ))
##########################
# Utils Functions
#
##########################


def on_or_off(start):
    """
    Check if api is open and return ON or OFF

    :param start: The application is start or not
    :type start: bool
    :return: Return ON or OFF
    :rtype: str
    """
    if start:
        if utils.check_api_connect() == 0:
            return term_bold(term_green('ON'))
    return term_bold(term_red('OFF'))


def assoc_request_parser(txt):
    """
    Split string and return in dictionary

    :param txt: The string
    :type txt: str
    :return: Return a dictionary
    :rtype: dict
    """
    tmp = txt.split('.')
    return {'target': tmp[0], 'action': tmp[1]}


def service_status(service):
    """
    Add color of service

    :param service: The service
    :type service: str
    :return: Add color
    :rtype: str
    """
    # TODO : Faire une réeele vérification du statut du service en opération.
    #  Pas juste croire l'utilisateur.
    if service in settings.SCP_SERVICES:
        return term_bold(term_green('ON'))
    return term_bold(term_red('OFF'))
