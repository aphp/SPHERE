"""
Define Application Entity as extension from pynetdicom AE
"""
# pylint: disable=no-name-in-module, misplaced-comparison-constant, invalid-name

import copy

from pynetdicom import AE, evt
from pynetdicom import _config
from pynetdicom import StoragePresentationContexts
from pynetdicom.sop_class import (
    VerificationSOPClass,
    PatientRootQueryRetrieveInformationModelFind,
    StudyRootQueryRetrieveInformationModelFind,
    PatientRootQueryRetrieveInformationModelMove,
    StudyRootQueryRetrieveInformationModelMove,
    ModalityWorklistInformationFind)
from pydicom.uid import (
    DeflatedExplicitVRLittleEndian, JPEGBaseline, JPEGExtended,
    JPEGLosslessP14, JPEGLossless, JPEGLSLossless, JPEGLSLossy,
    JPEG2000Lossless, JPEG2000, JPEG2000MultiComponentLossless,
    JPEG2000MultiComponent, RLELossless
)

from sphere.pacs.cecho import CEcho
from sphere.pacs.cstore import CStore
from sphere.pacs.cfind import CFind
from sphere.pacs.cmove import CMove
from sphere.dicmeta.database_pacs import DatabasePACS
from sphere.command.command_database import CommandDatabase
from sphere.pacs.query_ds import QueryDataset
from sphere.logs.logs import LOG_EVENT_SPHERE, LOG_TRANSACTION
from sphere import settings

_config.DECODE_STORE_DATASET = False


class SphereAE(AE):

    def __init__(self, queue):
        super().__init__()

        self.handlers = []

        self.query_ds = QueryDataset()

        # Define server connexion element
        self.port = settings.SCP_PORT
        self.ae_title = settings.SCP_AET
        self.require_called_aet = settings.REQUIRE_CALL_AET
        # TODO : Gerer les parametre de connexion
        # Limit parameter for server
        self.MaxAssociationIdleSeconds = settings.MAX_ASSOC_IDLE_SECOND  # not used
        self.maximum_associations = settings.MAX_ASSOC
        self.maximum_pdu_size = settings.PDU_SIZE

        self.acse_timeout = settings.ACSE_TIMEOUT
        self.dimse_timeout = settings.DIMSE_TIMEOUT
        self.network_timeout = settings.NETWORK_TIMEOUT

        self.list_assoc = []
        self.count_assoc = 0

        # self.db_queue = queue
        # Generate database instances
        self.db_pacs = DatabasePACS(queue)
        # self.db_logs = DatabaseLogs()

        # Generate Log var
        # self.instanceAEServerID = uuid.uuid4().int
        # self.dtStartServerInstance = datetime.now()

    def initialize_callback_action(self):
        """
        Initialize the callback action
        """
        self.callback_actions()

    def define_context_supported(self):
        """
        Add to ae instance the different requested context for each scp
            action authorized by settings
        """
        # TODO Gerer les differents type de storage. Adapter au cas par cas
        if 'c-echo' in settings.SCP_SERVICES:
            self.add_supported_context(VerificationSOPClass)
        if 'c-store' in settings.SCP_SERVICES:
            self.supported_contexts = sphere_storage_presentation_contexts
        if 'c-find' in settings.SCP_SERVICES:
            self.add_supported_context(
                PatientRootQueryRetrieveInformationModelFind)
            self.add_supported_context(
                StudyRootQueryRetrieveInformationModelFind)
        if 'c-move' in settings.SCP_SERVICES:
            self.requested_contexts = StoragePresentationContexts
            self.add_supported_context(
                PatientRootQueryRetrieveInformationModelMove)
            self.add_supported_context(
                StudyRootQueryRetrieveInformationModelMove)

    def define_context_requested(self, type_service, context=None):
        """
        Define the context Requested

        :param type_service: Type of service

            The possible value:

                - ``cechoscu``
                - ``cstorescu``
                - ``cfindscu``
                - ``cmovescu``

        :type type_service: str
        :param context: Name of the project's context
        :type context: str, None, optional
        """
        LOG_TRANSACTION.info("Define the context Requested for '%s'",
                             type_service)
        # TODO Meilleurs application des types de services, via les settings
        if 'cechoscu' == type_service:
            self.add_requested_context(VerificationSOPClass)
        elif 'cstorescu' == type_service:


            try:
                if context is not None:
                    self.requested_contexts = settings.DICT_CONTEXTS[context]
                else:
                    self.requested_contexts = \
                        settings.DICT_CONTEXTS[settings.LOCAL_CONTEXT]
            except KeyError:
                self.requested_contexts = settings.DICT_CONTEXTS['default']
                print("Info: Name of the project's context '{0}' given as "
                      "argument not recognised. Falling back to default context"
                      ".".format(context))
        elif 'cfindscu' == type_service:  # TODO Gerer les different level de findscu
            self.add_requested_context(
                PatientRootQueryRetrieveInformationModelFind)
            self.add_requested_context(
                StudyRootQueryRetrieveInformationModelFind)
            # self.add_requested_context(ModalityWorklistInformationFind)
        elif 'cmovescu' == type_service:
            self.add_requested_context(
                PatientRootQueryRetrieveInformationModelMove)
            self.add_requested_context(
                StudyRootQueryRetrieveInformationModelMove)

    def callback_actions(self):
        """
        Add to ae instance a function action dedicated for each scp action
            authorized by settings
        """
        # TODO Revoir l'appel au contexte avant la mise en place des services
        if 'c-echo' in settings.SCP_SERVICES:
            self.handlers.append((evt.EVT_C_ECHO, self.scp_cecho_action()))
        if 'c-store' in settings.SCP_SERVICES:
            self.handlers.append((evt.EVT_C_STORE, self.scp_cstore_action()))
        if 'c-find' in settings.SCP_SERVICES:
            self.handlers.append((evt.EVT_C_FIND, self.scp_cfind_action()))
        if 'c-move' in settings.SCP_SERVICES:
            self.handlers.append((evt.EVT_C_MOVE, self.scp_cmove_action()))
        self.define_context_supported()

# # C-ECHO
    def scp_cecho_action(self):
        """
        Initialize a cecho service and return the function action
            used for this

        :return: function/method reference call for cecho action
        :rtype: cecho_response
        """
        service = CEcho(self)
        return service.cecho_response

    def scu_cecho_action(self, **kwargs):
        """
        Run cecho request

        :param ip: The IP
        :type ip: str
        :param port: The Port
        :type port: str
        :param aec: Application Entity target Name
        :type aec: str, optional
        :return: function/method reference call for cecho_request
        :rtype: cecho_request
        """
        self.define_context_requested('cechoscu')
        verbose_level = kwargs.get('verbose')
        service = CEcho(self, {
            'ip': kwargs['ip'], 'port': kwargs['port'], 'aec': kwargs['aec']})
        return service.cecho_request(verbose_level)

# # C-STORE
    def scp_cstore_action(self):
        """
        Initialize a cstore service and return the function pointer action
            used for this

        :return: function/method reference call for cstore action
        :rtype: cstore_response
        """
        service = CStore(self)
        return service.cstore_response

    def scu_cstore_action(self, **kwargs):
        """
        Run the cstore request

        :param kwargs: The arguments of the cstores command. Kwargs comments in
            the function "cstore_action()" exists in "parser.py"
        :type kwargs: dict
        :return: function/method reference call for cstore_request
        """

        kwargs_store = {}
        self.define_context_requested('cstorescu', kwargs['context'])
        kwargs_store['verbose_level'] = kwargs.get('verbose')
        kwargs_store['many_assoc'] = kwargs.get('many_assoc')

        source_paths_db_fs = kwargs.get('source_paths_db_fs')
        kwargs_store['source_paths_db_fs'] = source_paths_db_fs
        if source_paths_db_fs == 'db':
            if 'uid_file_path' in kwargs:
                file_path = kwargs.get('uid_file_path')
                # Type of uid (patient, study or series)
                model_name = str(kwargs.get('model_name'))
                if file_path:
                    kwargs_store['file_path'] = str(file_path)
                else:
                    kwargs_store['file_path'] = file_path
                kwargs_store['any_uid'] = kwargs.get('any_uid')
                kwargs_store['model_name'] = model_name

        else:  # file system
            dicom_path = kwargs.get('path_dicom_dire_or_file')
            kwargs_store['dicom_path'] = dicom_path

        service = CStore(self, {
            'ip': kwargs['ip'], 'port': kwargs['port'], 'aec': kwargs['aec']})

        return service.cstore_request(kwargs_store)

# # Function for C-FIND and C-MOVE
    @staticmethod
    def qr_level(action, query_retrieve_level=None):
        """
        Return the query model with query retrieve level

        :param action: The action

            list of possible value of action:
                - ``find``
                - ``move``

        :type action: str
        :param query_retrieve_level: The query retrieve level

            list of possible value of query_retrieve_level:
                - ``PATIENT``
                - ``STUDY``
                - ``SERIES``

        :type query_retrieve_level: str
        :return: The query model

            The possible value to return:
                | ``P`` - PATIENT
                | ``S`` - STUDY (default)
                | ``S`` - SERIES
                | ``SE`` - SERIES (if action equal ``find`` and
                    query_retrieve_level equal ``SERIES``)

        :rtype: str
        """
        query_model = "S"
        if query_retrieve_level == "STUDY":
            query_model = "S"
        elif query_retrieve_level == "PATIENT":
            query_model = "P"
        elif query_retrieve_level == "SERIES" and action == "find":
            query_model = "SE"
        elif query_retrieve_level == "SERIES" and action == "move":
            query_model = "S"
        LOG_TRANSACTION.info("Return the query model with query retrieve level")
        return query_model

# # C-FIND
    def scp_cfind_action(self):
        """
        Run the cfind response

        :return: function/method reference call for cfind_response
        :type: cfind_response
        """
        service = CFind(self)
        return service.cfind_response

    def scu_cfind_action(self, **kwargs):
        """
        Run the cfind request

        :param kwargs: The arguments of the cfind command. Kwargs comments in
            the function "cfind_action()" exists in "parser.py"
        :type kwargs: dict
        :return: function/method reference call for cfind_request
        """
        self.define_context_requested('cfindscu')
        service = CFind(self, {
            'ip': kwargs['ip'], 'port': kwargs['port'], 'aec': kwargs['aec']})
        action = kwargs.get('action')
        query_retrieve_level = kwargs.get('qr_level')
        # verbose_level = kwargs.get('verbose')

        # noinspection PyTypeChecker
        query_model = self.qr_level(action, query_retrieve_level)
        ds = self.query_ds.create_query_ds(**kwargs)  # Create query dataset

        file_path = kwargs.get('output_filepath')

        return service.cfind_request(
            ds=ds, query_retrieve_level=query_retrieve_level,
            query_model=query_model, file_path=file_path,
            display_ds=kwargs.get('display_ds'),
            verbose_level=kwargs.get('verbose'),
            overwrite=kwargs.get('overwrite'))

# #C-MOVE
    def scp_cmove_action(self):
        """
        Run the cmove request

        :return: function/method reference call for cmove_response
        :rtype: cmove_response
        """
        service = CMove(self)
        return service.cmove_response

    def scu_cmove_action(self, **kwargs):
        """
        Run the cmove request

        :param kwargs: The arguments of the cmove command. Kwargs comments in
            the function "cmove_action()" exists in "parser.py"
        :type kwargs: dict
        :return: function/method reference call for cmove_request
        """
        self.define_context_requested('cmovescu')
        service = CMove(self, {
            'ip': kwargs['ip'], 'port': kwargs['port'], 'aec': kwargs['aec']})
        action = kwargs.get('action')
        query_retrieve_level = kwargs.get('qr_level')
        query_model = self.qr_level(action, query_retrieve_level)
        # Create query dataset
        list_ds = self.query_ds.create_query_ds(**kwargs)

        return service.cmove_request(list_ds=list_ds,
                                     file_uid=kwargs['file_uid'],
                                     ae_cstore=kwargs['ae_cstore'],
                                     query_model=query_model,
                                     verbose_level=kwargs.get('verbose'))

# #C-MOVE EXISTING
    def scu_cmove_existing_action(self, **kwargs):
        """
        Run cmove existing

        :param kwargs: The arguments of the cmove_existing command. Kwargs
            comments in the function "cmove_existing_action()" exists in "parser.py"
        :type kwargs: dict
        """
        LOG_EVENT_SPHERE.info('Start cmove_existing')
        LOG_TRANSACTION.info('{:-^90}'.format('Start cmove_existing'))

        LOG_TRANSACTION.info('Find in cmove_existing')
        print('Find in cmove_existing')
        kwargs['action'] = "find"
        self.scu_cfind_action(**kwargs)
        print('Diff')
        LOG_TRANSACTION.info('Diff in cmove_existing')
        output_filepath = kwargs['output_filepath']
        dict_diff = {'output_filepath': 'diff_' + output_filepath,
                     'db_action': 'check', 'check_mode': 'diff',
                     'list_filepath': 'study_uid', 'concept': 'study'}
        req_cmd = CommandDatabase(**dict_diff)
        req_cmd.execute()
        LOG_TRANSACTION.info('Move in cmove_existing')
        print('Move in cmove_existing')
        kwargs['action'] = "move"
        kwargs['file_study_uid'] = dict_diff['output_filepath']
        self.scu_cmove_action(**kwargs)
        LOG_TRANSACTION.info('{:-^90}'.format('End cmove_existing'))

# #OTHER FUNCTION
    def create_association(self):  # not used
        """ Create association"""
        return self.associate('127.0.0.1', 11111, ae_title='PSource')

    def start(self):
        """ start server"""
        LOG_EVENT_SPHERE.info("Runserver the PACS '%s' ",
                              self.ae_title.decode("utf-8").strip())
        self.start_server(('', self.port), evt_handlers=self.handlers)


# by default ImplicitVRLittleEndian, ExplicitVRLittleEndian and
# ExplicitVRBigEndian in StoragePresentationContexts
sphere_storage_presentation_contexts = copy.deepcopy(
    StoragePresentationContexts)

# Pre-defined Transfer Syntax UIDs (for convenience)
extra_transfer_syntax = [DeflatedExplicitVRLittleEndian, JPEGBaseline,
                         JPEGExtended, JPEGLosslessP14, JPEGLossless,
                         JPEGLSLossless, JPEGLSLossy, JPEG2000Lossless,
                         JPEG2000, JPEG2000MultiComponentLossless,
                         JPEG2000MultiComponent, RLELossless]

for presentation_context in sphere_storage_presentation_contexts:
    for transfer_syntax in extra_transfer_syntax:
        presentation_context.transfer_syntax.append(transfer_syntax)
