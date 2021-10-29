from sphere.dicmeta.requests.request import Request
from sphere.dicmeta.views.modality_view import ModalityView


class ModalityViewRequest(Request):

    def __init__(self, db):
        super().__init__(db)

        self.modelTable = ModalityView
