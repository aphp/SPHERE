from sphere import settings
from .database_pacs import DatabasePACS
from .dcm_file import DcmFile
from sphere.logs.logs import LOG_DATABASE


class DcmManager:

    def __init__(self, ds, db_pacs):
        self.db_pacs = DatabasePACS() if db_pacs is None else db_pacs

        if isinstance(ds, list) or isinstance(ds, tuple):
            self.dataset = [dcm for dcm in ds]
        elif ds.__class__ == DcmFile or ds.__class__ in DcmFile.__bases__:
            self.dataset = [ds]
        elif isinstance(ds, dict):
            self.dataset = [
                dcm for dcm in ds if DcmFile == dcm.__class__ or
                type(dcm) in DcmFile.__bases__]
        else:
            LOG_DATABASE.exception('No data in ds')

        try:
            # Cast
            for dcm in self.dataset:
                dcm.__class__ = DcmFile
        except Exception as exc:
            LOG_DATABASE.exception(exc)

    def add_metadata_dicom(self, instance_storage_metadata=None, queue_to_load=None):
        """
        Add object metadata DICOM in queue.
        It use the db connector defined in self.db_pacs.

        :param instance_storage_metadata: The id of storage metadata included
        :type instance_storage_metadata: int, None, optional
        :param queue_to_load: dict objects of data base
        :type queue_to_load: class queue.Queue, optional
        """
        for dcm in self.dataset:
            patient = self.db_pacs.PatientModel(**dcm.patient_metadata())
            study = self.db_pacs.StudyModel(**dcm.study_metadata(), **{'patient': patient})
            series = self.db_pacs.SeriesModel(**dcm.series_metadata(), **{'patient': patient, 'study': study})
            #instance = self.db_pacs.FileStorageMetadataDicomModel(**dcm.instance_metadata(),
            #                                      **{'patient': patient,
            #                                         'study': study,
            #                                         'series': series,
            #                                         'storage_metadata': storage_metadata})

            d = {**dcm.file_storage_metadata(),
                 **{'patient': patient,
                    'study': study,
                    'series': series},
                 **instance_storage_metadata}
            instance = self.db_pacs.FileStorageMetadataDicomModel(**d)

            dict_objects = {
                'patient': patient,
                'study': study,
                'series': series,
                'instance': instance}

            queue_to_load.put(dict_objects)
