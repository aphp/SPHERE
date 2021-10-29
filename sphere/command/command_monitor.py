""" Command of monitor"""
from collections import Iterable

from sphere.dicmeta.database_pacs import DatabasePACS
from sphere.dicmeta.requests.modality_view_request import ModalityViewRequest
from sphere.dicmeta.requests.speed_view_request import SpeedViewRequest


class CommandMonitor:

    DATA_LEVEL = {'full': 2, 'minimal': 1, 'key': 0}

    def __init__(self, **kwargs):
        self.db_pacs = DatabasePACS()
        self.action = kwargs['action']
        self.initialize_attribute(**kwargs)

    def initialize_attribute(self, **kwargs):
        """
        Initialize attribute of monitor

        :param kwargs: Parameters dictionary

            The list of parameters is:

                | func      : Function name
                | action    : Type of action, possible value is ``monitor``
                | concept   : The concept

                    The possible value: ``speed`` or ``modality``

                | data_level: The display level

                    The possible value: ``full``, ``minimal`` or ``key``

            Example of kwargs:
                | {
                |   'func'      : <function monitor_action at 0x7f66dc2d8b70>,
                |   'action'    : 'monitor'
                |   'concept'   : 'speed',
                |   'data_level': 'full'
                | }

        :type kwargs: dict
        """
        if 'concept' in kwargs and kwargs['concept'] in ['modality', 'speed']:
            self.concept = kwargs['concept']
        else:
            raise Exception('Please define a "concept" model valid')

        if 'data_level' in kwargs and kwargs['data_level'] in self.DATA_LEVEL:
            self.data_level = self.DATA_LEVEL[kwargs['data_level']]
        else:
            raise Exception('Please define a "data level" compatible')

    def execute(self):
        """ Execute modality and speed"""
        if self.concept == 'modality':
            res = ModalityViewRequest(self.db_pacs).get_all()
        if self.concept == 'speed':
            res = SpeedViewRequest(self.db_pacs).get_all()

        self.display_data(res)

    def display_data(self, data):
        """
        Display data

        :param data: The data
        :type data: list
        """
        if data is None or (isinstance(data, (list,)) and
                            (len(data) < 1 or all(x is None for x in data))):
            # raise Exception('No db entries founded')
            print('No db entries founded')
            return
        try:
            if isinstance(data, Iterable):
                for d in data:  # pylint: disable=invalid-name
                    d.display(self.data_level, output_console=True)
            else:
                data.display(self.data_level, output_console=True)
        except Exception as error:
            print(error)
            txt = "No display method for data " + self.concept
            raise Exception(txt)
