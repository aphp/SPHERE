import os
# import logging

from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import exceptions
from django.utils.translation import ugettext as _

from sphere.api_rest.api_annotation.inserter_file import FileInstance
from sphere.logs.logs import LOG_API_ANNOTATION


class SaveAnnotationView(APIView):
    """
    A view that can accept POST requests with JSON content.
    """
    parser_classes = [JSONParser]
    # 1.2.840.113619.2.25.22006.190.4.1161185374
    example_series = {
        "file_path": "/home/oac/Bureau/test_annotation",
        "uid": "1.3.46.670589.11.19159.5.0.14016.2008101309225540006",
        "level": "series"
    }
    example_series_not_exits = {
        "file_path": "/home/oac/Bureau/test_annotation",
        "uid": "1.2.840.113619.2.134.1762530585.2556.1161149296.9999",
        "level": "series"
    }
    example_instance = {
        "file_path": "/home/oac/Bureau/test_annotation",
        "uid": "1.2.840.113619.2.25.22006.190.4.1161185374",
        "level": "instance"
    }
    example_instence_not_exits = {
        "file_path": "/home/oac/Bureau/test_annotation",
        "uid": "1.2.124.113532.10.160.160.59.20111004.93208.3593882",
        "level": "instance"
    }

    @staticmethod
    def post(request):
        # print(request.data['file'])
        data = request.data
        # Check whether the data in dictionary format or not

        if not isinstance(data, dict):
            msg_dic = {
                'detail': _("The data must be in dictionary format "),
                'example data': _(
                    """{
                        "level": "instance",
                        "uid": "1.2.124.113532.10.160.160.59.20111004.93208.3593882",
                        "file_path": "/home/oac/Bureau/test_annotation"
                        }""")

            }
            LOG_API_ANNOTATION.error(msg_dic)
            raise exceptions.ValidationError(msg_dic)

        if isinstance(data, dict):
            level = data.get('level')
            uid = data.get('uid')
            file_path = data.get('file_path')

            # CHECK KEY
            # Check if the key 'level' already exists in a dictionary or not
            if 'level' not in data:
                msg = "The key 'level' does not exist in a dictionary"
                LOG_API_ANNOTATION.critical(msg)
                raise exceptions.ValidationError({'detail': _(msg)})

            # Check if the key 'uid' already exists in a dictionary or not
            if 'uid' not in data:
                msg = "The key 'uid' does not exist in a dictionary"
                LOG_API_ANNOTATION.critical(msg)
                raise exceptions.ValidationError({'detail': _(msg)})
            # Check if the key 'file_path' already exists in a dictionary or not
            if 'file_path' not in data:
                msg = "The key 'file_path' does not exist in a dictionary"
                LOG_API_ANNOTATION.critical(msg)
                raise exceptions.ValidationError({'detail': _(msg)})

            # CHECK VALUE
            if not level:
                msg = "The value of the key 'level' is empty"
                LOG_API_ANNOTATION.critical(msg)
                raise exceptions.ValidationError({'detail': _(msg)})
            if not uid:
                msg = "The value of the key 'uid' is empty"
                LOG_API_ANNOTATION.critical(msg)
                raise exceptions.ValidationError({'detail': _(msg)})
            if not file_path:
                msg = "The value of the key 'file_path' is empty"
                LOG_API_ANNOTATION.critical(msg)
                raise exceptions.ValidationError({'detail': _(msg)})

            # CHECK VALUE
            if level.upper() not in ["INSTANCE", "SERIES"]:  # check level
                # level must be equal to INSTANCE or SERIES
                msg = "level must be equal to INSTANCE or SERIES"
                LOG_API_ANNOTATION.critical(msg)
                raise exceptions.ValidationError({'level': _(msg)})
            if not os.path.basename(file_path):
                msg = "Not a file in this path '{}'".format(file_path)
                LOG_API_ANNOTATION.critical(msg)
                raise exceptions.ValidationError({'detail': _(msg)})
            # check if it is a file or not
            if not os.path.isfile(file_path) and os.path.isdir(file_path):
                msg = "This file '{}' is not a file".format(os.path.basename(file_path))
                LOG_API_ANNOTATION.critical(msg)
                raise exceptions.ValidationError({'detail': _(msg)})
            # check whether the file exists or not
            if not os.path.exists(file_path):
                msg = "The path '{}' does not exist".format(file_path)
                LOG_API_ANNOTATION.critical(msg)
                raise exceptions.ValidationError({'detail': _(msg)})
                # the file does not exist

            LOG_API_ANNOTATION.info("received data: %s", data)
            file_instance = FileInstance()
            file_instance.insert_annotation(data)
            return Response({'received data': data})
