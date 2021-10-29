"""
C-FIND is the operation by which relevant patient information is queried
and provided.
"""
# pylint: disable=invalid-name, too-many-branches
import os
from copy import deepcopy

from pynetdicom.sop_class import(
                PatientRootQueryRetrieveInformationModelFind,
                StudyRootQueryRetrieveInformationModelFind)

from sphere.pacs.associate import Associate
from sphere.utilities.list_accessible_ae import auth_in
from sphere.utilities.file import create_file_txt
from sphere.fsa.dicom_dataset_cfind import DicomDatasetCFind
from sphere.logs.verbose import Verbose
from sphere import settings
from sphere.logs.logs import LOG_EVENT_SPHERE, LOG_TRANSACTION


class CFind(Associate, Verbose):
    """ Search DICOM in database and in directory"""

    def __init__(self, ae, kwargs={}):
        super().__init__(ae, kwargs=kwargs)
        self.action_dicom_code_name = 'CFIND'

        self.dicom_dataset_find = DicomDatasetCFind()

        self.search_in_files = settings.SEARCH_FILE

    def cfind_response(self, event):
        """
        Response of cfind

        :param event: event
        :type event: :py:class:`pynetdicom.events.Event`
        :return: DICOM status hex code

            Success
              | ``0xFF00`` - Success Cmove

            Failure
              | ``0xFE00`` -
              | ``0xC000`` - QueryRetrieveLevel not in ds
              | ``0xA801`` - Association aborted
        :rtype: str
        """
        # Log
        LOG_TRANSACTION.info('{:_^76}'.format('Start cfind_response'))
        aec = event.assoc.requestor.ae_title.strip().decode("utf-8", "strict")
        LOG_EVENT_SPHERE.info("'%s' got a %s from '%s'",
                              self.ae.ae_title.decode("utf-8").strip(),
                              self.action_dicom_code_name, aec)

        message_log = "Start cfind_response and Check Association"
        LOG_TRANSACTION.debug(message_log)
        dict_verbose = self.init_verbose(**{
            'aec': aec,
            'action': self.action_dicom_code_name,
            'service': 'SCP',
            'log': message_log})
        dataset_dict_verbose = deepcopy(dict_verbose)
        # End Log

        ds = event.identifier
        print(ds)
        # log
        self.create_verbose(dataset_dict_verbose, **{
            'log': 'The data to search ', 'dataset': ds})

        LOG_TRANSACTION.debug('{:*^70}'.format('THE DATA SEARCHED IN THE '
                                               'DATABASE; DATASET EQUAL:'))
        for line in ds:
            LOG_TRANSACTION.debug(line)
        LOG_TRANSACTION.debug('{:*^70}'.format(' END DATASET '))
        # End log

        if auth_in(event, self.action_dicom_code_name):

            # log
            message_log = 'Association Success'
            LOG_TRANSACTION.info(message_log)
            self.create_verbose(dict_verbose, **{'log': message_log})
            # End log

            if 'QueryRetrieveLevel' not in ds:
                # Failure

                # log
                message_log = 'QueryRetrieveLevel not in ds'
                LOG_TRANSACTION.error(message_log)
                self.create_verbose(dict_verbose, **{'log': message_log,
                                                     'success': False})
                # End log

                yield 0xC000, None
                return
            qr_level = ds.QueryRetrieveLevel.upper()
            try:
                LOG_TRANSACTION.debug("Start dicom_dataset_find")
                matching = self.dicom_dataset_find.ds_found(
                    ds, qr_level, self.search_in_files)

                # log
                self.create_verbose(dict_verbose, **{
                    'log': "Number of %s is %s" % (qr_level, len(matching))})
                # End log

                if matching:  # matching not empty
                    for identifier in matching:

                        # log
                        self.create_verbose(dict_verbose, **{
                            'log': "Check if C-CANCEL has been received"})
                        LOG_TRANSACTION.debug(
                            "Check if C-CANCEL has been received")
                        # End log

                        # Check if C-CANCEL has been received
                        if event.is_cancelled:

                            # log
                            self.create_verbose(dict_verbose, **{
                                'log': " error: C-CANCEL has been received"})
                            LOG_TRANSACTION.error(
                                "C-CANCEL has been received")
                            # End log

                            yield (0xFE00, None)
                            return

                        # log
                        self.create_verbose(dataset_dict_verbose, **{
                            'log': 'C-CANCEL has not been received; '
                                   'Pending dataset ', 'dataset': identifier})
                        LOG_TRANSACTION.debug(
                            '{:*^70}'.format("C-CANCEL HAS NOT BEEN RECEVIED; "
                                             "PENDING DATASET; DATASET EQUAL:"))
                        for line in identifier:
                            LOG_TRANSACTION.debug(line)
                        LOG_TRANSACTION.debug('{:*^70}'.format(' END DATASET '))
                        # End log

                        # Pending
                        yield (0xFF00, identifier)
                    LOG_TRANSACTION.info(
                        '{:_^76}'.format('End cfind_response'))
                else:  # matching is empty
                    # Log
                    message_log = 'matching is empty'
                    self.create_verbose(dict_verbose, **{
                        'success': False,
                        'log': message_log})
                    LOG_TRANSACTION.error(message_log)
                    # End log

                yield self.DICOM_CODE_SUCCESS, None
                return
            except Exception as error:
                # Log
                self.create_verbose(dict_verbose, commit=True, **{
                    'success': False,
                    "log": "Error: {0}".format(error)})
                LOG_TRANSACTION.critical(error)
                # End log
        else:
            # Log
            message_log = "Association rejected or aborted"
            self.create_verbose(dict_verbose, **{
                'success': False,
                'final_status': self.DICOM_CODE_ASSOCIATION_ABORTED,
                "log": message_log})
            LOG_TRANSACTION.error(message_log)
            LOG_TRANSACTION.info('{:_^76}'.format('End cfind_response'))
            # End log

            return self.DICOM_CODE_ASSOCIATION_ABORTED

    def prepare_list_uid(self, path, file_name, identifiers, query_model):
        """
        Prepare and Create a list file of PatientID, SeriesInstanceUID or
        StudyInstanceUID

        :param path: Output file path
        :type path: str
        :param file_name: file name
        :type file_name: str
        :param identifiers: List of dataset
        :type identifiers: list [:py:class:`pydicom.dataset.Dataset`]
        :param query_model: the query model

            The possible value to return:
                | - ``P``
                | - ``S``
                | - ``SE``

        :type query_model: str
        """
        lists = []
        for identifier in identifiers:
            if query_model == "S":
                query_retrieve_level = "STUDY"
                if identifier.StudyInstanceUID not in lists:
                    lists.append(identifier.StudyInstanceUID)
            elif query_model == "P":
                query_retrieve_level = "PATIENT"
                if identifier.PatientID not in lists:
                    lists.append(identifier.PatientID)
            elif query_model == "SE":
                query_retrieve_level = "SERIES"
                if identifier.SeriesInstanceUID not in lists:
                    lists.append(identifier.SeriesInstanceUID)

        if lists:
            create_file_txt(path, file_name, lists)
            LOG_TRANSACTION.debug(
                "We created a file '%s' which contains all the uid %s",
                os.path.join(path, file_name), query_retrieve_level)
        else:
            LOG_TRANSACTION.error(
                'Not possible to produce study_uid or patient_id '
                'or series_uid')

    def cfind_request(self, **kwargs):
        """
        Create request cfind

        :param kwargs: Parameters dictionary

            The list of parameters is:

                | ds            : The dataset
                | query_retrieve_level        : The query retrieve level
                    list of possible value of query_retrieve_level:
                        | - ``PATIENT``
                        | - ``STUDY``
                        | - ``SERIES``
                | query_model            : query model
                    The possible value to return:
                        - ``P``
                        - ``S``
                        - ``SE``
                | file_path          : Output file path
                | overwrite          : overwrite file uid if exists
                | display_ds         : display dataset if True
                | verbose_level            : The verbose_level
                    list of possible value of verbose_level:
                        - ``0`` quiet mode
                        - ``1`` verbose mode
                        - ``0`` ultra-verbose mode

            Example of kwargs:
                | {
                |   'ds'      : (0008, 0052) Query/Retrieve Level   CS: 'STUDY'
                |               (0020, 000e) Series Instance UID    UI: *
                |   'query_retrieve_level'    : 'STUDY',
                |   'query_model'        : 'S',
                |   'file_path'      : 'log/study_uid',
                |   'overwrite'      : True
                |   'verbose_level'       : 1
                | }

        :type kwargs: dict
        """
        LOG_TRANSACTION.info('{:_^76}'.format('Start cfind_request'))
        query_model = kwargs.get('query_model')
        file_path = kwargs.get('file_path')
        ds = kwargs.get('ds')

        # Log
        LOG_EVENT_SPHERE.info("Launch the %s on %s ",
                              self.action_dicom_code_name, self.aec)
        message_log = "Start cfind_request and Check Association"
        LOG_TRANSACTION.debug(message_log)
        dict_verbose = self.init_verbose(
            verbose_level=kwargs.get('verbose_level'),
            **{
                'aec_scu': self.aec,
                'action': self.action_dicom_code_name,
                'service': 'SCU',
                'log': message_log})
        dataset_dict_verbose = deepcopy(dict_verbose)
        # End Log

        identifiers = []  # list of identifiers
        if self.assoc.is_established:
            # Use the C-FIND service to send the identifier
            # A query_model value of 'P' means use the
            # 'Patient Root Query Retrieve Information Model - Find'
            # presentation context
            if query_model == "SE":
                query_m = query_model
                query_model = "S"
            else:
                query_m = query_model

            if query_model == "S":
                query_model = StudyRootQueryRetrieveInformationModelFind
            elif query_model == "P":
                query_model = PatientRootQueryRetrieveInformationModelFind

            # Log
            LOG_TRANSACTION.info('Association Success and execute '
                                 'TCP Request; send find')

            LOG_TRANSACTION.debug('{:*^70}'.format(' REQUEST DATASET '))
            for line in ds:
                LOG_TRANSACTION.debug(line)
            LOG_TRANSACTION.debug('{:*^70}'.format(' END REQUEST DATASET '))

            self.create_verbose(dataset_dict_verbose, **{
                'log': 'Association Success and execute TCP Request; '
                       'send find  ds = ',
                'dataset': ds})
            # End log

            responses = self.assoc.send_c_find(ds, query_model=query_model)

            # Log
            self.create_verbose(
                dict_verbose, **{'log': 'TCP Request finalized'})
            LOG_TRANSACTION.info('TCP Request finalized and you find the '
                                 'result of cfind')
            # End log

            try:
                for (status, identifier) in responses:
                    if status:
                        # Log
                        message_log = 'C-FIND query status: 0x{0:04x}'.format(
                            status.Status)
                        LOG_TRANSACTION.info(message_log)
                        # End log

                        # If the status is 'Pending' then identifier is
                        # the C-FIND response
                        if status.Status in (0xFF00, 0xFF01):
                            # Log
                            LOG_TRANSACTION.debug(
                                '{:*^70}'.format(' RESULT DATASET '))
                            LOG_TRANSACTION.debug('identifier = ')
                            # copy_dict_log = deepcopy(dict_log)
                            display_ds = kwargs.get('display_ds')
                            for line in identifier:
                                if display_ds:
                                    print(line)
                                LOG_TRANSACTION.debug(line)
                            if display_ds:
                                print("*" * 100)
                            LOG_TRANSACTION.debug(
                                '{:*^70}'.format(' END RESULT DATASET '))
                            self.create_verbose(dataset_dict_verbose, **{
                                'log': message_log,
                                'dataset': identifier})
                            # End log

                            identifiers.append(identifier)
                        elif status.Status == 0x0000:
                            LOG_TRANSACTION.info(
                                'End cfind C-FIND query status: 0x0000')
                        else:
                            LOG_TRANSACTION.error(
                                'C-FIND query status: 0x{0:04x}'.format(
                                    status.Status))
                    else:
                        # Log
                        message = 'Connection timed out, was aborted or ' \
                                  'received invalid response'
                        self.create_verbose(dict_verbose,
                                            **{'log': message}, commit=True)
                        LOG_TRANSACTION.error(message)
                        # End log
                # Log
                message = "Equal number of %s is %s" % (
                    kwargs.get('query_retrieve_level'), len(identifiers))
                self.create_verbose(
                    dict_verbose, **{'log': message}, commit=True)
                LOG_TRANSACTION.debug(message)
                # End log

                if file_path:
                    if "/" in file_path:
                        file_name = os.path.basename(file_path)
                        path = os.path.dirname(file_path)
                    else:
                        file_name = file_path
                        path = "."
                    if os.path.isdir(path):
                        overwrite = kwargs.get('overwrite')
                        if not os.path.exists(file_name) or overwrite:
                            self.prepare_list_uid(
                                path, file_name, identifiers, query_m)
                        else:
                            LOG_TRANSACTION.error(
                                "A file name '%s' exists", file_name)
                            new_file_name = input('The new file name:')
                            self.prepare_list_uid(
                                path, new_file_name, identifiers, query_m)
                    else:
                        LOG_TRANSACTION.error(
                            "The specified path does not exist '%s'", path)
            except AttributeError:
                # Log
                message = "Dataset object has no attribute Status"
                self.create_verbose(
                    dict_verbose, **{'log': message}, commit=True)
                LOG_TRANSACTION.error(message)
                # End log
            else:
                # Release the association
                self.assoc.release()
        else:
            # Log
            message = 'Association rejected, aborted or never connected'
            self.create_verbose(dict_verbose, **{'log': message}, commit=True)
            LOG_TRANSACTION.critical(message)
            # End log
        LOG_TRANSACTION.info('{:_^76}'.format('End cfind_request'))
