""" Utility function for string """
import re
import shutil

from sphere.logs.logs import LOG_CODE_PYTHON


# pylint:disable=no-else-return
def str2bool(string):
    """
    Convert str to bool

    :param string: The string
    :type string: str, bool
    :return: True or False
    :rtype: bool
    """

    try:
        if isinstance(string, bool):
            return string
        else:  # if str
            if string.lower() in ('yes', 'true', 't', 'y', '1'):
                return True
            elif string.lower() in ('no', 'false', 'f', 'n', '0'):
                return False
    except Exception as exc:
        LOG_CODE_PYTHON.exception(exc)
    return string


def upper_level(level, list_level):
    """
    Upper the level

    :param level: The level of logging
    :type level: str
    :param list_level: The list pf level
    :type list_level: list
    :return: The level
    :rtype: str
    """
    try:
        if level is not None and level.upper().replace(" ", "") in list_level:
            level = level.upper().replace(" ", "")
    except Exception as exc:
        LOG_CODE_PYTHON.exception(exc)
    return level


def upper_first_letter(word):
    """
    Upper first letter

    :param word: The word
    :type word: str
    :return: The word with upper first letter
    :rtype: str
    """
    return re.sub('([a-zA-Z])', lambda x: x.groups()[0].upper(), word, 1)


def replace_id_uid(word):
    """
    Replace ID and UID with _id and _uid

    Example:
        | patientID ==> patient_id
        | studyUID ==> study_uid

    :param word: The word
    :type word: str
    :return: The word replace
    :rtype: str
    """
    if 'UID' in word:
        word = word[:-3] + "_uid"
    elif "ID" in word:
        word = word[:-2] + "_id"
    return word


def string_to_lower_no_space(string):
    """
    Lower string and replace space without empty

    :param string: The string
    :type string: str
    :return: The string lower and without space
    :rtype: str
    """
    string = string.lower()
    string.replace(" ", "")
    return string


def string_to_upper_no_space(string):
    """
    Upper string and replace space without empty

    :param string: The string
    :type string: str
    :return: The string upper and without space
    :rtype: str
    """
    string = string.upper()
    string.replace(" ", "")
    return string


def string_belongs_to_list_case_and_space_insensitive(
        string=None, list_strings=None):
    """
    Search string in list of strings

    :param string: The string
    :type string: str, optional
    :param list_strings: List of strings
    :type list_strings: list, optional
    :return: Return if string in list strings or not (True | False)
    :rtype: bool
    """
    if string is not None and list_strings is not None:
        string = string_to_lower_no_space(string)
        list_strings = [x.lower().replace(" ", "") for x in list_strings]
        if string in list_strings:
            return True
    return False


def pretty_size(num):
    """
    Pretty size

    :param num: The number
    :type num: int
    :return: Number and size unit
    :rtype: str
    """
    if num is not None:
        for unit in ['octets', 'Ko', 'Mo', 'Go', 'To', 'Po']:
            if abs(num) < 1024.0:
                return "%3.2f %s" % (num, unit)
            num /= 1024.0
        return "%.2f%s" % (num, unit)
    return None


def hard_disk_size():
    """
    Return Hard disk size (total, used and free) in gigabyte

    :return: total, used and free of disk space
    :rtype: tuple(int)
    """

    total, used, free = shutil.disk_usage("/")
    total = total // (2 ** 30)
    used = used // (2 ** 30)
    free = free // (2 ** 30)
    return total, used, free
