#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Management of swagger DICOM tags filters
"""
# Built-in/Generic Imports
import os
import sys
from drf_yasg import openapi

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Own modules
from sphere.api_rest.api_sphere_dicomweb.metadata_tags_configuration import METADATA_TAGS


def all_parameters():
    """
    Given the METADATA_TAGS, compute swagger fields to add filters on DICOM tags/keyword

    :return: The filters of (instance, series and study), limit, offset and includefield
    :rtype tuple (dict, py:class:`drf_yasg.openapi.Parameter`, ...)
    """
    filters = {}
    for tag, keyword, _, model in METADATA_TAGS:
        if model not in filters:
            filters[model] = []
        filters[model].append(
            openapi.Parameter(keyword, openapi.IN_QUERY,
                              description=keyword + "/" + tag + ' DICOM filter',
                              type=openapi.TYPE_STRING, required=False))

    includefield = openapi.Parameter('includefield',
                                     openapi.IN_QUERY,
                                     description="The tags to return in the "
                                                 "result separated by comma",
                                     type=openapi.TYPE_STRING,
                                     required=False,
                                     default="all")
    limit = openapi.Parameter('limit',
                              openapi.IN_QUERY,
                              description="Limits numbers of results",
                              type=openapi.TYPE_INTEGER,
                              required=False,
                              default=100)
    offset = openapi.Parameter('offset',
                               openapi.IN_QUERY,
                               description="Skips numbers of results",
                               type=openapi.TYPE_INTEGER,
                               required=False,
                               default=0)

    return filters, limit, offset, includefield


FILTERS, LIMIT, OFFSET, INCLUDEFIELD = all_parameters()
OTHER_PARM = [INCLUDEFIELD, LIMIT, OFFSET]

INSTANCES_PARAMETERS = OTHER_PARM + FILTERS['Instance']

SERIES_PARAMETERS = OTHER_PARM + FILTERS['Series']

STUDY_PARAMETERS = OTHER_PARM + FILTERS['Study']

RESPONSES1 = {
    200: "The search completed successfully, and the results are contained in "
         "the payload",
    406: 'The origin server does not support any of the Acceptable Media Types'
}
RESPONSES2 = {
    200: " The response payload contains representations for all of the "
         "Target Resource(s)",
    406: 'The origin server does not support any of the Acceptable Media Types',
    500: 'Internal Server Error'}
RESPONSES3 = {200: "Accept", 404: 'Bad Request', 500: 'Internal Server Error'}
