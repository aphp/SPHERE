""" log"""
import copy
from pprint import pformat


def log_sphere_commands(log, command_name, kwargs):
    """
    log of sphere commands

    :param log: Name of logging
    :type log: :py:class:`logging.Logger`
    :param command_name: The command sphere
    :type command_name: str
    :param kwargs: The arguments of the echo, stores, find, move,
        move_existing, assoc, database, monitor, request end data command.
    :type kwargs: dict
    """
    log.info("Start the command '%s' ", command_name)
    log.debug('{:*^70}'.format(' OUTGOING kwargs '))
    for key, value in kwargs.items():
        log.debug('{:<15}       : {!s}'.format(key, value))
    log.debug('{:*^70}'.format(' END kwargs '))


# pylint: disable=invalid-name
def log_dataset(log, ds, dcmpath=None):
    """
    Lod display dataset

    :param log: Name of logging
    :type log: :py:class:`logging.Logger`
    :param ds: The dataset
    :type ds: :py:class:`pydicom.dataset.Dataset`
    :param dcmpath: The path of file dicom
    :type dcmpath: str, optional
    """

    list_msg = list()
    list_msg.append('{:*^70}'.format(' OUTGOING DATASET '))
    if dcmpath:
        list_msg.append('DICOM file   : {0!s}'.format(dcmpath))
    list_msg.append('Study uid    : {0!s}'.format(ds.StudyInstanceUID))
    list_msg.append('Series uid   : {0!s}'.format(ds.SeriesInstanceUID))
    list_msg.append('Instance uid : {0!s}'.format(ds.SOPInstanceUID))
    list_msg.append('{:*^70}'.format(' END DATASET '))
    for msg in list_msg:
        log.debug(msg)


def logging_dict(log, dic, msg):
    """
    Display log

    :param log: Name of logging
    :type log: :py:class:`logging.Logger`
    :param dic: The dictionary
    :type dic: dict
    :param msg: The message
    :type msg: str
    """
    log.debug("{:-^70}".format(msg))
    if "parameters" in msg:
        copy_dic = copy.deepcopy(dic)
        copy_dic["db"]["params"]["ip"] = "I empty them"
        copy_dic["db"]["params"]["port"] = "I empty them"
        copy_dic["db"]["params"]["database"] = "I empty them"
        copy_dic["db"]["params"]["login"] = "I empty them"
        copy_dic["db"]["params"]["password"] = "I empty them"
    for line in pformat(dic).split('\n'):
        log.debug(line)
