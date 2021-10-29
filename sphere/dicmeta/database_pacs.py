""" Database pacs"""
# pylint: disable=invalid-name
from sphere.dicmeta.models.dicom_models.patient_model import PatientModel
from sphere.dicmeta.models.dicom_models.study_model import StudyModel
from sphere.dicmeta.models.dicom_models.series_model import SeriesModel
from sphere.dicmeta.models.dicom_models.file_storage_metadata_model import FileStorageMetadataDicomModel

# Import temp models
from sphere.dicmeta.models.temp_models.temp_file_storage_metadata_model import TempFileStorageMetadataModel
from sphere.dicmeta.models.temp_models.temp_series_model import TempSeriesModel
from sphere.dicmeta.models.temp_models.temp_study_model import TempStudyModel
from sphere.dicmeta.models.temp_models.temp_patient_model import TempPatientModel

# Import api models
try:
    from sphere.settings import START_ANNOTATION
except ImportError:
    START_ANNOTATION = False

if START_ANNOTATION:
    from sphere.dicmeta.models.api_models.mapping_annotation_model import MappingAnnotationModel

from sphere.dicmeta.models.study_list_model import StudyListModel

# Import the view
from sphere.dicmeta.views.modality_view import ModalityView
from sphere.dicmeta.views.speed_view import SpeedView

from .database import Database
from .models.base import DB_BASE_PACS


class DatabasePACS(Database):
    """ Bring together all pacs modules"""
    def __init__(self, db_queue=None):
        self.metadata_table = DB_BASE_PACS.metadata
        super().__init__()

        self.PatientModel = PatientModel
        self.StudyModel = StudyModel
        self.SeriesModel = SeriesModel
        self.FileStorageMetadataDicomModel = FileStorageMetadataDicomModel

        # API module
        if START_ANNOTATION:
            self.MappingAnnotationModel = MappingAnnotationModel

        # Temp Models
        self.TempFileStorageMetadataModel = TempFileStorageMetadataModel
        self.TempStudyModel = TempStudyModel
        self.TempSeriesModel = TempSeriesModel
        self.TempPatientModel = TempPatientModel

        self.StudyListModel = StudyListModel

        self.db_queue = db_queue

        self.views = {'modality': ModalityView(), 'speed': SpeedView()}
