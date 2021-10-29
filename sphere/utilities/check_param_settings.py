""" Check parameter of settings"""
# pylint: disable=eval-used, no-else-return,
import os
import sys
import logging

from sphere.utilities.string_tools import str2bool
from sphere.utilities.msg import message_bool, message_critical, message_int, \
    message_param, message_key_error, message_value_none


class CheckParamSettings:
    """ Check parameter of settings"""
    def __init__(self, parameter, log):
        """
        Reset the class

        :param parameter: The dictionary of parameters
        :type parameter: dict
        :param log: logger
        :type log: :py:class:`logging.Logger`
        """
        self.dict_param = parameter
        self.log = log

    @staticmethod
    def word_list(string):
        """
        word list separated by a point

        :param string: THe strings
        :type string: str
        :return: Word in square brackets
        :rtype: str
        """
        list_word = string.split('.')
        concat_word = ''
        for word in list_word:
            concat_word = concat_word + "['" + word + "']"
        return concat_word

    @staticmethod
    def create_directory(dir_name, log):
        """
       Create target directory & all intermediate directories if don't exists

       :param dir_name: Directory name
       :type dir_name: str
       :param log: logger
       :type log: :py:class:`logging.Logger`
       """
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            log.info("Directory %s Created ", dir_name)
        else:
            log.info("Directory %s already exists", dir_name)

    def upper_word(self, word):
        """
        Word upper

        :param word: The word
        :type word: str
        :return: The word
        :rtype: str
        """
        try:
            if isinstance(word, str):
                word = word.strip().upper()
            else:
                self.log.error('The value must be of type string')
        except Exception as exc:
            self.log.exception(exc)
        return word

    # pylint: disable=no-else-return
    def check_number(self, key_param, default_value):
        """
        Check the parameters where the value is type int

        :param key_param: The parameters separate by point
        :type key_param: str
        :param default_value: The default number
        :type default_value: int
        :return: The number
        :rtype: str
        """
        try:
            value = eval('self.dict_param' + self.word_list(key_param))
            if value is None:
                self.log.error(message_value_none(key_param, default_value))
                value = default_value
            else:
                if float(value).is_integer():
                    value = int(value)
                else:
                    value = float(value)
            self.log.debug(message_param(key_param, value))
            return value
        except ValueError:
            self.log.error(message_int(key_param, default_value))
            return default_value
        except KeyError:
            self.log.warning(message_key_error(key_param, default_value))
            return default_value
        except Exception as exc:
            self.log.exception(exc)
            self.log.critical(message_critical(key_param, int))
            sys.exit()

    def check_str(self, key_param, default_value):
        """
        Check the parameters where the value is type str

        :param key_param: The parameters separate by point
        :type key_param: str
        :param default_value: The default value
        :type default_value: str or list
        :return: The string
        :rtype: str or list
        """
        try:
            value = eval('self.dict_param' + self.word_list(key_param))
            if value is None:
                self.log.error(message_value_none(key_param, default_value))
                value = default_value

            self.log.debug(message_param(key_param, value))
            return value
        except ValueError:
            self.log.error(message_int(key_param, default_value))
            return default_value
        except KeyError:
            self.log.warning(message_key_error(key_param, default_value))
            return default_value
        except Exception as exc:
            self.log.exception(exc)
            self.log.critical(message_critical(key_param))
            sys.exit()

    def check_bool(self, key_param, default_value):
        """
        Check the parameters where the value is type bool

        :param key_param: The parameters separate by point
        :type key_param: str
        :param default_value: The default value
        :type default_value: bool
        :return: The bool
        :rtype: bool
        """
        try:
            value = eval('self.dict_param' + self.word_list(key_param))
            value = str2bool(value)
            if isinstance(value, bool):
                self.log.debug(message_param(key_param, value))
                return value
            else:
                self.log.warning(message_bool(key_param, value, default_value))
                return default_value
        except KeyError:
            self.log.warning(message_key_error(key_param, default_value))
            return default_value
        except Exception as exc:
            self.log.exception(exc)
            self.log.critical(message_critical(key_param, bool))
            sys.exit()

    def check_path_folder(self, key_param, default_path_folder):
        """
        Check path folder

        :param key_param: The parameters separate by point
        :type key_param: str
        :param default_path_folder: The default path folder
        :type default_path_folder: str
        :return: The path folder
        :rtype: str
        """
        try:
            path_folder = eval('self.dict_param' + self.word_list(key_param))
            # create log folder is not existing
            self.create_directory(path_folder, self.log)
            self.log.debug(message_param(key_param, path_folder))
            return path_folder
        except KeyError:
            self.create_directory(default_path_folder, self.log)
            self.log.warning(message_key_error(key_param, default_path_folder))
            return default_path_folder
        except Exception as exc:
            self.log.exception(exc)
            self.log.critical(message_critical(key_param))
            sys.exit()

    def check_path_file(self, key_param, default_file_name):
        """
        Check path file

        :param key_param: The parameters separate by point
        :type key_param: str
        :param default_file_name: The default file name
        :type default_file_name: str
        :return: The the path file
        :rtype: str
        """
        try:
            file_name = eval('self.dict_param' + self.word_list(key_param))
            self.log.debug(message_param(key_param, file_name))
            return file_name
        except KeyError:
            self.log.warning(message_key_error(key_param, default_file_name))
            return default_file_name
        except Exception as exc:
            self.log.exception(exc)
            self.log.critical(message_critical(key_param))
            sys.exit()

    def check_file_exists(self, key_param):
        """
        Check if the file exists or not

        :param key_param: The parameters separate by point
        :type key_param: str
        :return: The pah file
        :rtype: str
        """
        try:
            path_file = eval('self.dict_param' + self.word_list(key_param))
            if not os.path.exists(path_file):
                self.log.critical("The file '%s' does not exist", key_param)
                sys.exit()
            else:
                self.log.debug(message_param(key_param, path_file))
                return path_file
        except KeyError:
            self.log.critical("The '%s' parameter does not exists in settings "
                              "file. ", key_param)
            sys.exit()
        except Exception as exc:
            self.log.exception(exc)
            self.log.critical(message_critical(key_param))
            sys.exit()

    def check_level_log(self, key_param, default_level, list_level):
        """

        :param key_param: The parameters separate by point
        :type key_param: str
        :param default_level: The default level
        :type default_level: str
        :param list_level: List level
        :type list_level: list
        :return: The level
        :rtype: str
        """
        try:
            level = eval('self.dict_param' + self.word_list(key_param))
            level = self.upper_word(level)
            if level in list_level:
                self.log.debug(message_param(key_param, level))
                log_stream_level = logging.getLevelName(level)
                return log_stream_level
            else:
                self.log.warning(
                    "This value '%s' is unknown, here is the list "
                    "of values ​that we can accept : \n %s. The "
                    "default value %s = %s ",
                    level, list_level, key_param, default_level)
                log_stream_level = logging.getLevelName(default_level)
                return log_stream_level
        except KeyError:
            self.log.warning(message_key_error(key_param, default_level))
            log_stream_level = logging.getLevelName(default_level)
            return log_stream_level
        except Exception as exc:
            self.log.exception(exc)
            self.log.critical(message_critical(key_param))
            sys.exit()

    def check_str_in_list(self, key_param, default_word, list_value):
        """
        Check word if exists in list or not

        :param key_param: The parameters separate by point
        :type key_param: str
        :param default_word: The default word
        :type default_word: str
        :param list_value: List value
        :type list_value: list
        :return: The value
        :rtype: str
        """
        try:
            value = eval('self.dict_param' + self.word_list(key_param))
            value = self.upper_word(value)
            if value not in list_value:
                self.log.warning(
                    " %s not in this list %s; default value "
                    "%s = %s ",
                    value, list_value, key_param, default_word)
                return default_word
            else:
                self.log.debug(message_param(key_param, value))
                return value
        except KeyError:
            self.log.warning(message_key_error(key_param, default_word))
            return default_word
        except Exception as exc:
            self.log.exception(exc)
            self.log.critical(message_critical(key_param, str))
            sys.exit()

    def check_list_from_env(self, env_var, default_value):
        """
        Tries to build a list from comma-separated list specified as an environment variable.

        :param env_var: The environment variable to retrieve as a comma-separated list
        :type env_var: str
        :param default_value: The default list value
        :type default_value: list
        :return The list if the environment variable has been specified, or the default value if not.
        :rtype list
        """

        host_list = os.getenv(env_var)

        if host_list is not None:
            return host_list.split(", ")
        else:
            self.log.warning(
                "No list specified from enviroment variable %s, switching to default value %s",
                env_var, default_value)
            return default_value

    @staticmethod
    def empty_db_param(db_param):
        """
        Empty all param of database.

        :param db_param: The database parameter
        :type db_param: dict
        """
        db_param["ip"] = "I empty them"
        db_param["port"] = "I empty them"
        db_param["database"] = "I empty them"
        db_param["schema"] = "I empty them"
        db_param["login"] = "I empty them"
        db_param["password"] = "I empty them"
        return db_param
