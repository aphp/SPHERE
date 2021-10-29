""" Create verbose of PACS"""
from datetime import datetime

from sphere import settings
from sphere.logs.dicom_code import DicomCode


class Verbose(DicomCode):
    """ Init, create and display verbose of PACS"""

    def __init__(self, ae):
        self.ae = ae  # pylint: disable=invalid-name
        self.console_verbose = settings.VERBOSE_CONSOLE_LEVEL
        self.database_verbose = settings.VERBOSE_DATABASE_LEVEL

    def init_verbose(self, context=None, verbose_level=None, **kwargs):
        """
        Init dict verbose

        :param context: The context (abstract_syntax and transfer_syntax)

            Example of context :
                | ``PresentationContextTuple(context_id=87,
                    abstract_syntax='1.2.840.10008.5.1.4.1.1.4',
                    transfer_syntax='1.2.840.10008.1.2')``

        :type context: :py:class:`pynetdicom.presentation.PresentationContextTuple`
        :param verbose_level: The verbose

            list of possible value of verbose:

                | ``0`` - quiet mode
                | ``1`` - verbose mode
                | ``0`` - ultra-verbose mode
        :type verbose_level: int, default None
        :param kwargs: Parameters dictionary

            The list of parameters is:

                | action            : Action launch

                    list of possible value of action:
                        |  - ``CECHO``
                        |  - ``CSTORE``
                        |  - ``CFIND``
                        |  - ``CMOVE``

                | service        : The service

                    list of possible value of service:
                        | - ``SCU``
                        | - ``SCP``

                | aec          : Application Entity target Name
                | aec_scu      : Application Entity to send CSTORE
                | log   :  The verbose message

            Example of kwargs:
                | {
                |   'action'     : 'CECHO'
                |   'service'    : 'SCU',
                |   'aec'        : 'PACS1',
                |   'aec_scu'    : 'PACS2',
                |   'log'        : 'Start cecho_request and Check Association'
                | }

        :type kwargs: dict
        :return: The verbose of pacs
        :rtype: dict
        """
        action = kwargs.get('action')
        service = kwargs.get('service')
        aec = kwargs.get('aec')
        aec_scu = kwargs.get('aec_scu')
        log = kwargs.get('log')

        verbose_pacs = {
            'study_uid': None,
            'series_uid': None,
            'instance_uid': None,
            'action': action,
            'step': 'start',
            'service': service,
            'dt_exec': datetime.now(),
            'success': True,
            'associate_ae': aec if service == 'SCP' else aec_scu,
            'ae': self.ae.ae_title.decode('utf-8'),
            'final_status': None,
            'dict_log_message': None,
            'log': log}
        if hasattr(context, 'context_id'):
            verbose_pacs['context_id'] = context.context_id
        if hasattr(context, 'abstract_syntax'):
            verbose_pacs['abstract_syntax'] = context.abstract_syntax
        if hasattr(context, 'transfer_syntax'):
            verbose_pacs['transfer_syntax'] = context.transfer_syntax

        if verbose_level is not None:
            self.console_verbose = verbose_level

        self.commit_verbose(verbose_pacs)
        return verbose_pacs

    def create_verbose(self, verbose_pacs, commit=False, **kwargs):
        """
        Create the verbose

        :param verbose_pacs: The verbose dictionary
        :type verbose_pacs: dict
        :param commit: status of commit (True | False)
        :type commit: bool, optional
        :param kwargs: Parameters dictionary

            The list of parameters is:

                | success     : Success or not (True | False)
                | error       : Error or not (True | False)
                | close_id    : The request log
                | log         : The log

            Example of kwargs:
                | {
                |   'success': True,
                |
                | }

        :type kwargs: dict
        :return: request_log

        """
        if 'final_status' in kwargs:
            commit = True
            if isinstance(kwargs['final_status'], int):
                kwargs['final_status'] = '0x{0:04x}'.format(
                    kwargs['final_status'])
            kwargs['dict_log_message'] = self.DICOM_CODE_LOG_MESSAGE[
                kwargs['final_status']]

        verbose_pacs.update(kwargs)

        self.commit_verbose(verbose_pacs, commit=commit)

        # return request_log

    def commit_verbose(self, verbose_pacs, commit=False):
        """
        Commit verbose

        :param verbose_pacs: The verbose dictionary
        :type verbose_pacs: dict
        :param commit: status of commit (True | False)
        :type commit: bool, optional
        """
        if (commit and self.console_verbose == 1) or self.console_verbose > 1:
            self.print_verbose(verbose_pacs)

    def print_verbose(self, verbose_pacs):
        """
        Print status of association

        :param verbose_pacs: The verbose dictionary
        :type verbose_pacs: dict
        """
        head = "\n######################### CURRENT %s %s ASSOC ###########" \
            "##############\n" % (
                verbose_pacs.get('service'), verbose_pacs.get('action'))

        count_head = len(head)
        msg = head
        msg += "# Server Association metadata\n"
        msg += "# update date \t\t: %s\n" % (datetime.now())
        if verbose_pacs['service'] == 'SCP':
            msg += "# simultaneous assoc : %s\n" % self.ae.count_assoc
        msg += "# %s\n" % ('-'*(count_head-2))
        msg += "# %s\n" % ('-'*(count_head-2))
        msg += "# action\t\t: %s\n" % verbose_pacs.get('action')
        msg += "# service\t\t: %s\n" % verbose_pacs.get('service')
        if verbose_pacs.get('final_status'):
            msg += "# final_status\t\t: %s : %s \n" % (
                verbose_pacs.get('final_status'),
                verbose_pacs.get('dict_log_message'))
        if verbose_pacs.get('study_uid'):
            msg += "# Study UID\t\t: %s\n" % verbose_pacs.get('study_uid')
            msg += "# Series UID\t\t: %s\n" % verbose_pacs.get('series_uid')
            msg += "# Instance UID\t\t: %s\n" % verbose_pacs.get('instance_uid')

        if verbose_pacs.get('action') == "CFIND" and self.console_verbose == 1:
            msg += "# %s\n" % ('-' * (count_head - 2))
            msg += "# LOG\n"
            msg += "# %s\n" % ('-' * (count_head - 2))
            msg += "# last_log\t: %s\n" % verbose_pacs.get('log')

        if self.console_verbose > 1:
            msg += "# dt_exec\t\t: %s\n" % verbose_pacs.get('dt_exec')
            msg += "# associate_ae\t\t: %s\n" % verbose_pacs.get('associate_ae')
            msg += "# AE\t\t\t: %s\n" % verbose_pacs['ae']

            # if self.console_verbose > 1:
            msg += "# success\t\t: %s\n" % verbose_pacs.get('success')
            msg += "# %s\n" % ('-'*(count_head-2))

            if verbose_pacs.get('context_id'):
                msg += "# CONTEXT\n"
                msg += "# %s\n" % ('-'*(count_head-2))
                msg += "# context ID\t\t: %s\n" % verbose_pacs.get('context_id')
                msg += "# abstract Syntax\t: %s\n" % verbose_pacs.get(
                    'abstract_syntax')
                msg += "# Transfer Syntax\t: %s\n" % verbose_pacs.get(
                    'transfer_syntax')
                msg += "# %s\n" % ('-'*(count_head-2))
            msg += "# LOG\n"
            msg += "# %s\n" % ('-'*(count_head-2))
            msg += "# last_log\t: %s\n" % verbose_pacs.get('log')
            if verbose_pacs.get('dataset'):
                msg += "# %s\n" % ('-' * (count_head - 2))
                msg += "# DATASET DICOM\n"
                msg += "# %s\n" % ('-' * (count_head - 2))
                for line in verbose_pacs.get('dataset'):
                    msg += "# %s\n" % line
        msg += "%s" % ('#'*count_head)
        print(msg)
