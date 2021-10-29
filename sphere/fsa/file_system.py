"""
Create folder and save the DICOM file
"""
import os
import shutil
from multiprocessing.pool import ThreadPool  # Process
from dirsync import sync

from sphere import settings
from sphere.logs.logs import LOG_FILE_DICOM


class FileSystem:
    """ All file system methods  """
    def __init__(self):
        self.dicom_folder = settings.FS_PATH_STORAGE

    def remove_list_file(self, list_path):
        """
        Remove the list of files in multiprocessing

        :param list_path: List of file paths
        :type list_path: list
        """
        thread_pool = ThreadPool(4)
        thread_pool.map(self.remove_file, list_path)
        thread_pool.close()

    @staticmethod
    def remove_file(path):
        """
         Remove file

        :param path: The file path
        :type path: str
        """
        try:
            os.remove(path)
            LOG_FILE_DICOM.debug("%s removed successfully", path)
        except OSError as error:
            LOG_FILE_DICOM.error("%s \n File path can not be removed", error)

    def duplicate_folder_source(self, sourcedir):
        """
        Duplicate of folder

        :param sourcedir: The source directory
        :type sourcedir: str
        """
        sync(sourcedir, self.dicom_folder, 'sync', verbose=True)

    # Duplicate only for classical fs
    def duplicate_folder(self, target_dir):
        """
        Duplicate of folder

        :param target_dir: The target directory
        :type target_dir: str
        """
        sync(self.dicom_folder, target_dir, 'sync', verbose=True)

    @staticmethod
    def make_dir(folder_name):
        """
        Create folder if not exist

        :param folder_name: Folder name or folder path
        :type folder_name: str
        """
        if not os.path.exists(folder_name):
            LOG_FILE_DICOM.info("Create folder %s ", folder_name)
            os.makedirs(folder_name)
        else:
            LOG_FILE_DICOM.info("The folder %s  is exists", folder_name)


class FileSystemStore(FileSystem):
    """ Save data receive from cstore"""
    def __init__(self, ds=None):
        super().__init__()
        if not hasattr(ds, 'tmp_path'):
            LOG_FILE_DICOM.error('No file path to save ds')
            raise ValueError('No file path to save ds')
        self.ds = ds  # pylint: disable=invalid-name
        self.file_name = self.ds.SOPInstanceUID  # instanceUID
        self.dir_path = settings.FS_PATH_STORAGE
        # TODO : Ajouter une config pour les differents types d'architecture dossier
        self.directory_path_nested_logic_dicom()

    def directory_path_nested_logic_dicom(self):
        """
        return Directory path nested logic DICOM
        """
        self.dir_path = os.path.join(
            self.dir_path, self.ds.PatientID, self.ds.StudyInstanceUID,
            self.ds.SeriesInstanceUID)

    def save(self):
        """
        Save DICOM file

        :return: Absolute path of the DICOM file
        :rtype: str
        """
        file_path = os.path.join(self.dir_path, self.file_name)
        try:
            # Create sub folder if not exist
            FileSystem.make_dir(self.dir_path)
            # self.ds.save_as(file_path, write_like_original=False)
            LOG_FILE_DICOM.info('the file %s  was successfully saved at %s',
                                file_path, self.dir_path)
            shutil.move(self.ds.tmp_path, file_path)

            return os.path.abspath(file_path)
        except FileExistsError:
            try:
                shutil.move(self.ds.tmp_path, file_path)
                LOG_FILE_DICOM.debug(
                    "Restart move DICOM %s", self.ds.SOPInstanceUID)
                return os.path.abspath(file_path)
            except Exception as error:
                LOG_FILE_DICOM.exception(error)
                LOG_FILE_DICOM.error(
                    'error in the save of %s', self.ds.SOPInstanceUID)
                return os.path.abspath(self.ds.tmp_path)
        except Exception as error:
            LOG_FILE_DICOM.error('error in the save of %s',
                                 self.ds.SOPInstanceUID)
            LOG_FILE_DICOM.exception(error)
            return os.path.abspath(self.ds.tmp_path)
