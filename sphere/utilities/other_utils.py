import requests

from sphere.logs.logs import LOG_CODE_PYTHON


def check_url(url):
    """
    Check url is up or not

    :param url: The url
    :type url: str
    :return: Return True if website_is_up else False
    :rtype: bool
    """
    try:
        request_response = requests.get(url)
        status_code = request_response.status_code
        website_is_up = status_code == 200
        return website_is_up
    except requests.exceptions.ConnectionError:
        LOG_CODE_PYTHON.warning("Connection refused of %s", url)
        return False
    except Exception as exc:
        LOG_CODE_PYTHON.exception(exc)
        return False