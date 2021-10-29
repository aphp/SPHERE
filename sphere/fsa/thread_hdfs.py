# pylint: disable=invalid-name
import os
from time import sleep
import threading
import queue
import subprocess

from sphere.utilities.file import create_file_txt
from sphere import settings


class QueueGlobal:
    """Define a global object """
    def __init__(self):
        self.g_queue_hdfs = queue.Queue()


queue_global = QueueGlobal()
g_queue_hdfs = queue_global.g_queue_hdfs


class ThreadHdfs(threading.Thread):
    """ Parser website with Thread"""

    def __init__(self, name, qr_level):
        threading.Thread.__init__(self)
        self.name = name
        self.stop = False
        self.queue = g_queue_hdfs
        self.qr_level = qr_level

    def run(self):
        print("Starting " + self.name)
        while True:
            sleep(settings.TIME_SLEEP_THREAD_HDFS)
            print('=========== SIZE QUEUE  HDFS : %s' % (self.queue.qsize()))
            if self.queue.qsize():
                if self.queue.qsize() > settings.NUMBER_STUDY:
                    list_study_uid = [self.queue.get() for _ in
                                      range(settings.NUMBER_STUDY)]
                else:
                    list_study_uid = list(self.queue.queue)
                    self.queue.queue.clear()

                create_file_txt(settings.PATH_FILE_CSV_HDFS,
                                settings.NAME_FILE_CSV_HDFS,
                                list_study_uid)

                print("Run script of HDFS")
                path_csv_uid = os.path.abspath(os.path.join(
                    settings.PATH_FILE_CSV_HDFS, settings.NAME_FILE_CSV_HDFS))
                path_data = os.path.abspath(settings.FS_PATH_STORAGE)
                aet_pacs = settings.SCP_AET
                print("path_script", path_csv_uid, path_data, aet_pacs, self.qr_level)
                if os.path.exists(settings.PATH_SCRIPT):
                    subprocess.call([settings.PATH_SCRIPT,
                                     path_csv_uid,
                                     path_data,
                                     aet_pacs,
                                     self.qr_level])
                else:
                    print("The path '%s' does not exist" % settings.PATH_SCRIPT)

            if self.stop:
                break

    # pylint: disable=missing-function-docstring
    def stop_thread(self):
        print("End thread HDFS")
        self.stop = True

    def __repr__(self):
        return "<Thread(name='%s')>" % self.name
