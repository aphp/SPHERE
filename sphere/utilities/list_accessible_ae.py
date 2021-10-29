""" Function of list accessible ae """
# pylint: disable=invalid-name
import os
import traceback
import yaml
import re
import socket

from sphere import settings
from sphere.logs.logs import LOG_ACCESS


def list_all_access_list():
    """
    Search the list of associates

    :return: Return the list of associates
    :rtype: list
    """
    for root, _dirs, files in os.walk(settings.FS_PATH_WHITE_LIST):
        data = {}
        for file in files:
            LOG_ACCESS.info('file to open: %s', str(os.path.join(root, file)))
            with open(os.path.join(root, file), 'r') as stream:
                try:
                    data_loaded = yaml.load(stream)
                    LOG_ACCESS.debug('yaml loaded: %s', str(data_loaded))
                    data.update(data_loaded)
                except Exception:
                    traceback.print_exc()
                    LOG_ACCESS.error('error with yaml reading')
        return data


# # check auth for SCP (incoming SCU/ connexion)
def check_external_infos(ip, file_infos):
    """
    Check if ip in file_infos

    :param ip: The IP
    :type ip: str
    :param file_infos: The information
    :type file_infos: dict
    :return: Return True if ip in file_infos else return False
    :rtype: bool
    """
    LOG_ACCESS.info("Requestor IP is : " + ip)
    authorized_ip = get_authorized_ip(file_infos)

    if ip == authorized_ip:
        LOG_ACCESS.info('ip requestor and port of communication are valid')
        return True

    LOG_ACCESS.error('ip requestor is wrong')
    return False


def get_authorized_ip(file_infos):
    """
    Check the entris in the whitelist file. Resolve IP if a host is specified instead of an IP address.

    :param file_infos: The information
    """
    authorized_host = file_infos['ip'].strip()

    LOG_ACCESS.info("authorized host : " + authorized_host)
    if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", authorized_host):
        LOG_ACCESS.info("authorized host is an IP.")
        return authorized_host

    else:
        LOG_ACCESS.info("authorized host is not an IP.")
        authorized_ip = socket.gethostbyname(authorized_host)
        LOG_ACCESS.info("Resolved IP from hostname is : " + authorized_ip)
        return authorized_ip


def check_auth_file(aet, ip, data_loaded):
    """
    Check if aet in data_loaded

    :param aet: Application Entity title
    :type aet: str
    :param ip: The IP
    :type ip: str
    :param data_loaded: The data of file yml
    :type data_loaded: dict
    :return: Return True if aet in data_loaded else return False
    :rtype: bool
    """
    if aet in data_loaded.keys():
        LOG_ACCESS.info('aet requestor %s in list of authorized aet', aet)
        return check_external_infos(ip, data_loaded[aet])

    LOG_ACCESS.error('aet requestor %s not in list of authorized aet', aet)
    return False


def auth_in(event=None, action=None):
    """
    Check a authentication ( check if the aet and the ip in one of the
        file in the folder white list)

    :param event: The event
    :type event: :py:class:`pynetdicom.events.Event`, optional
    :param action: The action

        list of possible actions:
            | ``CECHO``
            | ``CSTORE``
            | ``CFIND``
            | ``CMOVE``
    :type action: str, optional
    :return: Return True or False
    :rtype: bool
    """
    if event is None or action is None:
        LOG_ACCESS.error('no event or action defined access not authorized')
        return False
    else:
        aet = event.assoc.requestor.ae_title.strip().decode("utf-8", "strict")
        ip = event.assoc.requestor.address.strip()
        port = settings.SCP_PORT
        for root, _dirs, files in os.walk(settings.FS_PATH_WHITE_LIST):
            nb_file = len(files)
            LOG_ACCESS.debug('nb file: %s', str(nb_file))
            file_nu = 1
            for file in files:
                LOG_ACCESS.info(
                    'file to open: %s', str(os.path.join(root, file)))
                with open(os.path.join(root, file), 'r') as stream:
                    try:
                        data_loaded = yaml.safe_load(stream)
                        LOG_ACCESS.debug('yaml loaded: %s', str(data_loaded))
                        LOG_ACCESS.debug('aet: ' + aet + ' ip: ' + ip +
                                         ' port: ' + str(port) +
                                         ' action: ' + action)
                        auth = check_auth_file(aet, ip, data_loaded)
                        if auth or file_nu == nb_file and not auth:
                            return auth

                    except Exception:
                        traceback.print_exc()
                        LOG_ACCESS.error('error with yaml reading')
                file_nu = file_nu+1
