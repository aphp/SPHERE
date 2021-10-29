import threading
import queue
from time import sleep

from sphere import settings
from sphere.utilities.msg import term_bold, term_green, term_red
from sphere.fsa.file_system_access import FileSystemAccess
from sphere.logs.logs import LOG_DATABASE


class QueueGlobal:
    """Define a global object """
    def __init__(self):
        self.g_queue_to_load = queue.Queue()


queue_global = QueueGlobal()
g_queue_to_load = queue_global.g_queue_to_load


class ThreadDatabase(threading.Thread):

    """ Save data in database with Thread"""
    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.counter = counter
        self.state = term_bold(term_red('OFF'))
        self.stop = False
        self.fsa = FileSystemAccess()
        self.queue = g_queue_to_load

    def run(self):
        print("Starting " + self.name)
        self.state = term_bold(term_green('ON'))
        while True:
            print('=========== SIZE QUEUE %s : %s' % (settings.SCP_AET,
                                                      self.queue.qsize()))
            try:
                if not self.queue.empty():
                    self.fsa.insert_data.bulk_insert_from_queue(self.queue)
                elif self.stop:
                    break
                elif self.queue.empty():
                    print("I'm waiting for the data to be saved in the database")
            except Exception as exc:
                try:
                    LOG_DATABASE.exception(exc)
                    LOG_DATABASE.warning("The number of instances is not "
                                         "saved in the database equal %s",
                                         self.fsa.insert_data.number_insert)
                except Exception as exc:
                    print(exc)

            sleep(settings.DB_SAVE_DELAY)
        print("Exiting " + self.name)
        self.state = term_bold(term_red('OFF'))

    def stop_thread(self):
        self.stop = True

    def __repr__(self):
        return "<Thread(thread_id='%s', name='%s'," \
               "counter='%s')>" % (self.thread_id, self.name, self.counter)
