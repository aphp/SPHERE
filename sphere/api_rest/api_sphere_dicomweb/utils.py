""" The functions utils of Api rest """
from io import BytesIO
from xml.dom import getDOMImplementation
from sphere.settings import API_DECOMPRESS_PIXELS
import pydicom

from sphere.logs.logs import LOG_API_DICOMWEB


def dict_to_list(dict_uid):
    """
    Returns the value of a dictionary

    :param dict_uid: The IP
    :type dict_uid: list
    :return: Return list of uid
    :rtype: list
    """
    list_uid = ([list(dic.values())[0] for dic in dict_uid])
    return list_uid


def return_list_uid(result):
    """
    Returns list uid

    :param result: The uid
    :type result: list
    :return: Return list of uid
    :rtype: list
    """
    list_uid = [lis[0] for lis in result]
    return list_uid


def metadata_dicom(dicom_path):
    """
    Returns metadata of dicom

    :param dicom_path: The path of a dicom file
    :type dicom_path: str
    :return: Return dict
    :rtype: dict py:class:`Dataset` representation based on the DICOM JSON Model
    """
    dsdcm = pydicom.dcmread(dicom_path, stop_before_pixels=True)
    data_json = dsdcm.to_json_dict()
    return data_json


def add_dicom_part(file_path, body):
    """
    Add application/dicom part to multipart/related

    :param file_path: The path to the dicom file
    :type file_path: str
    :param body: dicom is aggregated to this body
    :type body: bytes
    :return: the aggregated body of dicom files
    :rtype: bytes
    """
    mime_boundary = b'DICOM DATA BOUNDARY'
    part_content_type = b'Content-Type: application/dicom'
    dataset = pydicom.dcmread(file_path, stop_before_pixels=False)
    with BytesIO() as bcontent:
        pydicom.dcmwrite(bcontent, dataset)
        encoded_ds = bcontent.getvalue()
    if body is None:
        body = b''

    CRLF = b'\r\n'
    SEP = b'--'
    body += SEP + mime_boundary + CRLF + part_content_type \
            + CRLF + CRLF + encoded_ds + CRLF + SEP \
            + mime_boundary + SEP + CRLF
    return body


def add_frame_part(frame, body):
    """
    Add application/octet-stream part to multipart/related

    :param frame: The path
    :type frame: byte
    :param body: Dicom is aggregated to this body
    :type body: dataset
    :return: The aggregated body of frames
    :rtype: str
    """
    mime_boundary = b'DICOM FRAME BOUNDARY'
    part_mime_version = b'MIME-Version: 1.0'

    part_content_type = b'Content-Type: application/octet-stream; transfer-syntax=1.2.840.10008.1.2.1' \
                            if API_DECOMPRESS_PIXELS \
                            else b'Content-Type: application/octet-stream'

    part_content_length = b'Content-Length: ' + str(len(frame)).encode('ascii')

    
    if body is None:
        body = b''

    CRLF = b'\r\n'
    SEP = b'--'
    body += SEP + \
            mime_boundary + \
            CRLF + \
            part_content_type + \
            CRLF + \
            part_content_length + \
            CRLF + \
            part_mime_version + \
            CRLF + \
            CRLF + \
            frame + \
            CRLF + \
            SEP + \
            mime_boundary + \
            SEP + \
            CRLF
    return body


def parse_parameters(request_params):
    """
    Retrieve static parameters: limit, offset, includefield and dynamic filters

    :param request_params: the parameters of http request
    :type request_params: :py:class:`django.http.request.QueryDict`
    :return: The tuple  offset, limit, filters, includefield
    :rtype: tuple
    """
    # <QueryDict: {'limit': ['25'], 'offset': ['0'], 'fuzzymatching': ['true'], 'includefield': ['00081030,00080060']}>
    offset, limit, includefield, fuzzymatching = (0, 100, "all", "false")
    static_params = ['limit', 'offset', 'fuzzymatching', 'includefield']

    # fuzzymatching
    if "fuzzymatching" in request_params:
        try:
            fuzzymatching = request_params['fuzzymatching']
        except Exception as exc:
            LOG_API_DICOMWEB.exception(exc)

    # includefield
    if "includefield" in request_params:
        try:
            includefield = request_params['includefield']
        except Exception as exc:
            LOG_API_DICOMWEB.exception(exc)
    # limit
    if "limit" in request_params:
        try:
            limit = int(request_params['limit'])
        except Exception as exc:
            LOG_API_DICOMWEB.exception(exc)
    # offset
    if "offset" in request_params:
        try:
            offset = int(request_params['offset'])
        except Exception as exc:
            LOG_API_DICOMWEB.exception(exc)

    filters = {}
    for k in request_params:
        if k in static_params:
            continue
        filters[k] = request_params[k]
    LOG_API_DICOMWEB.info(" All parameters: limit = %s, offset = %s, "
                          "includefield = %s, filters = %s", limit, offset,
                          includefield, filters)
    return offset, limit, filters, includefield


TAG_NAME = {

}


def get_tag_name(tag_name):
    """
    Convert json attribute name to xml tag name

    :param tag_name: the name of json attribute
    :type tag_name: str
    :return: the xml tag name
    :rtype string
    """
    if tag_name in TAG_NAME:
        return TAG_NAME[tag_name]
    return tag_name.replace('_', '-')


def get_child_tag_name(tag_name):
    """
    In case of a tuple/array, Given the parent tag name, gives the child tag name

    :param tag_name: The tag name
    :type tag_name: str
    :return: the child tag name
    :rtype string
    """
    if tag_name[0:5] == 'list-':
        return tag_name[5:]
    return tag_name[0:-1]


def convert_to_xml(json_obj, tag_name):
    """
    Converts a json object to an xml entity

    :param json_obj: The json object
    :type json_obj: dict
    :param tag_name: The parent tag name
    :type tag_name: str
    :return: an xml string
    :rtype string
    """
    impl = getDOMImplementation()
    tag_name = get_tag_name(tag_name)
    doc = impl.createDocument(None, tag_name, None)
    node = doc.documentElement
    inner_convert_to_xml(json_obj, node, doc)
    return doc.documentElement.toprettyxml()


def inner_convert_to_xml(json_obj, parent, doc):
    """
    recursive function to convert dict to an xml

    :param json_obj: the dictionary to convert to xml
    :type json_obj: dict
    :param parent: the parent document node
    :type parent: dom node
    :param doc: the whole dom document
    :type doc: dom document
    :return: None
    """
    if isinstance(json_obj, (int, float, str)):
        txt = doc.createTextNode(str(json_obj))
        parent.appendChild(txt)
    elif isinstance(json_obj, list):
        tag_name = parent.localName
        child_tag_name = get_child_tag_name(tag_name)
        for obj in json_obj:
            child = doc.createElement(child_tag_name)
            parent.appendChild(child)
            inner_convert_to_xml(obj, child, doc)
    elif isinstance(json_obj, dict):
        for key in json_obj:
            ktag = get_tag_name(key)
            value = json_obj[key]
            child = doc.createElement(ktag)
            parent.appendChild(child)
            inner_convert_to_xml(value, child, doc)


def filter_dataset(fds, list_tags):
    """
    Create a dataset of tags in list_tags

    :param fds: The dataset
    :type fds: :py:class:`pydicom.dataset.Dataset`
    :param list_tags: List of tags. Example og tag: (0x0008, 0x0005)
    :type list_tags: list
    :return: Return the dataset with tags in list_tags
    :rtype: :py:class:`pydicom.dataset.Dataset`
    """
    ds_res = pydicom.Dataset()
    for tag in list_tags:
        try:
            ds_res.add(fds[tag])
        except KeyError:
            pass
    return ds_res


def get_group_element_number(tag):
    """
    Return tuple of group_number and element_number

    :param tag: The tag dicom
    :type tag: str
    :return: Return group number and element number
    :rtype: tuple
    """
    group_number = tag[:4]
    element_number = tag[4:]

    return group_number, element_number
