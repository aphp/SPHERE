"""
Move DICOM in PACS
"""
# pylint: disable=invalid-name
import os
import sys
import time
from time import sleep
from functools import partial
from multiprocessing.pool import ThreadPool  # Process
from copy import copy, deepcopy
import threading

from pydicom import dcmread
from pydicom.errors import InvalidDicomError
from pynetdicom.sop_class import (
    PatientRootQueryRetrieveInformationModelMove,
    StudyRootQueryRetrieveInformationModelMove)

from sphere import settings
from sphere.fsa.dicom_path_cmove import DicomPathCMove
from sphere.utilities.list_accessible_ae import list_all_access_list
from sphere.pacs.associate import Associate
from sphere.utilities.list_accessible_ae import auth_in
from sphere.logs.verbose import Verbose
from sphere.utilities.msg import execution_time
from sphere.utilities.string_tools import hard_disk_size
from sphere.utilities.log_tools import log_dataset
from sphere.logs.logs import LOG_EVENT_SPHERE, LOG_TRANSACTION
# HDFS
from sphere.fsa.thread_hdfs import ThreadHdfs, g_queue_hdfs
from sphere.utilities.dicom_utils import get_uid, check_exists_file


class CMove(Associate, Verbose):
    """
    Move DICOM files from one PACS to another
    """
    def __init__(self, ae, kwargs={}):
        super().__init__(ae, kwargs=kwargs)
        self.action_dicom_code_name = 'CMOVE'
        self.dicom_path_move = DicomPathCMove()
        self.move_aet = str()
        self.dict_verbose = type(None)()

    def satrt_cmove_hdfs(self, ds, qr_level):
        """
        Start cmove with HDFS

        :param ds: The dataset
        :type ds: :py:class:`pydicom.dataset.Dataset`
        :param qr_level: The query level

                    The possible value: ``PATIENT``, ``STUDY`` or ``SERIES``

        :type qr_level: str
        """
        total, used, free = hard_disk_size()
        if settings.FREE_HARD_DRIVE > free:
            LOG_TRANSACTION.critical(
                "There is no minimum (%s Go) space to launch "
                "cmove with HDFS Hard disk size; total = %s Go, "
                "used = %s Go,  free = %s GO",
                settings.FREE_HARD_DRIVE, total, used, free)
            sys.exit()
        # Get study_uid or series_uid and put the in g_queue_hdfs
        uid = get_uid(ds)
        g_queue_hdfs.put(uid)
        # Check and start thread hdfs
        if 'thread_hdfs' not in [thread.name for thread in
                                 threading.enumerate()]:
            self.thread_hdfs = ThreadHdfs('thread_hdfs', qr_level)
            self.thread_hdfs.start()

        sleep(settings.TIME_SLEEP_HDFS)
        print("lance cmove normale")

    def end_cmove_hdfs(self, matching, thread_pool):
        """
         Check path and send instance

        :param matching: Dicom file path list
        :type matching: list
        :param thread_pool: multiprocessing
        :type thread_pool: :py:class:`multiprocessing.pool.ThreadPool`
        """
        paths_not_exists = []
        paths_exists = []
        all_path = matching

        check_exists_file(all_path, paths_exists, paths_not_exists)
        all_path = copy(paths_not_exists)
        paths_not_exists.clear()

        if paths_exists:
            thread_pool.map(self.execute_send, paths_exists)
            paths_exists.clear()

        count_paths_not_exits = []
        while all_path:
            check_exists_file(all_path, paths_exists, paths_not_exists)
            all_path = copy(paths_not_exists)
            paths_not_exists.clear()

            if paths_exists:
                thread_pool.map(self.execute_send, paths_exists)
                paths_exists.clear()

            # check if there are paths exists in the database but
            # the file does not exist in HDFS
            count_paths_not_exits.append(len(all_path))
            if len(set(count_paths_not_exits)) > 1:
                count_paths_not_exits.clear()
            # if for 4 times the len of count_paths_not_exits does not change
            elif len(count_paths_not_exits) > 4 and len(
                    set(count_paths_not_exits)) == 1:
                sleep(60)
            # if for 10 times the len of count_paths_not_exits does not change
            elif len(count_paths_not_exits) > 10 and len(
                    set(count_paths_not_exits)) == 1:
                LOG_TRANSACTION.warning("There are %s files that does "
                                        "not exist in HDFS. \n"
                                        "List of path :",
                                        len(all_path))
                for path in all_path:
                    LOG_TRANSACTION.warning(path)

        if 'thread_hdfs' in [thread.name for thread in threading.enumerate()] \
                and self.thread_hdfs.queue.qsize() == 0:
            self.thread_hdfs.stop_thread()

    def cmove_response(self, event):
        """
        Response of Cmove

        :param event: Event
        :type event: :py:class:`pynetdicom.events.Event`
        :return: DICOM status hex code

            Success
              | ``0xFF00`` - Success Cmove

            Failure
              | ``0xC000`` - QueryRetrieveLevel not in ds
              | ``0xA801`` - Association aborted

        :rtype: str
        """
        # Log
        LOG_TRANSACTION.info('{:_^76}'.format('Start cmove_response'))
        aec = event.assoc.requestor.ae_title.strip().decode("utf-8", "strict")
        LOG_EVENT_SPHERE.info("'%s' got a %s from '%s'",
                              self.ae.ae_title.decode("utf-8").strip(),
                              self.action_dicom_code_name, aec)

        message_log = "Start cmove_response and Check Association"
        LOG_TRANSACTION.debug(message_log)
        self.dict_verbose = self.init_verbose(**{
            'aec': aec,
            'action': self.action_dicom_code_name,
            'service': 'SCP',
            'log': message_log})
        dataset_dict_verbose = deepcopy(self.dict_verbose)
        # End Log

        ds = event.identifier

        # log
        self.create_verbose(dataset_dict_verbose, **{
            'log': 'The data to search ', 'dataset': ds})
        LOG_TRANSACTION.debug("The data to search in a dataset ds =")
        for line in ds:
            LOG_TRANSACTION.debug(line)
        # End log

        if auth_in(event, self.action_dicom_code_name):
            # log
            message_log = 'Association Success'
            LOG_TRANSACTION.info(message_log)
            self.create_verbose(self.dict_verbose, **{'log': message_log})
            # End log

            if 'QueryRetrieveLevel' not in ds:
                # log
                message_log = 'QueryRetrieveLevel not in ds'
                LOG_TRANSACTION.error(message_log)
                self.create_verbose(self.dict_verbose, **{'log': message_log,
                                                          'success': False})
                # End log

                # Failure
                yield 0xC000, None
                return

            # Check move_aet is known
            # get_known_aet() is here to represent a user-implemented method of
            #   getting known AEs
            # known_aet_dict = get_known_aet()

            list_allowed_pacs = list_all_access_list()
            LOG_TRANSACTION.debug("list_allowed_pacs %s ",
                                  list_allowed_pacs)
            LOG_TRANSACTION.debug("event.request.__dict__ = %s ",
                                  event.request.__dict__)
            # pylint: disable=protected-access
            self.move_aet = \
                event.request._move_destination.strip().decode('utf-8')
            print("move_aet =  {0}".format(self.move_aet))
            LOG_TRANSACTION.debug("move_aet = %s ", self.move_aet)
            if self.move_aet not in list_allowed_pacs.keys():
                # Unknown destination AE
                # log
                message_log = 'Unknown destination AE ds; {0} not in this ' \
                              'list {1}'.format(self.move_aet,
                                                list_allowed_pacs.keys())
                LOG_TRANSACTION.error(message_log)
                self.create_verbose(self.dict_verbose, **{'log': message_log,
                                                          'success': False})
                # End log
                yield (None, None)
                return

            target = list_allowed_pacs[self.move_aet]
            LOG_TRANSACTION.debug("target of cmove= %s ", target)
            (addr, port) = (target['ip'], target['port'])  # target['port'])

            # Yield the IP address and listen port of the destination AE
            yield (addr, port)
            qr_level = ds.QueryRetrieveLevel.upper()
            LOG_TRANSACTION.debug("Start dicom_path_move")

            matching = self.dicom_path_move.path_found(ds, qr_level)
            if len(matching):
                print('The number of instances equals to : ' + str(len(matching)))
                if settings.START_MOVE_HDFS:
                    self.satrt_cmove_hdfs(ds, qr_level)

                yield len(matching)

                thread_pool = ThreadPool(processes=settings.NB_THREAD)
                # Log
                message_log = 'Send {0} path of instances with {1} Thread'.format(
                    len(matching), settings.NB_THREAD)
                self.create_verbose(self.dict_verbose, **{'log': message_log})
                LOG_TRANSACTION.debug(message_log)
                # End log
                if settings.START_MOVE_HDFS:
                    self.end_cmove_hdfs(matching, thread_pool)
                elif settings.PENDING_RESPONSES_MOVE:  # Pending
                    for dicom_file_path in matching:
                        ds = self.execute_send(dicom_file_path)
                        yield 0xFF00, ds
                else:  # No Pending
                    thread_pool.map(self.execute_send, matching)

                thread_pool.close()
                LOG_TRANSACTION.info('{:_^76}'.format('End cmove_response'))
            else:
                LOG_TRANSACTION.critical("Matching is empty")
                yield 0
        else:
            # Log
            message_log = "Association rejected or aborted"
            self.create_verbose(self.dict_verbose, **{
                'success': False,
                'final_status': self.DICOM_CODE_ASSOCIATION_ABORTED,
                "log": message_log})
            LOG_TRANSACTION.error(message_log)
            # End log

            return self.DICOM_CODE_ASSOCIATION_ABORTED

    def execute_send(self, dicom_file_path):
        """
        Send the DICOM file to another PACS

        :param dicom_file_path: The path of a dicom file
        :type dicom_file_path: str
        """
        assoc = self.generate_new_association_from_aet(self.move_aet)
        if assoc.is_established:
            try:
                try:
                    ds = dcmread(dicom_file_path)
                    # Log
                    message_log = "Read the dicom file '%s' and send the " \
                                  "dataset DICOM  with 'send_c_store' to %s " \
                                  % (dicom_file_path, self.move_aet)
                    self.create_verbose(self.dict_verbose, **{
                        'study_uid': ds.StudyInstanceUID,
                        'series_uid': ds.SeriesInstanceUID,
                        'instance_uid': ds.SOPInstanceUID,
                        'commit': False,
                        'log': message_log})
                    LOG_TRANSACTION.debug(message_log)
                    log_dataset(LOG_TRANSACTION, ds, dicom_file_path)
                    # End log

                    status = assoc.send_c_store(ds)
                    if 'Status' in status:
                        # If the storage request succeeded this will be 0x0000
                        print('C-STORE request status: 0x{0:04x}'.format(
                            status.Status))
                        if status.Status == 0xc211:
                            # Log
                            message_log = 'Unhandled exception raised by the ' \
                                          'handler bound to evt.EVT_C_STORE'
                            self.create_verbose(self.dict_verbose, **{
                                'success': False,
                                "log": message_log})
                            LOG_TRANSACTION.error(message_log)
                            # End log
                            assoc.release()
                            print("Error: 0xc211")
                        if status.Status == 0x0000:
                            assoc.release()
                            if settings.START_MOVE_HDFS and settings.REMOVE_FILE:
                                os.remove(dicom_file_path)
                            if settings.PENDING_RESPONSES_MOVE and not settings.START_MOVE_HDFS:  # Pending
                                return ds

                    else:
                        # Log
                        message_log = 'Connection timed out or invalid ' \
                                      'response from peer'
                        self.create_verbose(self.dict_verbose, **{
                            'success': False,
                            "log": message_log})
                        LOG_TRANSACTION.error(message_log)
                        # End log
                    assoc.release()
                except InvalidDicomError as error:
                    # Log
                    message_log = "'%s'1 is not a DICOM regular file" % dicom_file_path
                    LOG_TRANSACTION.error(error)
                    LOG_TRANSACTION.error(message_log)
                    self.create_verbose(self.dict_verbose, **{
                        'success': False,
                        "log": message_log})
                    # End log
                    assoc.release()
                except Exception as error:
                    LOG_TRANSACTION.exception(error)
                    assoc.release()
            except FileNotFoundError:
                print('\n\tSorry, \'', dicom_file_path, '\' not found.\n')
                # Log
                message_log = " This file '%s' not found." % dicom_file_path
                self.create_verbose(self.dict_verbose, **{
                    'success': False,
                    "log": message_log})
                LOG_TRANSACTION.error(message_log)
                # End log
                assoc.release()
        else:
            print('Association rejected or aborted')
            # Log
            message_log = "Association rejected or aborted"
            self.create_verbose(self.dict_verbose, **{
                'success': False,
                'final_status': self.DICOM_CODE_ASSOCIATION_ABORTED,
                "log": message_log})
            LOG_TRANSACTION.error(message_log)
            # End log

    def execute_move(self, ds, ae_cstore, query_model):
        """
        Execute send_c_move

        :param ds: The dataset
        :type ds: :py:class:`pydicom.dataset.Dataset`
        :param ae_cstore: Application Entity to send CSTORE (AE)
        :type ae_cstore: str
        :param query_model: The Information Model

            The possible value to return:
                | - ``P``
                | - ``S``

        :type query_model:
        """
        # Log
        self.create_verbose(
            self.dict_verbose, **{'log': 'Check or create Association'})
        dataset_dict_verbose = deepcopy(self.dict_verbose)
        # End log

        assoc = self.generate_new_association_from_aet()
        if assoc.is_established:
            # Use the C-MOVE service to send the identifier
            # A query_model value of 'P' means use the 'Patient Root Query
            #   Retrieve Information Model - Move' presentation context
            # Log
            LOG_TRANSACTION.debug('ds =')
            for line in ds:
                LOG_TRANSACTION.debug(line)

            self.create_verbose(dataset_dict_verbose, **{
                'log': 'Association Success and start send a DICOM ds = ',
                'dataset': ds})
            # End log
            ae_cstore = bytes(ae_cstore, 'utf-8')  # Convert string to bytes
            responses = assoc.send_c_move(ds, ae_cstore,
                                          query_model=query_model)
            try:
                for (status, identifier) in responses:
                    print(
                        'C-MOVE query status: 0x{0:04x}'.format(status.Status))

                    # If the status is 'Pending' then the identifier is
                    # the C-MOVE response
                    if status.Status in (0xFF00, 0xFF01):
                        print(identifier)
            except AttributeError:
                # Log
                msg = 'Dataset object has no attribute Status; dataset is empty'
                self.create_verbose(self.dict_verbose, **{
                    'log': msg, 'success': False})
                LOG_TRANSACTION.error(msg)
                # End log
                print(
                    'Error: Dataset object has no attribute Status; '
                    'dataset is empty')
            else:
                # Release the association
                self.assoc.release()
                #assoc.release()
        else:
            # Log
            msg = 'Association rejected or aborted'
            self.create_verbose(self.dict_verbose, **{
                'log': msg, 'success': False})
            LOG_TRANSACTION.error(msg)
            # End log

            assoc.release()
            print('Association rejected or aborted')
            self.execute_move(ds, ae_cstore, query_model)

    def cmove_request(self, **kwargs):
        """
        The c-move resquest

        :param kwargs: Parameters dictionary

            The list of parameters is:

                | list_ds            : List of the dataset
                | ae_cstore        : Application Entity to send CSTORE (AE)
                | query_model            : query model

                    The possible value to return:
                        | - ``P``
                        | - ``S``

                | file_uid          : Output file path
                | verbose_level            : The verbose_level

                    list of possible value of verbose_level:
                        | ``0`` - quiet mode
                        | ``1`` - verbose mode
                        | ``0`` - ultra-verbose mode

            Example of kwargs:
                | {
                |   'list_ds' : [(0008, 0052) Query/Retrieve Level   CS: 'STUDY'
                |               (0020, 000e) Series Instance UID    UI: \* ]
                |   'ae_cstore'    : 'PACS3',
                |   'query_model'        : 'S',
                |   'file_uid'      : 'log/study_uid',
                |   'verbose_level'       : 1
                | }

        :type kwargs: dict
        """
        # self.start_send(list_ds, ae_cstore, query_model, verbose_level)
        list_ds = kwargs.get('list_ds')
        ae_cstore = kwargs.get('ae_cstore')
        query_model = kwargs.get('query_model')
        # Log
        LOG_TRANSACTION.info('{:_^76}'.format('Start cmove_request'))
        LOG_EVENT_SPHERE.info("Launch the %s on %s ",
                              self.action_dicom_code_name, self.aec)
        if not list_ds:
            LOG_TRANSACTION.critical("This '%s' file is empty. "
                                     "So we can't start cmove",
                                     kwargs.get('file_uid'))
            self.assoc.release()
            sys.exit()
        message_log = "Start cmove_request and Check Association"
        LOG_TRANSACTION.info(message_log)
        self.dict_verbose = self.init_verbose(
            verbose_level=kwargs.get('verbose_level'),
            **{
                'aec_scu': self.aec,
                'action': self.action_dicom_code_name,
                'service': 'SCU',
                'log': message_log})
        # End Log
        if query_model == "S":
            query_model = StudyRootQueryRetrieveInformationModelMove
        elif query_model == "P":
            query_model = PatientRootQueryRetrieveInformationModelMove

        start_time = time.time()
        po = ThreadPool(processes=settings.NB_THREAD)
        send = partial(
            self.execute_move, ae_cstore=ae_cstore, query_model=query_model)

        # Log
        message_log = 'Send {0} {1}_UID with {2} Thread'.format(
            len(list_ds), "PATIENT" if query_model == "P" else "STUDY",
            settings.NB_THREAD)
        self.create_verbose(self.dict_verbose, **{'log': message_log})
        LOG_TRANSACTION.debug(message_log)
        # End log

        po.map(send, list_ds)
        # Release the association
        self.assoc.release()
        print(execution_time(start_time))
        # Log
        self.create_verbose(self.dict_verbose, **{
            'log': 'We have finished sending {0} {1}_UID  \n# in {2}'.format(
                len(list_ds), "PATIENT" if query_model == "P" else "STUDY",
                execution_time(start_time))})
        LOG_TRANSACTION.info('{:_^76}'.format('End cmove_request'))
        LOG_TRANSACTION.info(execution_time(start_time))
        # End Log
