from sphere.dicmeta.requests.request import Request
from sphere.dicmeta.views.speed_view import SpeedView


class SpeedViewRequest(Request):

    def __init__(self, db):
        super().__init__(db)

        self.modelTable = SpeedView
