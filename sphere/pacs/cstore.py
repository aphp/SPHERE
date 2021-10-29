""" Store DICOM in PACS"""
import sys
import time
from time import sleep
from copy import deepcopy
from multiprocessing.pool import ThreadPool  # Process
from functools import partial

from pydicom import dcmread
from pynetdicom import _config

from sphere.fsa.file_system_access import FileSystemAccess
from sphere import settings
from sphere.pacs.associate import Associate
from sphere.logs.verbose import Verbose

from sphere.utilities.list_accessible_ae import auth_in
from sphere.utilities.dicom_utils import all_dicom_instance_path
from sphere.utilities.file import file_instance_date, read_file_return_list
from sphere.utilities.msg import execution_time
from sphere.utilities.log_tools import log_dataset
from sphere.fsa.dicom_path_cstore import DicomPathCStore
from sphere.logs.logs import LOG_EVENT_SPHERE, LOG_TRANSACTION

_config.DECODE_STORE_DATASETS = False


class CStore(Associate, Verbose):
    """
    Send DICOM instances to a PACS.
    Define Request action to SCP C-STORE.
    Define cecho Response from a c-store request
    included file access authorization
    """
    def __init__(self, ae, kwargs={}):
        super().__init__(ae, start=False, kwargs=kwargs)

        self.dicom_path_store = DicomPathCStore()
        self.action_dicom_code_name = 'CSTORE'

    def cstore_response(self, event):
        """
        Verification of authorized access and store a valid DICOM file

        :param event: The event
        :type event: :py:class:`pynetdicom.events.Event`
        :return: DICOM status hex code

            Success
              | ``0x0000`` - Success

            Failure
              | ``0xA801`` - Unauthorized access
              | ``0xC211`` - Method error
        :rtype: str
        """
        LOG_TRANSACTION.info('{:_^76}'.format('Start cstore_response'))
        self.ae.count_assoc = len(self.ae.active_associations)
        context = event.context

        # Log
        aec = event.assoc.requestor.ae_title.strip().decode("utf-8", "strict")
        LOG_EVENT_SPHERE.info("'%s' got a %s from '%s'",
                              self.ae.ae_title.decode("utf-8").strip(),
                              self.action_dicom_code_name, aec)

        dict_verbose = self.init_verbose(context=context, **{
            'action': self.action_dicom_code_name,
            'service': 'SCP',
            'log': 'Start cstore_response',
            'aec': aec})
        # End log

        ds = event.dataset  # pylint: disable=invalid-name

        # Log
        log_dataset(LOG_TRANSACTION, ds)
        self.create_verbose(dict_verbose, **{
            'study_uid': ds.StudyInstanceUID,
            'series_uid': ds.SeriesInstanceUID,
            'instance_uid': ds.SOPInstanceUID,
            'commit': False,
            'log': 'Get dicom with event.dataset'})
        # End log
        if settings.CREATE_FILE_UID:
            LOG_TRANSACTION.info("Create a file '%s' in a directory '%s' "
                                 "if not exists and add study_uid, series_uid "
                                 "and instance_uid", settings.FILE_NAME_UID,
                                 settings.LOG_PATH_FOLDER)
            file_instance_date(
                ds.StudyInstanceUID, ds.SeriesInstanceUID, ds.SOPInstanceUID,
                settings.FILE_NAME_UID, settings.LOG_PATH_FOLDER)

        # Log
        msg = 'Check Association'
        LOG_TRANSACTION.info(msg)
        self.create_verbose(dict_verbose, **{'log': msg})
        # End log

        # pylint: disable=no-else-return
        if auth_in(event, self.action_dicom_code_name):

            # log
            LOG_TRANSACTION.info(
                'Association Success and Start create FS Access')
            self.create_verbose(dict_verbose, **{
                'log': 'Association Success and Start create FS Access'})
            # End log

            # CREATE A FSA Access
            repeat_store = 1
            try:
                fsa = FileSystemAccess(
                    ds=ds, db_pacs=self.ae.db_pacs, context=context)
            except Exception as error:

                # log
                self.create_verbose(dict_verbose, **{
                    'success': False,
                    'log': 'Failed to create fs access',
                    'final_status': self.DICOM_CODE_CSTORE_METHOD_ERROR})
                LOG_TRANSACTION.exception(error)
                # End log

                return self.DICOM_CODE_CSTORE_METHOD_ERROR

            # log
            self.create_verbose(dict_verbose, **{
                'log': 'End FS Access Created and Storage of DICOM file'})
            # End log

            # FS STORE DICOM File
            try:
                fsa.store()
            except OSError as os_error:
                LOG_TRANSACTION.exception(os_error)
            except ValueError as value_error:
                LOG_TRANSACTION.warning("Restart store DCM SOPInstanceUID = %s",
                                        ds.SOPInstanceUID)
                repeat_store += 1
                if repeat_store <= 2:
                    fsa.store()
                else:
                    LOG_TRANSACTION.error("Error after restart store DCM "
                                          "SOPInstanceUID %s file not stored ",
                                          str(ds.SOPInstanceUID))
                    LOG_TRANSACTION.exception(value_error)
            except Exception as error:
                LOG_TRANSACTION.error(
                    'DCM SOPInstanceUID %s file not stored ',
                    str(ds.SOPInstanceUID))
                LOG_TRANSACTION.exception(error)
                # log
                self.create_verbose(dict_verbose, **{
                    'success': False,
                    'log': 'DCM file not stored',
                    'final_status': self.DICOM_CODE_CSTORE_METHOD_ERROR})
                # End log

                return self.DICOM_CODE_CSTORE_METHOD_ERROR

            # log
            LOG_TRANSACTION.info('DICOM File Stored in FS')
            self.create_verbose(dict_verbose, **{
                'log': 'DICOM File Stored in FS',
                'final_status': self.DICOM_CODE_SUCCESS})
            # End log
            LOG_TRANSACTION.info('{:_^76}'.format('End cstore_response'))
            return self.DICOM_CODE_SUCCESS
        else:
            # log
            LOG_TRANSACTION.error('Association Failed')
            self.create_verbose(dict_verbose, **{
                'success': False,
                'log': 'Association Failed',
                'final_status': self.DICOM_CODE_UNAUTHORIZED_ACCESS})
            # End log
            return self.DICOM_CODE_UNAUTHORIZED_ACCESS

    def cstore_request(self, kwargs):
        """
        Verification of authorized access and store a valid DICOM file

        :param kwargs: Parameters dictionary

        The list of parameters is:
            | source_paths_db_fs  : Source to have the paths

                The possible value:
                    - ``db`` database
                    - ``fs`` file system

            | model_name    : The model name (required if source_paths_db_fs = db)

                The possible value: ``patient``, ``study`` or ``series``

            | fileUID       : The path of the uid (required if source_paths_db_fs = db)
            | dicom_path    : The path of the dicom files (required if source_paths_db_fs = fs)
            | many_assoc    : Many or one assoc (True | False) [default: True] (optional)
            | verbose_level       : The verbose level default None (optional)

                list of possible value of verbose:
                    | ``0`` - quiet mode
                    | ``1`` - verbose mode
                    | ``0`` - ultra-verbose mode

        Example of kwargs:
            | {
            |   'source_paths_db_fs' : 'db',
            |   'model_name' : 'study', (if source_paths_db_fs = db)
            |   'fileUID'    : 'study_uid.uid', (if source_paths_db_fs = db)
            |   'dicom_path' : '/home/oac/PACS/PACS2/data/', (if source_paths_db_fs = fs)
            |   'many_assoc' : True
            |   'verbose'    : 1
            | }

        :type kwargs: dict
        """
        LOG_TRANSACTION.info('{:_^76}'.format('Start cstore_request'))
        many_assoc = kwargs.get('many_assoc')
        verbose_level = kwargs.get('verbose_level')
        source_paths_db_fs = kwargs.get('source_paths_db_fs')
        try:
            # Log
            LOG_EVENT_SPHERE.info("Launch the '%s' with '%s' and '%s' "
                                  "threads on '%s' with the DICOM files "
                                  "in '%s'",
                                  self.action_dicom_code_name,
                                  "Many associate" if many_assoc else
                                  "Only one associate",
                                  settings.NB_THREAD, self.aec,
                                  "database" if source_paths_db_fs == "db" else "directory")
            message_log = "Start cstore_request in %s in '%s' " % (
                "Many associate" if many_assoc else "Only one associate",
                "database" if source_paths_db_fs == "db" else "directory")
            # pylint: disable=attribute-defined-outside-init
            self.dict_verbose = self.init_verbose(
                verbose_level=verbose_level,
                **{
                    'aec_scu': self.aec,
                    'action': self.action_dicom_code_name,
                    'service': 'SCU',
                    'log': message_log})

            LOG_TRANSACTION.debug(message_log)
            # End Log
            start_time = time.time()
            if source_paths_db_fs == "db":
                LOG_TRANSACTION.info("Search the file path in the database "
                                     "and not in the file system")
                file_path = kwargs.get('file_path')
                model_name = kwargs.get('model_name')
                uid = kwargs.get("any_uid")
                if file_path:
                    LOG_TRANSACTION.info("Store with file Uid.")
                    list_uid = read_file_return_list(file_path)
                    LOG_TRANSACTION.debug("List uid : %s in this file '%s'",
                                          list_uid, file_path)
                    if not list_uid:
                        LOG_TRANSACTION.critical(
                            "This file '%s' is empty so not possible to "
                            "launch store", file_path)
                        sys.exit(-1)
                else:
                    LOG_TRANSACTION.info("Store only one Uid.")
                    list_uid = [uid]
                sleep_store = settings.SLEEP_IN_STORE
                # With sleep
                if sleep_store and list_uid and list_uid[0] != '*':
                    LOG_TRANSACTION.info("Store with sleep between each set "
                                         "of instances linked to uid")
                    # Send one by one with a sleep
                    for uid in list_uid:
                        list_instance_path = self.dicom_path_store.all_paths(
                            model_name, [uid])
                        LOG_TRANSACTION.info("I will send %s instances with "
                                             "Store", len(list_instance_path))
                        self.start_send(list_instance_path, many_assoc, uid)
                        if list_instance_path and uid != list_uid[-1]:
                            LOG_TRANSACTION.warning("sleep %s minutes of "
                                                    "store ", sleep_store/60)
                            sleep(sleep_store)
                        elif not list_instance_path:
                            LOG_TRANSACTION.error(
                                "The %s_uid '%s'  not exists in "
                                "database", model_name, uid)
                # Without sleep
                else:
                    LOG_TRANSACTION.info("Store without sleep")
                    list_instance_path = self.dicom_path_store.all_paths(
                        model_name, list_uid)
                    self.start_send(list_instance_path, many_assoc)

                    self.display_log(list_instance_path, source_paths_db_fs,
                                     file_path=file_path, model_name=model_name)

            else:  # file system
                LOG_TRANSACTION.info("Search the file path in the file system "
                                     "and not in the database")
                dicom_path = kwargs.get('dicom_path')
                list_instance_path = all_dicom_instance_path(dicom_path)
                self.display_log(list_instance_path, source_paths_db_fs,
                                 dicom_path=dicom_path)
                self.start_send(list_instance_path, many_assoc)

            total_store_time = execution_time(start_time)
            msg = f"Total store time: {total_store_time}"
            LOG_TRANSACTION.info(msg)
            print(msg)
        except Exception as error:
            LOG_TRANSACTION.exception(error)
        LOG_TRANSACTION.info('{:_^76}'.format('End cstore_request'))

    @staticmethod
    def display_log(list_instance_path, source_paths_db_fs,
                    file_path=None, model_name=None, dicom_path=None):
        """
        Display log

        :param list_instance_path: list instance path
        :type list_instance_path: list
        :param source_paths_db_fs: The source of path
        :type source_paths_db_fs: str

            The possible value:
                - ``db`` database
                - ``fs`` file system

        :param file_path: file path of uid
        :type file_path: str
        :param model_name: The model name
        :type model_name: str

            list of possible value:
                - ``patient``
                - ``study``
                - ``series``
                - ``instance``

        :param dicom_path: The path of the dicom folder
        :type dicom_path: str
        """
        if not list_instance_path:
            if source_paths_db_fs == "db":
                LOG_TRANSACTION.error("All %s_uid in file '%s' not exists "
                                      "in database", model_name, file_path)
            else:
                LOG_TRANSACTION.error("No valid DICOM or folder %s is empty ",
                                      dicom_path)
        else:
            LOG_TRANSACTION.info(
                "I will send %s instances",
                len(list_instance_path))

    def start_send(self, list_dicom_instance_path, many_assoc, uid=None):
        """
        Start the send of file DICOM

        :param list_dicom_instance_path: List all DICOM instance path
        :type list_dicom_instance_path: list
        :param many_assoc: If many associate (True) else only one (False)
        :type many_assoc: bool
        :param uid: The uid of (patient, study, series or instance) if used sleep in store
        :type uid: str
        """
        start_time = time.time()

        if uid:  # send one by one
            # Log
            copy_dict_verbose = deepcopy(self.dict_verbose)
            message_log = f'Send {len(list_dicom_instance_path)} files Dicom' \
                          f' with {settings.NB_THREAD} Thread of this {uid}'
            self.create_verbose(self.dict_verbose, **{'log': message_log})
            LOG_TRANSACTION.debug(message_log)
            # End log
        else:  # send all
            # Log
            copy_dict_verbose = deepcopy(self.dict_verbose)
            message_log = 'Send {0} files Dicom with {1} Thread'.format(
                len(list_dicom_instance_path), settings.NB_THREAD)
            self.create_verbose(self.dict_verbose, **{'log': message_log})
            LOG_TRANSACTION.debug(message_log)
            # End log

        thread_pool = ThreadPool(processes=settings.NB_THREAD)
        if not many_assoc:
            assoc = self.generate_new_association_from_aet()
        else:
            assoc = None
        send = partial(self.execute_send, assoc=assoc, many_assoc=many_assoc)
        thread_pool.map(send, list_dicom_instance_path)
        thread_pool.close()
        if not many_assoc:
            assoc.release()
        exec_time = execution_time(start_time)
        if uid:
            # Log
            self.create_verbose(copy_dict_verbose, **{
                'log': f'We have finished sending '
                       f'{len(list_dicom_instance_path)} '
                       f'dicom files of this uid {uid} \n# {exec_time}'})
            print(exec_time)
            LOG_TRANSACTION.info(exec_time)
            # End Log
        else:
            # Log
            self.create_verbose(copy_dict_verbose, **{
                'log': 'We have finished sending {0} dicom files \n# {1}'.
                                format(len(list_dicom_instance_path),
                                       exec_time)})
            # End Log

    def execute_send(self, dcmpath, assoc, many_assoc):
        """
        Execute send the DICOM (send_c_store)

        :param dcmpath: The path of a DICOM instance file
        :type dcmpath: str
        :param assoc: Associate
        :type assoc: :py:class:`pynetdicom.association.Association`
        :param many_assoc: If many associate (True) else only one (False)
        :type many_assoc: bool
        """
        try:
            dict_verbose = self.dict_verbose

            # Log
            self.create_verbose(
                dict_verbose, **{'log': 'Check or create Association'})
            # End log

            if many_assoc:
                assoc = self.generate_new_association_from_aet()

            if not assoc.is_established:
                assoc = self.generate_new_association_from_aet()

            if assoc.is_established:
                # Log
                self.create_verbose(dict_verbose, **{
                    'log': 'Association Success start reading the dicom '
                           'file %s ' % dcmpath})
                # End log

                # pylint: disable=invalid-name
                ds = dcmread(dcmpath, stop_before_pixels=False)

                # Log
                log_dataset(LOG_TRANSACTION, ds, dcmpath)
                self.create_verbose(dict_verbose, **{
                    'study_uid': ds.StudyInstanceUID,
                    'series_uid': ds.SeriesInstanceUID,
                    'instance_uid': ds.SOPInstanceUID,
                    'log': 'Read a DICOM file %s' % dcmpath})
                # End log

                # Log
                self.create_verbose(dict_verbose, **{
                    'log': 'Execute TCP Request (send dataset)'})
                # End log

                status = assoc.send_c_store(ds)

                # Check the status of the storage request
                if 'Status' in status:
                    # If the storage request succeeded this will be 0x0000
                    if '0x{0:04x}'.format(status.Status) != '0x0000':
                        print('C-STORE request status: 0x{0:04x}'.format(
                            status.Status))
                    if status.Status == 0xc211:
                        # Log
                        self.create_verbose(dict_verbose, **{
                            'success': False,
                            'final_status': self.DICOM_CODE_CSTORE_METHOD_ERROR}
                                            )
                        LOG_TRANSACTION.error(
                            "SC-STORE SCP implementation error")
                        # End log

                    else:
                        # Log
                        self.create_verbose(dict_verbose, **{
                            'final_status': self.DICOM_CODE_PENDING,
                            'success': False,
                            'log': 'TCP Request finalized'})
                        LOG_TRANSACTION.info(
                            "TCP Request finalized dicom_code: "
                            "0x{0:04x}".format(self.DICOM_CODE_PENDING))
                        # End log
                else:
                    # Log
                    self.create_verbose(
                        dict_verbose, **{'log': 'Status not in status'})
                    # End log
                    print('Connection timed out or invalid response from peer')

                if many_assoc:
                    # Release the association
                    assoc.release()
                    LOG_TRANSACTION.debug("Release the association")
            else:
                # Log
                self.create_verbose(dict_verbose, **{
                    'success': False,
                    'final_status': self.DICOM_CODE_ASSOC_REJECTED_ABORTED,
                    'log': 'Failed to etablish access'})
                LOG_TRANSACTION.error("Release the association and this file "
                                      "%s not send", dcmpath)
                # End log
        except ValueError:
            LOG_TRANSACTION.error("This file %s not send.", dcmpath)
        except Exception as exc:
            LOG_TRANSACTION.exception("This file %s not send. \n %s",
                                      dcmpath, exc)
