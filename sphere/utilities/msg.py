"""List of text display function"""
import time


# terminal functions
def term_red(string):
    """
    Display the string in red color

    :param string: The string
    :type string: str
    :return: Return the string in red color
    :rtype: str
    """
    return '\033[91m{}\033[0m'.format(str(string))


def term_green(string):
    """
    Display the string in green color

    :param string: The string
    :type string: str
    :return: Return the string in green color
    :rtype: str
    """
    return '\033[92m{}\033[0m'.format(str(string))


def term_bold(string):
    """
    Display the string in bold color

    :param string: The string
    :type string: str
    :return: Return the string in bold color
    :rtype: str
    """
    return '\033[01m{}\033[0m'.format(str(string))


# terminal message of runserver
TERMINAL_MESSAGE = "#+++++++++++++++++++++++++++\n" \
     "# DICOM Server {scp_ae_title}\n" \
     "# Port : {scp_ae_port}\n" \
     "# (SCP)C-ECHO\t{scp_service_cecho}\n" \
     "# (SCP)C-STORE\t{scp_service_cstore}\n" \
     "# (SCP)C-FIND\t{scp_service_cfind}\n" \
     "# (SCP)C-MOVE\t{scp_service_cmove}\n" \
     "# Thread database save\t{service_thread_db_save}\n" \
     "# Extended database\t{extended_db}\n"\
     "# Api Sphere DicomWeb \t{sphere_dicomweb}\n" \
     "# Api Annotation \t{api_annotation}\n" \
     "#+++++++++++++++++++++++++++"


def execution_time(start_time):
    """
    The execution time of a program in hours, minutes and seconds format

    :param start_time: the time
    :type start_time: folder
    :return: Program execution time
    :rtype: str
    """
    return time.strftime("Execution time : %H:%M:%S", time.gmtime(
        time.time() - start_time))


# -_-_-_-_-_-_-_-_-_Message log settings-_-_-_-_-_--_ #


def message_bool(name_param, base_value, default_value):
    """
    Return a message to verify a boolean

    :param name_param: Name of parameter
    :type name_param: str
    :param base_value: The base value
    :type base_value: str, list, ...
    :param default_value: The default value
    :type default_value: bool
    :return: The massage
    :rtype: str
    """
    msg = "This value '{0}' is invalid, here is the list of values ​that we " \
          "can accept : \n [True, 'yes', 'true', 't', 'y', '1', False, 'no', " \
          "'false', 'f', 'n', '0']. The default value {1} = {2} ".\
          format(base_value, name_param, default_value)
    return msg


def message_critical(name_param, type_param=None):
    """
    Return message

    :param name_param: Name of parameter
    :type name_param: str
    :param type_param: Type value of parameter
    :type type_param:
    :return: The message
    :rtype: str
    """
    msg_type = ""
    if type_param == int:
        msg_type = "(must be integer or float)"
    elif type_param == bool:
        msg_type = "(must be boolean)"

    msg_critical = "Server has been killed because value for '%s' parameter " \
                   "must be defined in setting file %s." % (name_param,
                                                            msg_type)
    return msg_critical


def message_int(name_param, value_param):
    """

    :param name_param: Name of parameter
    :type name_param: str
    :param value_param: Value of parameter
    :type value_param:
    :return: The massage
    :rtype: str
    """
    msg_int = "Only numbers accepted. The default value {0} = {1}".format(
        name_param, value_param)
    return msg_int


def message_key_error(name_param, value_param):
    """

    :param name_param: Name of parameter
    :type name_param: str
    :param value_param: Value of parameter
    :type value_param: str, bool
    :return: The massage
    :rtype: str
    """
    tab = '\t' * 16
    msg_key_error = "The '{0}' parameter does not exists in settings file. " \
                    "\n {2} The default value = {1} ".format(
                        name_param, value_param, tab)
    return msg_key_error


def message_value_none(param, default_value):
    """
    The message if value of param is None

    :param param: Name of parameter
    :type param: str
    :param default_value: The default value of parameter
    :type default_value:
    :return: The message
    :rtype: str
    """
    msg_value_none = "The value of this param '{}' is 'None' because is empty" \
                     " so the default value = {}".format(param, default_value)
    return msg_value_none


def message_param(param, value):
    """
    Display the value of param

    :param param: Name of parameter
    :type param: str
    :param value: Value of parameter
    :type value: str, bool
    :return: The massage
    :rtype: str
    """
    msg_param = 'The parameter {:<30} = {}'.format(param, value)
    return msg_param
