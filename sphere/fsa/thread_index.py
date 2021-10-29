# pylint: disable=invalid-name
import os
from datetime import datetime
from time import sleep
import threading
import queue

from pydicom import dcmread
from pydicom.errors import InvalidDicomError
from sphere.logs.logs import LOG_CMD_INDEX
from sphere.dicmeta.database_pacs import DatabasePACS
from sphere.dicmeta.dcm_manager import DcmManager


class QueueGlobal:
    """Define a global object """
    def __init__(self):
        self.g_queue_index = queue.Queue()


queue_global = QueueGlobal()
g_queue_index = queue_global.g_queue_index


class ThreadIndex(threading.Thread):
    """ Parser website with Thread"""
    n_files_not_saved_db = 0

    def __init__(self, name, dicom_folder):
        threading.Thread.__init__(self)
        self.name = name
        self.stop = False
        self.dicom_folder = dicom_folder
        self.queue = g_queue_index
        from sphere.dicmeta.thread import g_queue_to_load
        self.db_pacs = DatabasePACS(g_queue_to_load)

    def instance_model(self, dcm, fp):
        """
            Create instance

            :param dcm: We have delete indexed files.
            :type dcm: :py:class: `Dataset`
            :param fp: The file path
            :type fp: str
        """
        LOG_CMD_INDEX.debug('in fsa, %s', self.db_pacs.db_queue.qsize())

        instance_storage_metadata = {
            'dt_deb_storage': datetime.now(),
            'filesize': os.stat(fp).st_size,
            'storageMethod': 'FS',
            'storageStatus': 0,
            'filePath': fp,
            'dt_end_storage': datetime.now()
        }

        dcm_meta = DcmManager([dcm], db_pacs=self.db_pacs)
        dcm_meta.add_metadata_dicom(instance_storage_metadata, self.db_pacs.db_queue)

    def run(self):
        stop_before_pixels = True
        print("Starting " + self.name)
        while True:
            for path, _subdirs, files in os.walk(self.dicom_folder):
                for fpath in files:
                    LOG_CMD_INDEX.debug("fpath = %s", fpath)
                    try:
                        fp = os.path.join(os.path.abspath(path), fpath)
                        dcm = dcmread(os.path.join(path, fpath),
                                      stop_before_pixels=stop_before_pixels)
                        self.instance_model(dcm, fp)
                        self.queue.put(fp)
                    except InvalidDicomError:
                        self.n_files_not_saved_db += 1
                        LOG_CMD_INDEX.warning(" %s is not a DICOM regular file",
                                              os.path.join(
                                                  os.path.abspath(path), fpath))
                    except FileNotFoundError:
                        self.n_files_not_saved_db += 1
                        LOG_CMD_INDEX.critical("The file '%s' does not exist", path)
                    except Exception as exc:
                        self.n_files_not_saved_db += 1
                        LOG_CMD_INDEX.critical("error: '%s', path: '%s'", exc,
                                               os.path.join(path, fpath))
                    if self.stop:
                        break
                if self.stop:
                    break
            LOG_CMD_INDEX.info("End thread index")
            break

    # pylint: disable=missing-function-docstring
    def stop_thread(self):
        self.stop = True

    def __repr__(self):
        return "<Thread(name='%s')>" % self.name
