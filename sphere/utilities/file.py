"""
The functions utils
"""

import os
import csv
import datetime

from sphere.logs.logs import LOG_CODE_PYTHON


def file_instance_date(study_uid, series_uid, instances_uid, file_name,
                       path_folder):
    """
    Create a file that contains a date study_uid, series_uid and instances_uid

    :param study_uid: The Study UID
    :type study_uid: str
    :param series_uid: The Series UID
    :type series_uid: str
    :param instances_uid: The Instance UID
    :type instances_uid: str
    :param file_name: The file name
    :type file_name: str
    :param path_folder: The path of folder
    :type path_folder: str
    """
    date = str(datetime.datetime.now()).split(" ")[0]
    file_to_open = os.path.join(path_folder, file_name)
    file = open(file_to_open, 'a')
    date_instance = \
        date + " | " + study_uid + " | " + series_uid + " | " + instances_uid
    file.write(date_instance + "\n")
    file.close()


def create_file_txt(path, file_name, data):
    """
    Create a file txt

    :param path: The path of the file
    :type path: str
    :param file_name: Name of the file
    :type file_name: str
    :param data: The data of the file
    :type data: list
    """

    file = open(os.path.join(path, file_name), 'w')
    if isinstance(data, list):
        for line in data:
            file.write(line+"\n")
    else:
        file.write(str(data))
    file.close()


def create_file_csv(path, file_name, data, header):
    """
    Create a file csv

    :param path: The path of the file
    :type path: str
    :param file_name: Name of file
    :type file_name: str
    :param data: The data of file
    :type data: list
    :param header: The header of file
    :type header: list
    """
    with open(os.path.join(path, file_name), 'w') as csv_file:
        write = csv.writer(csv_file)
        write.writerow(header)
        write.writerows(data)


def read_file_txt(file_path):
    """
    Read a text file

    :param file_path: The path of the file
    :type file_path: str
    :return: The data if it exists
    :rtype: str or None
    """
    try:
        file = open(file_path, "r")
        return file.read()
    except FileNotFoundError:
        LOG_CODE_PYTHON.error("This file '%s' not exits", file_path)
        return None


def read_file_return_list(file_path):
    """
    Read file and return list of file lines

    :param file_path: The file path
    :type file_path: str
    :return: List of file lines
    :rtype: list
    """
    if not os.path.isfile(file_path):
        txt_except = "File '%s' not find" % file_path
        raise Exception(txt_except)
    return [line.rstrip('\n') for line in open(file_path)]
