""" test functions helper for asserting in tests """
import json
import pydicom

from api_sphere_dicomweb.models import Instance, StorageMetadata
from api_sphere_dicomweb.utils import dict_to_list

# def serialize_db_data(cursor, schema, filename):
#     sql_req = "select study_uid, series_uid, instance_uid from %s.instance;" % (schema)
#     cursor.execute(sql_req)
#     res = cursor.fetchall()
#     index = {}
#     for row in res:
#         #print(row)
#         for i, uid in enumerate(row):
#             add_row(index, row)
#     with open(filename, "w") as fout:
#         fout.write(json.dumps(index, indent=True))


def load_db_data(filename):
    """
    Loads a json object from file
    :param filename: str
    :return: dict
    """
    with open(filename) as fin:
        return json.loads(fin.read())


def add_row(index, row):
    """
    Adds row  (study_uid, series_uid, instance_uid in the index
    :param index: dict
    :param row: list
    :return: None
    """
    (study_uid, series_uid, instance_uid) = row
    if study_uid in index:
        series = index[study_uid]
    else:
        series = {}
        index[study_uid] = series

    if series_uid in series:
        instances = series[series_uid]
    else:
        instances = []
        series[series_uid] = instances
    instances.append(instance_uid)


def compute_test_referentiel(fixture_file):
    """
    Given the fixture file, compute data referentiel for test asserting
    :param fixture_file: str
    :return: tuple of instances_by_study_series, list_all_study, \
    list_all_series, list_all_instances, list_instances_by_study, \
    list_series_by_study
    """
    with open(fixture_file) as ffixture:
        content = ffixture.read()
    fix_obj = json.loads(content)
    instances_by_study_series = {}
    list_all_study = []
    # list_all_study = set()
    list_all_series = set()
    list_all_instances = set()
    list_instances_by_study = {}
    list_series_by_study = {}
    for elem in fix_obj:
        model = elem['model'].split(".")
        if model[0] == 'api_sphere_dicomweb':
            # if model[1] in ['study', 'series', 'instance', 'storagemetadata']:
            if model[1] in ['instance']:
                instance_uid = elem['fields']['instance_uid']
                list_all_instances.add(instance_uid)
                series_uid = elem['fields']['series_uid']
                list_all_series.add(series_uid)
                study_uid = elem['fields']['study_uid']
                if not study_uid in list_instances_by_study:
                    list_instances_by_study[study_uid] = []
                list_instances_by_study[study_uid].append(instance_uid)
                if not study_uid in list_series_by_study:
                    list_series_by_study[study_uid] = []
                list_series_by_study[study_uid].append(series_uid)
                # list_all_study.add(study_uid)
                list_all_study.append(study_uid)
                add_row(instances_by_study_series, (study_uid, series_uid, instance_uid))
    return instances_by_study_series, list_all_study, list_all_series, \
           list_all_instances, list_instances_by_study, list_series_by_study


def get_metadata_from_instance_uid(instance_uid):
    """
    Retrieves Metadata from dicom files given instance_uid
    :param instance_uid: str
    :return: json metadata file
    """
    dicom_path = list(StorageMetadata.objects.filter(instance_uid=instance_uid)\
                      .all().values('file_path'))[0]['file_path']
    dsdcm = pydicom.dcmread(dicom_path, stop_before_pixels=True)
    data_json = dsdcm.to_json_dict()
    metadata = json.loads(json.dumps(data_json))
    return metadata


def get_metadata_from_series_uid(series_uid):
    """
    Retrieves Metadata from dicom files given series_uid
    :param series_uid: str
    :return: json metadata file
    """
    metadata = []
    dict_instance_uid = list(
        Instance.objects.filter(series_uid=series_uid).all().values('instance_uid'))
    list_instance_uid = dict_to_list(dict_instance_uid)

    for instance_uid in list_instance_uid:
        dicom_path = list(StorageMetadata.objects.filter(instance_uid=instance_uid)\
                          .all().values('file_path'))[0]['file_path']
        dsdcm = pydicom.dcmread(dicom_path, stop_before_pixels=True)
        data_json = dsdcm.to_json_dict()
        metadata.append(data_json)
    metadata = json.loads(json.dumps(metadata))
    return metadata


def get_metadata_from_study_uid(study_uid):
    """
    Retrieves Metadata from dicom files gievn study_uid
    :param study_uid: str
    :return:  json metadata file
    """
    metadata = []
    dict_instance_uid = list(
        Instance.objects.filter(study_uid=study_uid).all().values('instance_uid'))
    list_instance_uid = dict_to_list(dict_instance_uid)

    for instance_uid in list_instance_uid:
        dicom_path = list(StorageMetadata.objects.filter(instance_uid=instance_uid).all()\
                          .values('file_path'))[0]['file_path']
        dsdcm = pydicom.dcmread(dicom_path, stop_before_pixels=True)
        data_json = dsdcm.to_json_dict()
        metadata.append(data_json)
    metadata = json.loads(json.dumps(metadata))
    return metadata


def compare_elements(element1, element2):
    """
    Deep recursive comparing function
    :param element1: Any element
    :param element2: Any element
    :return: a boolean that returns if the both elements are equal
    """
    if not isinstance(element1, type(element2)):
        print("types differ: elem1", type(element1), element1, "elem2", type(element2), element2)
        return False
    if isinstance(element1, str):
        if element1 != element2:
            print("values are different:", element1, element2)
            return False
        return True
    if isinstance(element1, (float, int)):
        if element1 != element2:
            print("values are different:", element1, element2)
            return False
        return True
    if isinstance(element1, list):
        for couple in zip(element1, element2):
            ret = compare_elements(couple[0], couple[1])
            if not ret:
                return False
        return True

    set1 = set(element1.keys())
    set2 = set(element2.keys())
    diff1 = set1.difference(set2)
    diff2 = set2.difference(set1)
    if len(diff1) != 0:
        print("not in 2", diff1)
        return False
    if len(diff2) != 0:
        print("not in 1", diff2)
        return False
    for key in set1.intersection(set2):
        ret = compare_elements(element1[key], element2[key])
        if not ret:
            return False
    return True


def parse_multi_part(content, boundary=b'DICOM DATA BOUNDARY'):
    """
    Add content to the related part of a multi part responses
    :param content: the content to be added
    :param boundary: the boundary between parts
    :return: The content with parted added
    """
    SEP = b'--'
    CRLF = b'\r\n'
    content_type = b'Content-Type: application/dicom'
    beg_line = SEP + boundary + CRLF + content_type + CRLF + CRLF
    end_line = CRLF + SEP + boundary + SEP + CRLF
    pbeg = content.index(beg_line)
    pfin = content.index(end_line, pbeg)
    parsed_content = content[len(beg_line): pfin]
    return parsed_content


def read_dicom(instance_uid):
    """
    Reads a dicom file and returns its content
    :param instance_uid: str
    :return: the DICOM content
    """
    dicom_filepath = list(StorageMetadata.objects.filter(instance_uid=instance_uid)\
                          .all().values('file_path'))[0]['file_path']
    dsdcm = pydicom.dcmread(dicom_filepath, stop_before_pixels=False)
    with BytesIO() as bcontent:
        pydicom.dcmwrite(bcontent, dsdcm)
        encoded_ds = bcontent.getvalue()
    return encoded_ds
