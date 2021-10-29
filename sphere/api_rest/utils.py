import socket

from sphere import settings


def check_api_connect():
    """check if API and connect"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((settings.IP_API, settings.PORT_API))
    return result

    # if result == 0:
    #     print("server is open")
    # else:
    #     print("server is not open")


def check_pid(pid):
    """
        Check For the existence of a unix pid.

        :param pid: The pid
        :type pid: str
        :return: False if except is OSError, else True
        :rtype: bool
    """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

