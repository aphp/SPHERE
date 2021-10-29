import time

from sphere.utilities import msg


def test_execution_time():
    """ Test the function message_bool."""
    start_time = time.time()
    time.sleep(2)
    assert msg.execution_time(start_time) == "Execution time : 00:00:02"


def test_message_bool():
    """ Test the function message_bool."""
    assert msg.message_bool("name_param", "ON", "True") == \
           "This value 'ON' is invalid, here is the list of values ​that we " \
      "can accept : \n [True, 'yes', 'true', 't', 'y', '1', False, 'no', " \
      "'false', 'f', 'n', '0']. The default value name_param = True "


def test_message_critical():
    """ Test the function message_bool."""
    assert msg.message_critical("name_param", str) == \
           "Server has been killed because value for 'name_param' " \
           "parameter must be defined in setting file ."

    assert msg.message_critical("name_param", int) == \
           "Server has been killed because value for 'name_param' " \
           "parameter must be defined in setting file (must be integer)."

    assert msg.message_critical("name_param", bool) == \
           "Server has been killed because value for 'name_param' " \
           "parameter must be defined in setting file (must be boolean)."


def test_message_int():
    """ Test the function message_int."""
    assert msg.message_int("name_param", "value_param") == \
           "Only numbers accepted. The default value name_param = value_param"


def test_message_key_error():
    """ Test the function message_key_error."""
    tab = '\t' * 16
    assert msg.message_key_error("name_param", "value_param") == \
           "The '{0}' parameter does not exists in settings file. " \
           "\n {2} The default value = {1} ".format(
               "name_param", "value_param", tab)


def test_message_param():
    """ Test the function message_param."""
    assert msg.message_param("param", "value") == \
           'The parameter {:<30} = {}'.format("param", "value")


def test_message_value_none():
    """ Test the function message_value_none."""
    assert msg.message_value_none("param", "default_value") == \
           "The value of this param '{}' is 'None' because is empty" \
           " so the default value = {}".format("param", "default_value")


def test_term_bold():
    """ Test the function term_bold."""
    assert msg.term_bold('Test') == '\033[01m{}\033[0m'.format(str("Test"))


def test_term_green():
    """ Test the function term_green."""
    assert msg.term_green('ON') == '\033[92m{}\033[0m'.format(str("ON"))


def test_term_red():
    """ Test the function term_red."""
    assert msg.term_red('OFF') == '\033[91m{}\033[0m'.format(str('OFF'))
