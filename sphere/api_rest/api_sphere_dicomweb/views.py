#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
List views of DicomWeb
"""

# Libs
from rest_framework.views import APIView
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework import status
from django.http import HttpResponse
from django.db.utils import OperationalError
from drf_yasg.utils import swagger_auto_schema

# Own modules
from sphere.api_rest.api_sphere_dicomweb.dicomweb_services.search_qido_rs \
    import SearchOrmSqlalchemy
from sphere.api_rest.api_sphere_dicomweb.dicomweb_services.retrieve_wado_rs \
    import RetrieveOrmSqlalchemy
from sphere.api_rest.api_sphere_dicomweb.utils import \
    add_dicom_part, add_frame_part, parse_parameters, convert_to_xml
from sphere.api_rest.api_sphere_dicomweb.swagger_utils import RESPONSES1, \
    RESPONSES2, RESPONSES3, INSTANCES_PARAMETERS, SERIES_PARAMETERS, \
    STUDY_PARAMETERS
from sphere.api_rest.api_sphere_dicomweb.renderers import DicomJsonRenderer, \
    MultiPartDicomRelatedRenderer,  MultiPartOctetStreamRelatedRenderer, ALLRenderer
from sphere.api_rest.api_sphere_dicomweb.response import DicomJsonResponse
from sphere.api_rest.api_sphere_dicomweb.jwt_utils import validate_jwt_token
from sphere.logs.logs import LOG_API_DICOMWEB
from sphere.api_rest.api_sphere_dicomweb.utils import metadata_dicom
from sphere.dicmeta.database_pacs import DatabasePACS


db_pacs = DatabasePACS()
session = db_pacs.create_session()



def format_http_response(accepted_media_type, content, xml_root=None):
    """
    Format http response into json or xml

    :param accepted_media_type: The accepted media type
    :type accepted_media_type: str

        The possible value:
                - ``application/dicom+json``
                - ``application/dicom+xml``
    :param content: the object to render
    :type content: dict or list
    :param xml_root: the root tag name
    :type xml_root: str
    :return: the HTTP response (json or xml)
    :rtype:
    """
    LOG_API_DICOMWEB.info("accepted_media_type =  %s", accepted_media_type)
    if 'application/dicom+json' == accepted_media_type:
        if isinstance(content, dict):
            return DicomJsonResponse(content)
        else:
            return DicomJsonResponse(content, safe=False)
    elif 'application/dicom+xml' == accepted_media_type:
        str_xml = ''
        if len(content) > 1 and xml_root:
            str_xml = convert_to_xml(content, xml_root)
        elif len(content) == 1:
            key = None
            for key in content:
                pass
            if xml_root:
                str_xml = convert_to_xml(content[key], xml_root)
            else:
                str_xml = convert_to_xml(content[key], key)
        return HttpResponse(str_xml, accepted_media_type, 200)
    else:
        # return 406 status code
        msg = "No accept media_type: equal <b style='color:red;'>'{} </b>'" \
              ", I accept <b style='color:green;'>'application/dicom+json'" \
              "</b>'".format(accepted_media_type)
        LOG_API_DICOMWEB.error("Media_type = '%s', we accept that"
                               "'application/dicom+json'", accepted_media_type)
        return HttpResponse(msg, status=status.HTTP_406_NOT_ACCEPTABLE)


# ======= Instance ====== #
# Link: /qidors/instances
class AllInstancesView(APIView):
    """
    Return list of instance metadata
        list of tags that can be returned with the metadata of instance:
            `SOP Class UID` ==============> `(0008,0016)`
            `SOP Instance UID` ===========> `(0008,0018)`
            `Instance Availability` ======> `(0008,0056)`
            `Timezone Offset From UTC` ===> `(0008,0201)`
            `Retrieve URL` ===============> `(0008,1190)`
            `Instance Number` ============> `(0020,0013)`
            `Rows` =======================> `(0028,0010)`
            `Columns` ====================> `(0028,0011)`
            `Bits Allocated` =============> `(0028,0100)`
            `Number of Frames` ===========> `(0028,0008)`
    """
    renderer_classes = [DicomJsonRenderer, ALLRenderer]

    def __init__(self):
        APIView.__init__(self)

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=INSTANCES_PARAMETERS, responses=RESPONSES1
    )
    @validate_jwt_token
    def get(request):
        """
        get method to search for instances uid

        :param request: The Request object
        :type request: :py:class:`rest_framework.request.Request`
        :return: List of object metadata
        :rtype: :py:class:`django.http.response.JsonResponse`,
                :py:class:`django.http.response.HttpResponse` or ...
        """
        LOG_API_DICOMWEB.info("link: /qidors/instances")
        offset, limit, filters, includefield = parse_parameters(request.query_params)
        search_orm_sqlalchemy = SearchOrmSqlalchemy(session)
        instance_metadata_list = search_orm_sqlalchemy.all_instances(
            offset, limit, filters, includefield)
        return format_http_response(request.accepted_media_type,
                                    instance_metadata_list,
                                    xml_root='list_instance_uid')


# Link: /qidors/studies/{StudyInstanceUID}/instances
class AllInstancesOfStudyView(APIView):
    """
    Return list of instance metadata
    list of tags that can be returned with the metadata of instance:
        `SOP Class UID` ==============> `(0008,0016)`
        `SOP Instance UID` ===========> `(0008,0018)`
        `Instance Availability` ======> `(0008,0056)`
        `Timezone Offset From UTC` ===> `(0008,0201)`
        `Retrieve URL` ===============> `(0008,1190)`
        `Instance Number` ============> `(0020,0013)`
        `Rows` =======================> `(0028,0010)`
        `Columns` ====================> `(0028,0011)`
        `Bits Allocated` =============> `(0028,0100)`
        `Number of Frames` ===========> `(0028,0008)`
    """
    renderer_classes = [DicomJsonRenderer, ALLRenderer]

    def __init__(self):
        APIView.__init__(self)

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=INSTANCES_PARAMETERS, responses=RESPONSES1
    )
    @validate_jwt_token
    def get(request, study_uid):
        """
        get method to search for instances uid of a study

        :param request: The Request object
        :type request: :py:class:`rest_framework.request.Request`
        :param study_uid: study uid
        :type study_uid: str
        :return: List of metadata
        :rtype: :py:class:`django.http.response.JsonResponse`,
                :py:class:`django.http.response.HttpResponse` or ...
        """
        LOG_API_DICOMWEB.info(
            "link: /qidors/studies/{StudyInstanceUID}/instances")
        offset, limit, filters, includefield = parse_parameters(
            request.query_params)
        search_orm_sqlalchemy = SearchOrmSqlalchemy(session)
        instance_metadata_list = search_orm_sqlalchemy.all_instances_of_one_study(
            study_uid, offset, limit, filters, includefield)
        return format_http_response(request.accepted_media_type,
                                    instance_metadata_list)


# Link: /qidors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/instances
class AllInstancesOfSeriesOfStudyView(APIView):
    """
    Return list of instance metadata
    list of tags that can be returned with the metadata of instance:
        `SOP Class UID` ==============> `(0008,0016)`
        `SOP Instance UID` ===========> `(0008,0018)`
        `Instance Availability` ======> `(0008,0056)`
        `Timezone Offset From UTC` ===> `(0008,0201)`
        `Retrieve URL` ===============> `(0008,1190)`
        `Instance Number` ============> `(0020,0013)`
        `Rows` =======================> `(0028,0010)`
        `Columns` ====================> `(0028,0011)`
        `Bits Allocated` =============> `(0028,0100)`
        `Number of Frames` ===========> `(0028,0008)`
    """
    renderer_classes = [DicomJsonRenderer, ALLRenderer]

    def __init__(self):
        APIView.__init__(self)

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=INSTANCES_PARAMETERS, responses=RESPONSES1
    )
    @validate_jwt_token
    def get(request, study_uid, series_uid):
        """
        get method to search for instances uid

        :param request: The Request object
        :type request: :py:class:`rest_framework.request.Request`
        :param study_uid: Study uid
        :type study_uid: str
        :param series_uid: Series uid
        :type series_uid: str
        :return: list of metadata
        :rtype: :py:class:`django.http.response.JsonResponse`,
                :py:class:`django.http.response.HttpResponse` or ...
        """
        LOG_API_DICOMWEB.info(
            "link: /qidors/studies/{StudyInstanceUID}/series"
            "{SeriesInstanceUID}/instances")
        offset, limit, filters, includefield = parse_parameters(
            request.query_params)
        search_orm_sqlalchemy = SearchOrmSqlalchemy(session)
        instance_metadata_list = search_orm_sqlalchemy.all_instances_of_one_study_and_series(
            study_uid, series_uid, offset, limit, filters, includefield)
        return format_http_response(request.accepted_media_type, instance_metadata_list)


# ======= Series ======== #
# Link: /qidors/series
class AllSeriesView(APIView):
    """
    Return list of all series metadata
        list of tags that can be returned with the metadata of series:
            `Modality` ===============================> `(0008,0060)`
            `Timezone Offset From UTC` ===============> `(0008,0201)`
            `Series Description` ====================> `(0008,103E)`
            `Retrieve URL` ==========================> `(0008,1190)`
            `Series Instance UID` ===================> `(0020,000E)`
            `Series Number` =========================> `(0020,0011)`
            `Number of Series Related Instances` ====> `(0020,1209)`
            `Performed Procedure Step Start Date` ===> `(0040,0244)`
            `Performed Procedure Step Start Time` ===> `(0040,0245)`
            `Request Attributes Sequence` ===========> `(0040,0275)`
            `>Scheduled Procedure Step ID` ==========> `(0040,0009)`
            `>Requested Procedure ID` ===============> `(0040,1001)`
    """
    renderer_classes = [DicomJsonRenderer, ALLRenderer]

    def __init__(self):
        APIView.__init__(self)

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=SERIES_PARAMETERS, responses=RESPONSES1
    )
    @validate_jwt_token
    def get(request):
        """
        get method to search for series uid

        :param request: The Request object
        :type request: :py:class:`rest_framework.request.Request`
        :return: list of metadata
        :rtype: :py:class:`django.http.response.JsonResponse`,
                :py:class:`django.http.response.HttpResponse` or ...
        """
        LOG_API_DICOMWEB.info("link: /qidors/series")
        offset, limit, filters, includefield = parse_parameters(
            request.query_params)
        search_orm_sqlalchemy = SearchOrmSqlalchemy(session)
        series_metadata_list = search_orm_sqlalchemy.all_series(
            offset, limit, filters, includefield)
        return format_http_response(request.accepted_media_type, series_metadata_list)


# Link: /qidors/studies/{StudyInstanceUID}/series
class AllSeriesOfStudyView(APIView):
    """
    Return list of study metadata
        list of tags that can be returned with the metadata of series:
            `Modality` ===============================> `(0008,0060)`
            `Timezone Offset From UTC` ===============> `(0008,0201)`
            `Series Description` ====================> `(0008,103E)`
            `Retrieve URL` ==========================> `(0008,1190)`
            `Series Instance UID` ===================> `(0020,000E)`
            `Series Number` =========================> `(0020,0011)`
            `Number of Series Related Instances` ====> `(0020,1209)`
            `Performed Procedure Step Start Date` ===> `(0040,0244)`
            `Performed Procedure Step Start Time` ===> `(0040,0245)`
            `Request Attributes Sequence` ===========> `(0040,0275)`
            `>Scheduled Procedure Step ID` ==========> `(0040,0009)`
            `>Requested Procedure ID` ===============> `(0040,1001)`
    """
    renderer_classes = [DicomJsonRenderer, ALLRenderer]

    def __init__(self):
        APIView.__init__(self)

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=SERIES_PARAMETERS, responses=RESPONSES1
    )
    @validate_jwt_token
    def get(request, study_uid):
        """
        get method to search for series

        :param request: The Request object
        :type request: :py:class:`rest_framework.request.Request`
        :param study_uid: The study uid
        :type study_uid: str
        :return: list of metadata
        :rtype: :py:class:`django.http.response.JsonResponse`,
                :py:class:`django.http.response.HttpResponse` or ...
        """
        LOG_API_DICOMWEB.info(
            "link: /qidors/studies/{StudyInstanceUID}/series")
        offset, limit, filters, includefield = parse_parameters(
            request.query_params)
        search_orm_sqlalchemy = SearchOrmSqlalchemy(session)
        series_metadata_list = search_orm_sqlalchemy.all_series_of_one_study(
            study_uid, offset, limit, filters, includefield)
        return format_http_response(request.accepted_media_type, series_metadata_list)


# ======= Studies ======= #
# Link: /qidors/studies
class AllStudiesView(APIView):
    """
    Return list of study metadata
        list of tags that can be returned with the metadata of studies:
                `Study Date` ==========================> `(0008,0020)`
                `Study Time` ==========================> `(0008,0030)`
                `Accession Number` ====================> `(0008,0050)`
                `Instance Availability` ===============> `(0008,0056)`
                `Modalities in Study` =================> `(0008,0061)`
                `Referring Physician's Name` ==========> `(0008,0090)`
                `Timezone Offset From UTC` ============> `(0008,0201)`
                `Retrieve URL` ========================> `(0008,1190)`
                `Patient's Name` ======================> `(0010,0010)`
                `Patient ID` ==========================> `(0010,0020)`
                `Patient's Birth Date` ================> `(0010,0030)`
                `Patient's Sex` =======================> `(0010,0040)`
                `Study Instance UID` ==================> `(0020,000D)`
                `Study ID` ============================> `(0020,000D)`
                `Number of Study Related Series` ======> `(0020,1206)`
                `Number of Study Related Instances` ===> `(0020,1208)`
    """
    renderer_classes = [DicomJsonRenderer, ALLRenderer]

    def __init__(self):
        APIView.__init__(self)

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=STUDY_PARAMETERS, responses=RESPONSES1
    )
    @validate_jwt_token
    def get(request):
        """
        get method to search for all studies

        :param request: The Request object
        :type request: :py:class:`rest_framework.request.Request`
        :return: list of metadata
        :rtype: :py:class:`django.http.response.JsonResponse`,
                :py:class:`django.http.response.HttpResponse` or ...
        """
        LOG_API_DICOMWEB.info("link: /qidors/studies")
        offset, limit, filters, includefield = parse_parameters(
            request.query_params)
        s_orm = SearchOrmSqlalchemy(session)
        study_metadata_list = s_orm.all_studies(offset, limit, filters, includefield)
        return format_http_response(request.accepted_media_type, study_metadata_list)


###########################
# ==== Retrieve WADO ==== #
###########################

# Link: /wadors/studies/{StudyInstanceUID}/metadata
class MetadataStudyView(APIView):
    """
    Return the metadata list of all instances linked to study_uid except pixels
    """
    renderer_classes = [DicomJsonRenderer, ALLRenderer]

    def __init__(self):
        APIView.__init__(self)

    @staticmethod
    @swagger_auto_schema(responses=RESPONSES2)
    @validate_jwt_token
    def get(request, study_uid):
        """
        get method to retrieve metadata

        :param request: The Request object
        :type request: :py:class:`rest_framework.request.Request`
        :param study_uid: The study uid
        :return: dicom metadata
        """
        LOG_API_DICOMWEB.info(
            "link: /wadors/studies/{StudyInstanceUID}/metadata")
        try:
            list_metadata_study = []
            retrieve_orm_sqlalchemy = RetrieveOrmSqlalchemy(session)
            for file_path in retrieve_orm_sqlalchemy.list_paths_dicom(study_uid):
                list_metadata_study.append(metadata_dicom(file_path))
            return format_http_response(request.accepted_media_type, list_metadata_study)
        except OperationalError:
            return HttpResponse("Erreur d'accès à la base de données", "text/plain", 500)


# Link: /wadors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/metadata
class MetadataSeriesView(APIView):
    """
    Return the metadata list of all instances linked to study_uid and series_uid except pixels
    """
    renderer_classes = [DicomJsonRenderer, ALLRenderer]

    def __init__(self):
        APIView.__init__(self)

    @staticmethod
    @swagger_auto_schema(responses=RESPONSES1)
    @validate_jwt_token
    def get(request, study_uid, series_uid):
        """
        get method to retrieve metadata

        :param request: The Request object
        :type request: :py:class:`rest_framework.request.Request`
        :param study_uid: The study uid
        :type study_uid: str
        :param series_uid: The series uid
        :type series_uid: str
        :return: metadata
        """
        LOG_API_DICOMWEB.info(
            "link: /wadors/studies/{StudyInstanceUID}/series/"
            "{SeriesInstanceUID}/metadata")
        try:
            list_metadata_series = []
            retrieve_orm_sqlalchemy = RetrieveOrmSqlalchemy(session)
            for file_path in retrieve_orm_sqlalchemy.list_paths_dicom(
                    study_uid, series_uid):
                list_metadata_series.append(metadata_dicom(file_path))

            return format_http_response(request.accepted_media_type, list_metadata_series)
        except OperationalError:
            return HttpResponse("Erreur d'accès à la base de données", "text/plain", 500)


# Link: /wadors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/instances/{SOPInstanceUID}/metadata
class MetadataInstanceView(APIView):
    """
    Return the metadata if one instance except pixels
    """
    renderer_classes = [DicomJsonRenderer, ALLRenderer]

    def __init__(self):
        APIView.__init__(self)

    @staticmethod
    @swagger_auto_schema(responses=RESPONSES2)
    @validate_jwt_token
    def get(request, study_uid, series_uid, instance_uid):
        """
        get method to retrieve metadata

        :param request: The Request object
        :type request: :py:class:`rest_framework.request.Request`
        :param study_uid: The study uid
        :type study_uid: str
        :param series_uid: The series uid
        :type series_uid: str
        :param instance_uid: The instance uid
        :type instance_uid: str
        :return: dicom metadata
        """
        LOG_API_DICOMWEB.info(
            "link: /wadors/studies/{StudyInstanceUID}/series/"
            "{SeriesInstanceUID}/instances/{SOPInstanceUID}/metadata")
        try:
            retrieve_orm_sqlalchemy = RetrieveOrmSqlalchemy(session)
            dict_metadata_instance = metadata_dicom(
                retrieve_orm_sqlalchemy.list_paths_dicom(
                    study_uid, series_uid, instance_uid)[0])
            return format_http_response(request.accepted_media_type, dict_metadata_instance)
        except OperationalError:
            return HttpResponse("Erreur d'accès à la base de données", "text/plain", 500)


# Link: /wadors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/instances/{SOPInstanceUID}/frames/{frame}
class InstanceFrameView(APIView):
    """
    Return the data pixels of one frame
    """
    renderer_classes = [MultiPartOctetStreamRelatedRenderer, StaticHTMLRenderer]

    def __init__(self):
        APIView.__init__(self)

    @staticmethod
    @validate_jwt_token
    def get(request, study_uid, series_uid, instance_uid, frame):
        """
         Get method

        :param request: The Request object
        :type request: :py:class:`rest_framework.request.Request`
        :param study_uid: The study uid
        :type study_uid: str
        :param series_uid: Series uid
        :type series_uid: str
        :param instance_uid: Instance uid
        :type instance_uid: str
        :param frame: frame uid
        :type frame: str
        :return:
        :rtype:
        """
        LOG_API_DICOMWEB.info(
            "link: /wadors/studies/{StudyInstanceUID}/series/"
            "{SeriesInstanceUID}/instances/{SOPInstanceUID}"
            "frames/{frame}")
        LOG_API_DICOMWEB.info("study_uid: %s, series_uid: %s, "
                              "instance_uid: %s, frame: %s", study_uid,
                              series_uid, instance_uid, frame)
        retrieve_orm_sqlalchemy = RetrieveOrmSqlalchemy(session)
        bframe = retrieve_orm_sqlalchemy.frame_of_instance(instance_uid, frame)
        # multipart_content_type = 'multipart/related; boundary=\
        #             "FRAME DATA BOUNDARY"; type="application/octet-stream"'
        multipart_content_type = 'multipart/related; \
            type="application/octet-stream; \
            transfer-syntax=1.2.840.10008.1.2.1"; \
            boundary="FRAME DATA BOUNDARY"'
                    
        body = b''
        body = add_frame_part(bframe, body)
        response = HttpResponse(body, multipart_content_type)
        return response


# Link: /wadors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/instances/{SOPInstanceUID}
class DCMInstanceView(APIView):
    """
    Return the metadata and data pixels of one instance
    """
    renderer_classes = [MultiPartDicomRelatedRenderer]

    def __init__(self):
        APIView.__init__(self)

    @staticmethod
    @swagger_auto_schema(responses=RESPONSES3)
    @validate_jwt_token
    def get(request, study_uid, series_uid, instance_uid):
        """
        Get method to retrieve an instance of dicom

        :param request: The Request object
        :type request: :py:class:`rest_framework.request.Request`
        :param study_uid: The study uid
        :type study_uid: str
        :param series_uid: Series uid
        :type series_uid: str
        :param instance_uid: Instance uid
        :type instance_uid: str
        :return:
        :rtype:
        """
        LOG_API_DICOMWEB.info(
            "link: /wadors/studies/{StudyInstanceUID}/series/"
            "{SeriesInstanceUID}/instances/{SOPInstanceUID}")
        try:
            retrieve_orm_sqlalchemy = RetrieveOrmSqlalchemy(session)
            list_file_path = retrieve_orm_sqlalchemy.list_paths_dicom(
                study_uid, series_uid, instance_uid)
            multipart_content_type = 'multipart/related; boundary=\
            "DICOM DATA BOUNDARY"; type="application/dicom"'
            body = b''
            for filename in list_file_path:
                body = add_dicom_part(filename, body)
            if len(list_file_path) != 0:
                response = HttpResponse(body, multipart_content_type)
            else:
                response = HttpResponse('message: No dicom instance found', "application/text", 404)
            return response
        except OperationalError:
            return HttpResponse("Error: d'accès à la base de données", "text/plain", 500)


# Link: /wadors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID}
class DCMInstancesOfSeriesView(APIView):
    """
    Return the metadata and data pixels of all instances linked to study_uid and series_uid
    """
    renderer_classes = [MultiPartDicomRelatedRenderer, StaticHTMLRenderer]

    def __init__(self):
        APIView.__init__(self)

    @staticmethod
    @swagger_auto_schema(responses=RESPONSES3)
    @validate_jwt_token
    def get(request, study_uid, series_uid):
        """
        Get method to retrieve DICOM instances from series/study

        :param request: The Request object
        :type request: :py:class:`rest_framework.request.Request`
        :param study_uid: The study uid
        :type study_uid: str
        :param series_uid: Series uid
        :type series_uid: str
        :return: application/dicom
        :rtype : str
        """
        LOG_API_DICOMWEB.info(
            "link: /wadors/studies/{StudyInstanceUID}/series/"
            "{SeriesInstanceUID}")
        try:
            retrieve_orm_sqlalchemy = RetrieveOrmSqlalchemy(session)
            list_file_path = retrieve_orm_sqlalchemy.list_paths_dicom(
                study_uid, series_uid)

            multipart_content_type = 'multipart/related; boundary=\
            "DICOM DATA BOUNDARY"; type="application/dicom"'
            body = b''
            for filename in list_file_path:
                body = add_dicom_part(filename, body)
            if len(list_file_path) != 0:
                response = HttpResponse(body, multipart_content_type)
            else:
                response = HttpResponse('message: No dicom instance found', "application/text", 404)
            return response
        except OperationalError:
            return HttpResponse("Error d'accès à la base de données", "text/plain", 500)


# Link: /wadors/studies/{StudyInstanceUID}
class DCMInstancesOfSeriesOfStudyView(APIView):
    """
    Return the metadata and data pixels of all instances linked to study_uid
    """
    renderer_classes = [MultiPartDicomRelatedRenderer, StaticHTMLRenderer]

    def __init__(self):
        APIView.__init__(self)

    @staticmethod
    @swagger_auto_schema(responses=RESPONSES3)
    @validate_jwt_token
    def get(request, study_uid):
        """
        get methods to retrieve DICOM instances

        :param request: The Request object
        :type request: :py:class:`rest_framework.request.Request`
        :param study_uid: The study uid
        :type study_uid: str
        :return: application/dicom
        """
        LOG_API_DICOMWEB.info("link: /wadors/studies/{StudyInstanceUID}")
        try:
            retrieve_orm_sqlalchemy = RetrieveOrmSqlalchemy(session)
            list_file_path = retrieve_orm_sqlalchemy.list_paths_dicom(study_uid)
            multipart_content_type = 'multipart/related; boundary=\
            "DICOM DATA BOUNDARY"; type="application/dicom"'
            body = b''

            for filename in list_file_path:
                body = add_dicom_part(filename, body)

            if len(list_file_path) != 0:
                response = HttpResponse(body, multipart_content_type)
            else:
                response = HttpResponse('Message: No dicom instance found', "application/text", 404)
                
            return response
        except OperationalError:
            return HttpResponse("Erreur d'accès à la base de données", "text/plain", 500)
