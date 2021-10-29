""" Create associate and log"""
# pylint: disable=invalid-name

from sphere import settings
from sphere.utilities.list_accessible_ae import list_all_access_list
from sphere.logs.logs import LOG_TRANSACTION


class Associate:

    def __init__(self, ae, start=True, kwargs={}):
        # TODO : Verifier qu'il s'agit bien d'une instance d'ae
        self.ae = ae
        self.action_dicom_code_name = 'C[ECHO|FIND|MOVE|STORE|GET]'
        self.service_dicom_code_name = 'SC[U|P]'

        self.console_verbose = settings.VERBOSE_CONSOLE_LEVEL
        self.database_verbose = settings.VERBOSE_DATABASE_LEVEL

        # self.statusAssoc = {}

        if 'aec' in kwargs:
            self.aec = kwargs['aec']
        else:
            self.aec = None

        # Create Association
        if 'ip' in kwargs and 'port' in kwargs:
            LOG_TRANSACTION.info("Create a association with '%s'", self.aec)
            self.ip = kwargs['ip']
            self.port = kwargs['port']
            self.aec = kwargs['aec']

            if start:
                self.assoc = self.associate(
                    ip=kwargs['ip'], port=kwargs['port'], aec=kwargs['aec'])
        else:
            self.assoc = None

    def associate(self, ip, port, aec=None):
        """
        Create associate

        :param ip: The Internet Protocol
        :type ip: str
        :param port: The port
        :type port: str
        :param aec: Application Entity target Name
        :type aec: str, optional
        :return: The associate
        """
        assoc = self.ae.associate(ip, port, ae_title=aec)
        return assoc

    def generate_new_association_from_aet(self, aec=None):
        """
        Generate a new association from aet

        :param aec: Application Entity target Name
        :type aec: str, optional
        :return: The associate
        :rtype: :py:class:`pynetdicom.association.Association`
        """
        # TODO : Ne pas faire ca comme ca, plutot un fonction retreive de
        #  toutes les possibilite
        LOG_TRANSACTION.info("Create new association with %s ",
                             aec if aec is not None else self.aec)
        if aec is not None:
            access_list = list_all_access_list()
            if aec in access_list:
                try:
                    return self.associate(
                        ip=access_list[aec]['ip'],
                        port=access_list[aec]['port'], aec=aec)
                except Exception as error:
                    txt_except = 'association impossible: {0} '.format(error)
                    LOG_TRANSACTION.error(txt_except)
                    raise Exception(txt_except)
        return self.associate(ip=self.ip, port=self.port, aec=self.aec)
