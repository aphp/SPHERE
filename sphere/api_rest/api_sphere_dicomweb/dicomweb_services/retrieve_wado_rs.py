""" Retrieve DICOM objects (WADO-RS) """

import os
import sys
import pydicom

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from sphere.dicmeta.database_pacs import DatabasePACS
from sphere.api_rest.api_sphere_dicomweb.utils import return_list_uid
from sphere.logs.logs import LOG_API_DICOMWEB
from sphere.settings import API_DECOMPRESS_PIXELS


class RetrieveOrmSqlalchemy:
    """ Search and return the path of dicom file with ORM SqlAlchemy:
     * All studies
     * All series of one study
     * All instance of one study
     * All instances of one study and series
     * All instances
     """

    def __init__(self, session):
        self.db_pacs = DatabasePACS()
        self.session = session

    def files_path(self, instance_uid):
        """
        Returns the file path of instance_uid

        :param instance_uid: The instance uid
        :type instance_uid: str
        :return: Return file path
        :rtype: str
        """
        dict_storage_metadata = self.session.query(
            self.db_pacs.FileStorageMetadataDicomModel.filePath).filter(
                self.db_pacs.FileStorageMetadataDicomModel.instanceUID == instance_uid).all()
        file_path = return_list_uid(dict_storage_metadata)[0]
        self.db_pacs.clear_session(self.session)
        return file_path

    def list_paths_dicom(self, study_uid, series_uid=None, instance_uid=None):
        """
        Returns list of paths dicom_file

        :param study_uid: The study uid
        :type study_uid: str
        :param series_uid: The series uid
        :type series_uid: str
        :param instance_uid: The instance uid
        :type instance_uid: str
        :return: Return list of dicom file paths
        :rtype: list
        """
        if instance_uid and series_uid and study_uid:
            dict_instance = self.session.query(
                self.db_pacs.FileStorageMetadataDicomModel.instanceUID).filter(
                    self.db_pacs.FileStorageMetadataDicomModel.studyUID == study_uid).filter(
                        self.db_pacs.FileStorageMetadataDicomModel.seriesUID == series_uid).filter(
                            self.db_pacs.FileStorageMetadataDicomModel.instanceUID == instance_uid).all()
        elif series_uid and study_uid:
            dict_instance = self.session.query(
                self.db_pacs.FileStorageMetadataDicomModel.instanceUID).filter(
                    self.db_pacs.FileStorageMetadataDicomModel.studyUID == study_uid).filter(
                        self.db_pacs.FileStorageMetadataDicomModel.seriesUID == series_uid).all()
        else:  # only study
            dict_instance = self.session.query(
                self.db_pacs.FileStorageMetadataDicomModel.instanceUID).filter(
                    self.db_pacs.FileStorageMetadataDicomModel.studyUID == study_uid).all()
        self.db_pacs.clear_session(self.session)
        paths_dicom_file = []
        for instance_uid in return_list_uid(dict_instance):
            file_path = self.files_path(instance_uid)
            paths_dicom_file.append(file_path)

        return paths_dicom_file

    # ======= Get File ====== #

    def frame_of_instance(self, instance_uid, frame):
        """
        Get pixel data

        :param instance_uid: The instance uid
        :type instance_uid: str
        :param frame: Frame number
        :type frame: str
        :return: The pixel data of dcm file
        :rtype: bytes
        """
        file_path = self.files_path(instance_uid)
        dataset = pydicom.dcmread(file_path)

        content = b''
        try:
            
            if API_DECOMPRESS_PIXELS:
                # Calling pixel_array decompresses the pixels using the pylibjpeg plugins
                content = dataset.pixel_array.tobytes()
            else :
                # Fetching the pixels as is (equivalent of PixelData)
                content = dataset[(0x7fe0, 0x0010)].value

        except KeyError:
            LOG_API_DICOMWEB.error("This tag '(7fe0, 0010)' (PixelData) does "
                                   "not exists in this file: %s", file_path)
        except Exception as exc:
            LOG_API_DICOMWEB.exception(exc)
        return content
