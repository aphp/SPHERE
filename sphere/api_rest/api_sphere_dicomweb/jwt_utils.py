# Built-in/Generic Imports
import re

# Libs
from django.http import HttpResponse
import requests

# Own modules
from sphere.settings import API_JWT_VALIDATION, API_JWT_VALIDATION_URL

bearer_regex = re.compile(r'^Bearer\s(.*)$')


def validate(token):
    if API_JWT_VALIDATION is True:
        res = requests.post(API_JWT_VALIDATION_URL, data={'token': token})
        if res.status_code != 200:
            return res.status_code, res.headers['content-type'], res.text
    return 200, '', ''


def validate_jwt_token(func):
    def helper(*args, **eargs):
        if API_JWT_VALIDATION is True:
            request = args[0]
            try:
                auth_header = request.META['HTTP_AUTHORIZATION']
                match = bearer_regex.search(auth_header)
                if match is not None:
                    access_token = match.group(1)
                    (status, content_type, content) = validate(access_token)
                    if status == 200:
                        print("la validation du token est effectuée")
                        ret = func(*args, **eargs)
                        return ret
                    else:
                        return HttpResponse(content, content_type, status)
                else:
                    return HttpResponse("No access token found in Authorization header", 'text/plain', 403)

            except KeyError as ke:
                return HttpResponse("L'entête Authorization est inexistante", "text/plain", 403)

        else:
            ret = func(*args, **eargs)
            return ret

    return helper
