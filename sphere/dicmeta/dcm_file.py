# pylint: disable=eval-used
from datetime import datetime

from pydicom.dataset import Dataset

from sphere.utilities.utils_database import read_copy_extended_db


class DcmFile(Dataset):
    """ Add value of tag in column name of all tables. """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Create alias for ID/UID
        self.instanceUID = self.SOPInstanceUID
        self.studyUID = self.StudyInstanceUID
        self.seriesUID = self.SeriesInstanceUID
        self.patientID = self.PatientID

    def file_storage_metadata(self):
        """
        Get file storage  metadata

        :return: The metadata
        :rtype: dict
        """
        meta = {
            'instanceUID': str(self.SOPInstanceUID),
            'seriesUID': str(self.SeriesInstanceUID),
            'studyUID': str(self.StudyInstanceUID),
            'patientID': str(self.PatientID)
        }
        self.extended(meta, 'instance')
        return meta

    def series_metadata(self):
        """
        Get series metadata

        :return: The metadata
        :rtype: dict
        """
        meta = {
            'seriesUID': str(self.SeriesInstanceUID),
            'studyUID': str(self.StudyInstanceUID),
            'patientID': str(self.PatientID),
            'seriesDate': self.check_attribute_dicom('SeriesDate'),
            'seriesDescription': self.check_attribute_dicom('SeriesDescription'),
            'stationName': self.check_attribute_dicom('StationName'),
            'bodyPartExamined': self.check_attribute_dicom('BodyPartExamined'),
            'manufacturer': self.check_attribute_dicom('Manufacturer'),
            'manufacturerModelName': self.check_attribute_dicom('ManufacturerModelName')
        }

        try:
            meta['modality'] = str(str(self.Modality))
        except Exception:
            meta['modality'] = 'Unknown'

        self.extended(meta, 'series')
        return meta

    def study_metadata(self):
        """
        Get study metadata

        :return: The metadata
        :rtype: dict
        """
        meta = {
            'studyUID': str(self.StudyInstanceUID),
            'patientID': str(self.PatientID),
            'dateStudy': self.check_attribute_dicom('StudyDate'),
            'institutionName': self.check_attribute_dicom('InstitutionName'),
            'accessionNumber': self.check_attribute_dicom('AccessionNumber'),
            'protocolName': self.check_attribute_dicom('ProtocolName'),
            'studyDescription': self.check_attribute_dicom('StudyDescription')
        }
        self.extended(meta, 'study')
        return meta

    def patient_metadata(self):
        """
        Get patient metadata

        :return: The metadata
        :rtype: dict
        """
        meta = {
            'patientID': str(self.PatientID),
            'patientName': self.check_attribute_dicom('PatientName'),
            'patientSex': self.check_attribute_dicom('PatientSex'),
            'patientBirthDate': self.check_attribute_dicom('PatientBirthDate')
        }
        self.extended(meta, 'patient')
        return meta

    def check_attribute_dicom(self, keyword):
        """
        Check and return value of keyword or return None if not exists

        :param keyword: The keyword of DICOM
        :type keyword: str
        :return: Return value
        :rtype: str
        """
        try:
            value = str(eval("self." + keyword))
        except Exception:
            value = None

        return value

    def extended(self, meta, table_name):
        """
        Add extended attribute of database in dict metadata

        :param meta: Dictionary of metadata
        :type meta: dict
        :param table_name: Name of table

            list of possible value of query_model:
                - patient
                - study
                - series
                - instance
        :type table_name: str
        """
        json_extended = read_copy_extended_db()
        if json_extended and table_name in json_extended.keys():
            for tag, dic in json_extended[table_name].items():
                field_name = dic['field_name']
                if 'parents' in dic:
                    parents_list_tags = dic['parents'].split(',')
                    list_res_p = []
                    for p_tag in parents_list_tags:
                        list_res_p.extend([str([p_tag[:4], p_tag[4:]]), str([0])])
                    try:
                        meta[field_name] = str(eval("self" + ''.join(list_res_p) + str([tag[:4], tag[4:]]) + '.value'))
                    except Exception:
                        meta[field_name] = None
                else:
                    try:
                        meta[field_name] = str(self[tag[:4], tag[4:]].value)
                    except Exception:
                        meta[field_name] = None
