""" Test the module query_ds"""
from sphere.pacs.query_ds import QueryDataset
query_ds = QueryDataset()


class TestQueryDS:
    BASE = {'action': 'find', 'ip': '127.0.0.1', 'port': 11111, 'aec': 'PACS1'}
    DICT_PATIENT = {'qr_level': 'PATIENT', 'patient_id': None,
                    'study_uid': None, 'series_uid': None,
                    'output_filepath': None}
    DICT_PATIENT_ID = {'qr_level': 'PATIENT', 'patient_id': '142536',
                       'study_uid': None, 'series_uid': None,
                       'output_filepath': None}

    DICT_STUDY = {'qr_level': 'STUDY', 'patient_id': None,
                  'study_uid': None, 'series_uid': None,
                  'output_filepath': None}
    DICT_STUDY_UID = {'qr_level': 'STUDY', 'patient_id': None,
                      'study_uid': "1.1.2.12.23.45.85", 'series_uid': None,
                      'output_filepath': None}

    DICT_SERIES = {'qr_level': 'SERIES', 'patient_id': None,
                   'study_uid': None, 'series_uid': None,
                   'output_filepath': None}
    DICT_SERIES_UID = {'qr_level': 'SERIES', 'patient_id': None,
                       'study_uid': None, 'series_uid': '1.22.1.52.444.1',
                       'output_filepath': None}

    DICT_PATIENT.update(BASE)
    DICT_PATIENT_ID.update(BASE)
    DICT_STUDY.update(BASE)
    DICT_STUDY_UID.update(BASE)
    DICT_SERIES.update(BASE)
    DICT_SERIES_UID.update(BASE)

    # TODO test patient_id and study_uid and series_uid if not None
    def test_find_patient(self):
        """ test find patient"""
        data_set = query_ds.create_query_ds(**self.DICT_PATIENT)
        assert data_set.QueryRetrieveLevel == 'PATIENT'
        assert data_set.PatientID == '*'
        ds_id = query_ds.create_query_ds(**self.DICT_PATIENT_ID)
        assert ds_id.QueryRetrieveLevel == 'PATIENT'
        assert ds_id.PatientID == '142536'

    def test_find_study(self):
        """ Test find study """
        data_set = query_ds.create_query_ds(**self.DICT_STUDY)
        assert data_set.QueryRetrieveLevel == 'STUDY'
        assert data_set.StudyInstanceUID == '*'
        data_set = query_ds.create_query_ds(**self.DICT_STUDY_UID)
        assert data_set.QueryRetrieveLevel == 'STUDY'
        assert data_set.StudyInstanceUID == '1.1.2.12.23.45.85'

    def test_find_series(self):
        """ Test find series"""
        data_set = query_ds.create_query_ds(**self.DICT_SERIES)
        assert data_set.QueryRetrieveLevel == 'SERIES'
        assert data_set.SeriesInstanceUID == '*'
        data_set = query_ds.create_query_ds(**self.DICT_SERIES_UID)
        assert data_set.QueryRetrieveLevel == 'SERIES'
        assert data_set.SeriesInstanceUID == '1.22.1.52.444.1'
