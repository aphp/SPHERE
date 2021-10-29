""" Check echo of PACS"""

from sphere.utilities.list_accessible_ae import auth_in
from sphere.logs.verbose import Verbose
from sphere.logs.logs import LOG_EVENT_SPHERE, LOG_TRANSACTION
from .associate import Associate


class CEcho(Associate, Verbose):
    """
    Define Request action to SCP C-ECHO
        Define cecho Response from a c-echo request
        included file access authorization
    """

    def __init__(self, ae, kwargs={}):
        super().__init__(ae, kwargs=kwargs)

        self.action_dicom_code_name = 'CECHO'

    def cecho_response(self, event):
        """
        Verification of authorized access and return a success status code or
            unauthorized code

        :param event: The event
        :type event: :py:class:`pynetdicom.events.Event`
        :return: DICOM status hex code

            Success
              | ``0x0000`` - Success

            Failure
              | ``0xA801`` - unauthorized access
        :rtype: str
        """
        context = event.context

        # Log
        aec = event.assoc.requestor.ae_title.strip().decode("utf-8", "strict")
        LOG_EVENT_SPHERE.info("'%s' got a %s from '%s'",
                              self.ae.ae_title.decode("utf-8").strip(),
                              self.action_dicom_code_name, aec)

        dict_verbose = self.init_verbose(context=context, **{
            'action': self.action_dicom_code_name,
            'service': 'SCP',
            'log': 'Start cecho_response and Check Association',
            'aec': aec})
        LOG_TRANSACTION.info('Start cecho_response')
        # End log

        if auth_in(event, self.action_dicom_code_name):
            # Log
            self.create_verbose(dict_verbose, **{
                'final_status': self.DICOM_CODE_SUCCESS,
                'log': 'Association Success'})
            LOG_TRANSACTION.info('Association Success')
            # End log

            return self.DICOM_CODE_SUCCESS

        # Log
        self.create_verbose(dict_verbose, **{
            'success': False,
            'final_status': self.DICOM_CODE_UNAUTHORIZED_ACCESS,
            'log': 'Association Failed'})
        LOG_TRANSACTION.error('Association Failed')
        # End log

        return self.DICOM_CODE_UNAUTHORIZED_ACCESS

    def cecho_request(self, verbose_level=None):
        """
        launch the request of c-echo

        :param verbose_level: The verbose_level
        :type verbose_level: int, default None

            list of possible value of verbose_level:
                - ``0`` quiet mode
                - ``1`` verbose mode
                - ``0`` ultra-verbose mode
        """
        # Log
        LOG_EVENT_SPHERE.info("Launch the %s on %s ",
                              self.action_dicom_code_name, self.aec)
        LOG_TRANSACTION.info('Start cecho_request and Check Association')
        dict_verbose = self.init_verbose(verbose_level=verbose_level, **{
            'action': self.action_dicom_code_name,
            'service': 'SCU',
            'log': 'Start cecho_request and Check Association',
            'aec_scu': self.aec})
        # End log

        if self.assoc.is_established:
            # Log
            LOG_TRANSACTION.info('Association Success')
            self.create_verbose(dict_verbose, **{
                'log': 'Association Success and execute TCP Request; '
                       'send echo'})
            # End log

            # Use the C-ECHO service to send the request
            # returns the response status a pydicom Dataset
            status = self.assoc.send_c_echo()

            # Log
            self.create_verbose(dict_verbose, **{'log': 'TCP Request finalized'})
            # End log

            # Check the status of the verification request
            # If the verification request succeeded this will be 0x0000
            if 'Status' in status:
                # Log
                self.create_verbose(dict_verbose, **{
                    'final_status': '0x{0:04x}'.format(status.Status),
                    'log': ' Status 0x0000'})
                LOG_TRANSACTION.info(
                    'C-ECHO request status: 0x{0:04x}'.format(
                        self.DICOM_CODE_SUCCESS))
                # End log

            else:
                # Log
                self.create_verbose(dict_verbose, **{
                    'success': False,
                    'final_status': self.DICOM_CODE_ASSOCIATION_ABORTED})
                LOG_TRANSACTION.error("Association rejected or aborted")
                # End log
                # print('Connection timed out or invalid response from peer')

            # Release the association
            self.assoc.release()
        else:
            # Log
            self.create_verbose(dict_verbose, **{
                'success': False,
                'final_status': self.DICOM_CODE_UNAUTHORIZED_ACCESS,
                'log': 'Association Failed'})
            LOG_TRANSACTION.error("Cecho request; Association Failed")
            # End log
