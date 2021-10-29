"""
The functions utils of DICOM
"""
# pylint: disable=too-many-locals
import os

from pydicom import dcmread
from pydicom.errors import InvalidDicomError
from sphere.logs.logs import LOG_TRANSACTION, LOG_CMD_INDEX, LOG_CODE_PYTHON


# pylint: disable=bare-except
def dicom_display_field_value(data, code, field=""):  # not used
    """
    DICOM display field value

    :param data: The data
    :type data: dict
    :param code: The code
    :type code: str
    :param field: The field
    :type field: str, optional
    """
    try:
        print(data[code])
    except:
        print(str(code).replace('\'', '') + " " + field)


def check_dicom_file(
        path, list_dicom_instance_path, list_ds, dic_instance_path,
        return_type):
    """
    Check if the file is a DICOM or not and if exists or not

    :param path: The path of the DICOM file
    :type path: str
    :param list_dicom_instance_path: A list that contains the paths of
        the DICOM file
    :type list_dicom_instance_path: list
    :param list_ds: List dataset DICOM
    :type list_ds: list
    :param dic_instance_path: dict dataset and path
    :type dic_instance_path: dict
    :param return_type: Dict contains the paths and dataset
    :type return_type: str
    """
    try:
        dataset = dcmread(path, stop_before_pixels=True)
        list_dicom_instance_path.append(path)
        if return_type == "list_ds":
            list_ds.append(dataset)
        elif return_type == "dict":
            dic_instance_path[path] = dataset
    except InvalidDicomError:
        LOG_TRANSACTION.error("%s is not a DICOM regular file", path)
    except FileNotFoundError:
        LOG_TRANSACTION.error("The file '%s' does not exist", path)


def get_all_dicom_file(dicom_folder, force_disk_read=False,
                       stop_before_pixels=True):
    """
    Get all DICOM file

    :param force_disk_read: Force disk read or not
    :type force_disk_read: bool, optional
    :param stop_before_pixels: Stop before Pixels
    :type stop_before_pixels: bool, optional
    :return: Two lists (DICOM file and dataset DICOM)
    :rtype: tuple (str, :py:class:`pydicom.dataset.Dataset`)
    """
    if force_disk_read:
        for path, _subdirs, files in os.walk(dicom_folder):
            for fpath in files:
                LOG_CMD_INDEX.debug("fpath = %s", fpath)
                try:
                    yield os.path.join(os.path.abspath(path), fpath),\
                        dcmread(
                            os.path.join(path, fpath),
                            stop_before_pixels=stop_before_pixels)
                except InvalidDicomError:
                    LOG_CMD_INDEX.warning(" %s is not a DICOM regular file",
                                          os.path.join(
                                              os.path.abspath(path), fpath))
                except FileNotFoundError:
                    LOG_CMD_INDEX.critical("The file '%s' does not exist", path)
                except Exception as exc:
                    LOG_CMD_INDEX.critical("error: '%s', path: '%s'", exc,
                                           os.path.join(path, fpath))
    else:
        print('Find all DICOM with database not implemented yet')


def all_dicom_instance_path(dicom_path, return_format=None):
    """
    Return lists path of all instances DICOM

    :param dicom_path: Path of the DICOM file
    :type dicom_path: str
    :param return_format: What format on returns the data

        list of possible value of return_format:
            - list_ds : list of dataset
            - dict : dictionary of path and dataset
            - None  : (default) list of path DICOM
    :type return_format: str or None, optional
    :return: list path of all DICOM or list ds DICOM or dict DICOM
    :rtype: list [:py:class:`pydicom.dataset.Dataset`] or dict
    """
    list_dicom_instance_path = []
    list_ds = []
    dic_instance_path = {}
    try:
        # if cstore request is called giving a list of DICOM file path
        if isinstance(dicom_path, list):
            for path in dicom_path:
                check_dicom_file(path, list_dicom_instance_path, list_ds,
                                 dic_instance_path, return_format)
        # if cstore request is called giving a path to a folder
        elif os.path.isdir(dicom_path):
            for path, subdirs, files in os.walk(dicom_path):
                subdirs[:] = [d for d in subdirs if not d[0] == '.']
                for fpath in files:
                    if not fpath[0] == '.':
                        check_dicom_file(os.path.join(path, fpath),
                                         list_dicom_instance_path, list_ds,
                                         dic_instance_path, return_format)

        # if cstore is called with a single DICOM file
        elif isinstance(dicom_path, str):
            if os.path.exists(dicom_path):
                check_dicom_file(dicom_path, list_dicom_instance_path, list_ds,
                                 dic_instance_path, return_format)
            else:
                LOG_TRANSACTION.critical("The file '%s' does not exist",
                                         dicom_path)

        if return_format == "list_ds":
            all_dicom_path = list_ds
        elif return_format == "dict":
            all_dicom_path = dic_instance_path
        else:
            all_dicom_path = list_dicom_instance_path

        return all_dicom_path
    except Exception as error:
        LOG_CODE_PYTHON.exception(error)
        return []


def get_uid(dataset):
    """
        Get study_uid or series_uid of dataset

        :param dataset: The Dataset
        :type dataset: :py:class:`pydicom.dataset.Dataset`
        :return: Return uid
        :rtype: str
    """
    qr_level = dataset.QueryRetrieveLevel.upper()
    if qr_level == 'STUDY':
        uid = dataset.StudyInstanceUID
    elif qr_level == 'SERIES':
        uid = dataset.SeriesInstanceUID
    return uid


def check_exists_file(all_path, paths_exists, paths_not_exists):
    """
    Check whether the file exits or not and add it to one of the two lists
    (paths_exists, paths_not_exists)

    :param all_path: list of all file paths
    :type all_path: list
    :param paths_exists: List of file paths exists
    :type paths_exists: list
    :param paths_not_exists: List of file paths does not exist
    :type paths_not_exists: list
    """
    for instance_path in all_path:
        if not os.path.exists(instance_path):
            paths_not_exists.append(instance_path)
        else:
            paths_exists.append(instance_path)

    msg = "all path check: {}, paths_exists: {}, paths_not_exists: {}".format(
        len(all_path), len(paths_exists), len(paths_not_exists))
    print(msg)
    LOG_TRANSACTION.info(msg)
    path_rest = list(set(all_path) - set(paths_exists) - set(paths_not_exists))
    if path_rest:
        for path in path_rest:
            LOG_TRANSACTION.warning('This path %s is duplicate', path)
            # TODO supprimer tous les elemenets de la liste
