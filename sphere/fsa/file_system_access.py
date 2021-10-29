"""
file system access
"""
# pylint: disable=invalid-name
import os
from time import time, sleep
import traceback
from datetime import datetime

from pydicom.dataset import Dataset
from pynetdicom import (
    PYNETDICOM_IMPLEMENTATION_UID,
    PYNETDICOM_IMPLEMENTATION_VERSION
)

from sphere.utilities.string_tools import \
    string_belongs_to_list_case_and_space_insensitive
from sphere.dicmeta.database_pacs import DatabasePACS
from sphere.dicmeta.dcm_manager import DcmManager
from sphere import settings
from sphere.fsa.file_system import FileSystem
from sphere.fsa.file_system import FileSystemStore
from sphere.dicmeta.insert_in_database import InsertData
from sphere.utilities.msg import execution_time
from sphere.logs.logs import LOG_FILE_DICOM, LOG_DATABASE, LOG_CMD_INDEX
from sphere.fsa.thread_index import ThreadIndex
from sphere.fsa.thread_index import g_queue_index


class FileSystemAccess:
    """
    this class takes 2 parameters, a dataset as 'ds' and a context as
    'context' those 2 parameters are mandatory
    """
    def __init__(self, ds=None, db_pacs=None, context=None):
        if db_pacs is None:
            # TODO better integration with no dynamic import
            from sphere.dicmeta.thread import g_queue_to_load
            self.db_pacs = DatabasePACS(g_queue_to_load)
        else:
            self.db_pacs = db_pacs

        self.ds = ds
        if ds is not None:
            self.path_tmp_file = os.path.join(
                settings.TMP_PATH_STORAGE, self.ds.SOPInstanceUID)
            self.dcm = DcmManager(self.ds, db_pacs=self.db_pacs)

        self.context = context
        self.storage = settings.STORAGE_METHOD

        self.dicom_folder = settings.FS_PATH_STORAGE

        self.insert_data = InsertData(self.db_pacs)
        self.file_system = FileSystem()

    def create_file_meta(self):
        """
        This function take the dataset and the context and build the
        dataset with the metadata that will be saved. The function return
        either the dataset if no error or None if there was an error

        :return: True or False
        :rtype: bool
        """
        if self.ds is not None and self.context is not None:
            LOG_FILE_DICOM.debug(
                'The SOPInstanceUID dataset is: %s, the abstract_syntax is: '
                '%s, the transfer_syntax is: %s',
                str(self.ds.SOPInstanceUID),
                str(self.context.abstract_syntax),
                str(self.context.transfer_syntax))
            try:
                meta = Dataset()
                meta.MediaStorageSOPClassUID = self.ds.SOPClassUID
                meta.MediaStorageSOPInstanceUID = self.ds.SOPInstanceUID
                meta.ImplementationClassUID = PYNETDICOM_IMPLEMENTATION_UID
                meta.ImplementationVersionName =\
                    PYNETDICOM_IMPLEMENTATION_VERSION
                meta.TransferSyntaxUID = self.context.transfer_syntax
                self.ds.file_meta = meta
                self.ds.is_little_endian =\
                    self.context.transfer_syntax.is_little_endian
                self.ds.is_implicit_VR =\
                    self.context.transfer_syntax.is_implicit_VR
                LOG_FILE_DICOM.info('dataset constructed successfully')
                return True
            except Exception as exc:
                LOG_FILE_DICOM.error('unable to construct the dataset')
                LOG_FILE_DICOM.exception(exc)
                traceback.print_exc()
                return False
        else:
            LOG_FILE_DICOM.debug(
                'the SOPInstanceUID dataset is: %s the context is: '
                '%s either the dataset or the context or both is/are '
                'not defined', str(self.ds.SOPInstanceUID), str(self.context))
            return False

    def store_fs(self):
        """
        this function call the create_file_meta() function and if it succeed """
        try:
            if os.path.exists(self.path_tmp_file):
                storage_status = 0
            else:
                storage_status = 1
            self.instance_storage_metadata = {
                'dt_deb_storage': datetime.now(),
                'filesize': os.stat(self.path_tmp_file).st_size,
                'storageMethod': settings.STORAGE_METHOD,
                'storageStatus': storage_status
            }

            if self.ds is not None:
                fs = FileSystemStore(self.ds)
                fp = fs.save()
            else:
                LOG_FILE_DICOM.error(
                    'the dataset is not existing see previous error')

            self.instance_storage_metadata['filePath'] = fp
            self.instance_storage_metadata['dt_end_storage'] = datetime.now()
        except Exception as error:
            LOG_FILE_DICOM.exception(error)

    def store(self):
        """ Save DICOM file"""
        if self.create_file_meta():
            self.ds.save_as(self.path_tmp_file, write_like_original=False)
            self.ds.tmp_path = self.path_tmp_file
            if string_belongs_to_list_case_and_space_insensitive(
                    string=self.storage, list_strings=settings.LIST_STORAGES):
                self.store_fs()
                try:
                    self.dcm.add_metadata_dicom(
                        self.instance_storage_metadata, self.db_pacs.db_queue)
                    print('in fsa, ', self.db_pacs.db_queue.qsize())
                except Exception as error:
                    LOG_DATABASE.exception(
                        "Error store db filepath = %s \n %s",
                        self.instance_storage_metadata['filePath'], error)

    def clean_queue_index(self, erase, g_queue_index, number_instance):
        """
            If erase True: remove all files
            If erase False: clean queue

            :param erase: We have delete indexed files.
            :type erase: str, optional, default False
            :param g_queue_index: The queue of file path
            :type g_queue_index: :py:class: `queue.Queue`
            :param number_instance: Number of instance
            :type number_instance: int
        """
        if erase:
            list_fp = [g_queue_index.get() for _ in range(number_instance)]
            self.file_system.remove_list_file(list_fp)
        else:
            g_queue_index.queue.clear()

    @staticmethod
    def summarize_index(exec_time, n_files_saved_db, n_files_not_saved_db):
        """
            Summarize of index

            :param exec_time: The execution time
            :type exec_time: str, optional
            :param n_files_saved_db: Number files saved in database
            :type n_files_saved_db: int
            :param n_files_not_saved_db: Number files not saved in database
            :type n_files_not_saved_db: int
        """
        return "{} \n ========> Files add to the database equal to {} \n " \
               "========> Files is not saved in the database equal to" \
               " {} ".format(exec_time, n_files_saved_db, n_files_not_saved_db)

    def index_dicom_folder(self, erase=False, dicom_folder=None):
        """
        Index DICOM folder

        :param erase: We have delete indexed files.
        :type erase: str, optional, default False
        :param dicom_folder: The dicom folder
        :type dicom_folder: str, optional
        """
        # List all files
        if dicom_folder and dicom_folder not in self.dicom_folder:
            self.dicom_folder = dicom_folder
        LOG_CMD_INDEX.info("Start Index all DICOM file in this path '%s' %s",
                           self.dicom_folder, " and remove DICOM file" if erase
                           else " ")
        n_files_saved_db = 0
        thread_index = ThreadIndex('thread_index', self.dicom_folder)
        thread_index.daemon = True  # causes the thread to terminate when the main process ends.
        thread_index.start()  # Start thread_db_save
        sleep(70)
        start_time = time()
        try:
            while not self.db_pacs.db_queue.empty() or not g_queue_index.empty() or thread_index.is_alive():
                try:
                    LOG_CMD_INDEX.info('Insert %s instances in database.',
                                       self.db_pacs.db_queue.qsize())
                    self.insert_data.bulk_insert_from_queue(self.db_pacs.db_queue)
                    number_instance = self.insert_data.number_insert
                    n_files_saved_db = n_files_saved_db + number_instance
                    self.clean_queue_index(erase, g_queue_index, number_instance)

                except Exception as exc:
                    number_instance = self.insert_data.number_insert
                    for _ in range(number_instance):
                        g_queue_index.get()
                    LOG_CMD_INDEX.exception(exc)

                if self.db_pacs.db_queue.empty() and not g_queue_index.empty():
                    sleep(60)
                    if self.db_pacs.db_queue.empty():
                        LOG_CMD_INDEX.warning(
                            "It's been a minute since the database queue is "
                            "empty and the path queue is not empty. So I'm "
                            "going to stop the process. g_queue_index = %s",
                            g_queue_index.qsize())
                        break
                if thread_index.is_alive() and self.db_pacs.db_queue.empty():
                    LOG_CMD_INDEX.warning("Thread index is faster than the "
                                          "main thread which saves in the "
                                          "database, 'then sleep 60s main "
                                          "thread'")
                    sleep(60)
                LOG_CMD_INDEX.info("Thread index is alive or no: %s",
                                   thread_index.is_alive())
            msg = self.summarize_index(execution_time(start_time),
                                       n_files_saved_db,
                                       thread_index.n_files_not_saved_db)
            print(msg)
            LOG_CMD_INDEX.info(msg)
            thread_index.join()
            if thread_index.is_alive():
                thread_index.stop_thread()
        except (KeyboardInterrupt, SystemExit):
            LOG_CMD_INDEX.warning("you clicked Ctrl + C to stop the process."
                                  "I finish inserting the data in memory into "
                                  "the database and I stop the proccess."
                                  " db_queue = %s", self.db_pacs.db_queue.qsize())
            thread_index.stop_thread()
            while not self.db_pacs.db_queue.empty():
                self.insert_data.bulk_insert_from_queue(self.db_pacs.db_queue)
                number_instance = self.insert_data.number_insert
                n_files_saved_db = n_files_saved_db + number_instance
                self.clean_queue_index(erase, g_queue_index, number_instance)
            msg = self.summarize_index(execution_time(start_time),
                                       n_files_saved_db,
                                       thread_index.n_files_not_saved_db)
            print(msg)
            LOG_CMD_INDEX.info(msg)
        except Exception as exc:
            LOG_CMD_INDEX.exception(exc)
        finally:
            if not self.db_pacs.db_queue.empty():
                LOG_CMD_INDEX.error("finally: db_pacs.db_queue is not empty,"
                                    "Queue size: %s", self.db_pacs.db_queue.qsize())
            else:
                LOG_CMD_INDEX.info('finally: db_pacs.db_queue is empty')
