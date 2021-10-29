import json
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase

from django.core.exceptions import FieldError

from api_sphere_dicomweb.test.db_test_utils import \
    compute_test_referentiel, get_metadata_from_instance_uid, \
    get_metadata_from_study_uid, get_metadata_from_series_uid, \
    compare_elements

from api_sphere_dicomweb.test.fixture_utils import update_fixture_fsys_path
# Create your tests here.

from api_sphere_dicomweb.views import AllInstancesView, AllInstancesOfStudyView, \
    AllInstancesOfSeriesOfStudyView, AllSeriesView, AllSeriesOfStudyView, AllStudiesView, \
    MetadataStudyView, MetadataSeriesView, MetadataInstanceView, DCMInstanceView, \
    DCMInstancesOfSeriesView, DCMInstancesOfSeriesOfStudyView

from api_sphere_dicomweb.models import Patient, Study, Series, Instance

from sphere.api_rest.api_sphere_dicomweb.metadata_tags_configuration \
    import METADATA_TAGS


FIXTURE_TEMPLATE_FILE = 'api_sphere_dicomweb_fixture_pynetdicom.template'
FIXTURE_FILE = update_fixture_fsys_path(FIXTURE_TEMPLATE_FILE)

INSTANCES_BY_STUDY_SERIES, LIST_ALL_STUDY, LIST_ALL_SERIES, LIST_ALL_INSTANCES, \
    LIST_INSTANCES_BY_STUDY, LIST_SERIES_BY_STUDY = \
    compute_test_referentiel("api_sphere_dicomweb/test/fixtures/" + FIXTURE_FILE)


class QidoRSTests(APITestCase):
    """
    Test class for qidors
    """
    fixtures = [FIXTURE_FILE]
    """
    Tests class
    """

    @staticmethod
    def test_qidors():
        """
        tests qidors
        :return: None
        """
        factory = APIRequestFactory()

        # all instances
        view_all_instances = AllInstancesView.as_view()
        request_all_instances = factory.get('qidors/instances/')
        response = view_all_instances(request_all_instances)
        assert response.status_code == 200
        resp_json = json.loads(response.content)
        instance_lst = resp_json['list_instance_uid']
        assert len(LIST_ALL_INSTANCES) == len(instance_lst)
        assert len(set(instance_lst).difference(LIST_ALL_INSTANCES)) == 0
        assert len(set(LIST_ALL_INSTANCES).difference(instance_lst)) == 0

        # all instances of study
        view_all_instances_of_study = AllInstancesOfStudyView.as_view()
        request_all_instances_of_study = factory.get('qidors/studies/<study>/instances/')
        for study in LIST_INSTANCES_BY_STUDY:
            instances_of_study = LIST_INSTANCES_BY_STUDY[study]
            response = view_all_instances_of_study(request_all_instances_of_study, study)
            assert response.status_code == 200
            resp_json = json.loads(response.content)
            instances_lst = resp_json['list_instance_uid']
            assert len(instances_of_study) == len(instances_lst)
            assert len(set(instances_lst).difference(instances_of_study)) == 0
            assert len(set(instances_of_study).difference(instances_lst)) == 0

        # all instances of series of study
        view_all_instances_of_series_of_study = AllInstancesOfSeriesOfStudyView.as_view()
        request_all_instances_of_series_of_study = factory.get(
            'qidors/studies/<study>/series/<series>/instances')
        for study in INSTANCES_BY_STUDY_SERIES:
            for series in INSTANCES_BY_STUDY_SERIES[study]:
                instances_of_series_of_study = INSTANCES_BY_STUDY_SERIES[study][series]
                response = view_all_instances_of_series_of_study(
                    request_all_instances_of_series_of_study, study, series)
                assert response.status_code == 200
                resp_json = json.loads(response.content)
                instances_lst = resp_json['list_instance_uid']
                assert len(instances_lst) != 0
                assert len(instances_of_series_of_study) == len(instances_lst)
                assert len(set(instances_lst).difference(instances_of_series_of_study)) == 0
                assert len(set(instances_of_series_of_study).difference(instances_lst)) == 0

        # all series
        view_all_series = AllSeriesView.as_view()
        request_all_series = factory.get('qidors/studies')
        response = view_all_series(request_all_series)
        assert response.status_code == 200
        resp_json = json.loads(response.content)
        series_lst = resp_json['list_series_uid']
        assert len(LIST_ALL_SERIES) == len(series_lst)
        assert len(set(series_lst).difference(LIST_ALL_SERIES)) == 0
        assert len(set(LIST_ALL_SERIES).difference(series_lst)) == 0

        # all series of study
        view_all_series_of_study = AllSeriesOfStudyView.as_view()
        request_all_series_of_study = factory.get('qidors/studies/{study}/series')
        for study in LIST_SERIES_BY_STUDY:
            series_of_study = set(LIST_SERIES_BY_STUDY[study])
            response = view_all_series_of_study(request_all_series_of_study, study)
            assert response.status_code == 200
            resp_json = json.loads(response.content)
            series_lst = resp_json['list_series_uid']
            assert len(series_lst) != 0
            assert len(series_of_study) == len(series_lst)
            assert len(set(series_lst).difference(series_of_study)) == 0
            assert len(set(series_of_study).difference(series_lst)) == 0

        # all studies
        view_all_studies = AllStudiesView.as_view()
        request_all_studies = factory.get('qidors/studies')
        response = view_all_studies(request_all_studies)
        assert response.status_code == 200
        resp_json = json.loads(response.content)
        studies_lst = resp_json['list_study_uid']

        study_set = set(LIST_ALL_STUDY)
        assert len(studies_lst) != 0
        assert len(study_set) == len(studies_lst)
        assert len(set(studies_lst).difference(study_set)) == 0
        assert len(set(study_set).difference(studies_lst)) == 0

    @staticmethod
    def test_qidors_xml():
        """
        tests qidors with xml format
        :return: None
        """
        # all instances
        view_all_instances = AllInstancesView.as_view()
        request_all_instances = APIRequestFactory().get('qidors/instances/?fmt=xml')
        response = view_all_instances(request_all_instances)
        assert response.status_code == 200
        str_ret = response.content.decode('utf-8')
        print(str_ret)


class QidoRSFiltersTests(APITestCase):
    """
    Test class for qidors filter
    """
    fixtures = [FIXTURE_FILE]
    """
    Tests class
    """

    @staticmethod
    def test_qidors():
        """
        Tests qidors with filters
        :return: None
        """
        factory = APIRequestFactory()
        assert len(LIST_SERIES_BY_STUDY) != 0
        # AllInstancesView
        for tab in LIST_SERIES_BY_STUDY.values():
            for series_instance_uid in tab:
                view_all_instances = AllInstancesView.as_view()
                request_instances = factory.get(
                    'qidors/instances?SeriesInstanceUID={0}&limit=10&offset=0'
                    .format(series_instance_uid))
                response = view_all_instances(request_instances)
                assert response.status_code == 200
                resp_json = json.loads(response.content)
                instance_lst_1 = resp_json['list_instance_uid']
                print("instance_lst_1:", instance_lst_1)
                request_instances = factory.get(
                    'qidors/instances?0020000E={0}&limit=10&offset=0'.format(series_instance_uid))
                response = view_all_instances(request_instances)
                assert response.status_code == 200
                resp_json = json.loads(response.content)
                instance_lst_2 = resp_json['list_instance_uid']
                print("instance_lst_2:", instance_lst_2)
                assert len(instance_lst_1) == len(instance_lst_2)
                assert len(instance_lst_1) != 0

        # AllInstancesOfStudyView
        view_all_instances_of_study = AllInstancesOfStudyView.as_view()
        study = None
        for study in LIST_INSTANCES_BY_STUDY:
            break
        len_sum = 0
        for tab in LIST_SERIES_BY_STUDY.values():
            for series_instance_uid in tab:
                request_instances = factory.get(
                    'qidors/studies/<study>/instances?SeriesInstanceUID={0}&limit=10&offset=0'
                    .format(series_instance_uid))
                response = view_all_instances_of_study(request_instances, study)
                assert response.status_code == 200
                resp_json = json.loads(response.content)
                instance_lst_1 = resp_json['list_instance_uid']
                print("instance_lst_1:", instance_lst_1)
                # assert len(instance_lst_1) != 0

                request_instances = factory.get(
                    'qidors/studies/<study>/instances?0020000E={0}&limit=10&offset=0'
                    .format(series_instance_uid))
                response = view_all_instances_of_study(request_instances, study)
                assert response.status_code == 200
                resp_json = json.loads(response.content)
                instance_lst_2 = resp_json['list_instance_uid']
                print("instance_lst_2:", instance_lst_2)
                assert len(instance_lst_1) == len(instance_lst_2)
                len_sum += len(instance_lst_1)
        assert len_sum > 0

        # AllInstancesOfSeriesOfStudyView
        len_sum = 0
        for study, series_tab in LIST_SERIES_BY_STUDY.items():
            for series in series_tab:
                sop_class_uid = '1.2.276.0.7230010.3.0.3.6.0'
                view_all_instances_of_series_of_study = AllInstancesOfSeriesOfStudyView.as_view()
                request_instances = factory.get(
                    'qidors/studies/<study>/series/<series>/instances\
                    ?SOPClassUID={0}&limit=10&offset=0'
                    .format(sop_class_uid))
                response = view_all_instances_of_series_of_study(request_instances, study, series)
                assert response.status_code == 200
                resp_json = json.loads(response.content)
                instance_lst_1 = resp_json['list_instance_uid']
                print("instance_lst_1:", instance_lst_1)
                request_instances = factory.get(
                    'qidors/studies/<study>/series/<series>/instances\
                    ?00080016={0}&limit=10&offset=0'
                    .format(sop_class_uid))
                response = view_all_instances_of_series_of_study(request_instances, study, series)
                assert response.status_code == 200
                resp_json = json.loads(response.content)
                instance_lst_2 = resp_json['list_instance_uid']
                print("instance_lst_2:", instance_lst_2)
                assert len(instance_lst_1) == len(instance_lst_2)
                len_sum += len(instance_lst_1)
                # assert len(instance_lst_1) != 0
        assert len_sum > 0

        # AllSeriesView
        view_all_series = AllSeriesView.as_view()
        series_date = '19970430'
        request_all_series = factory.get('qidors/studies?SeriesDate={0}'.format(series_date))
        response = view_all_series(request_all_series)
        assert response.status_code == 200
        resp_json = json.loads(response.content)
        series_lst_1 = resp_json['list_series_uid']
        print('series_lst_1', series_lst_1)
        request_all_series = factory.get('qidors/studies?00080021={0}'.format(series_date))
        response = view_all_series(request_all_series)
        assert response.status_code == 200
        resp_json = json.loads(response.content)
        series_lst_2 = resp_json['list_series_uid']
        print('series_lst_2', series_lst_2)
        assert len(series_lst_1) == len(series_lst_2)
        assert len(series_lst_1) != 0

        # AllSeriesOfStudyView
        view_all_series_of_study = AllSeriesOfStudyView.as_view()
        station_name = 'CT01_OC0'
        len_sum = 0
        for study in LIST_ALL_STUDY:
            request_all_series_of_study = factory.get(
                'qidors/studies/<study>/series?StationName={0}'.format(station_name))
            response = view_all_series_of_study(request_all_series_of_study, study)
            assert response.status_code == 200
            resp_json = json.loads(response.content)
            series_lst_1 = resp_json['list_series_uid']
            print('series_lst_1', series_lst_1)
            request_all_series_of_study = factory.get(
                'qidors/studies/<study>/series?00081010={0}'.format(station_name))
            response = view_all_series_of_study(request_all_series_of_study, study)
            assert response.status_code == 200
            resp_json = json.loads(response.content)
            series_lst_2 = resp_json['list_series_uid']
            print('series_lst_2', series_lst_2)
            assert len(series_lst_1) == len(series_lst_2)
            len_sum += len(series_lst_1)
            # assert len(series_lst_1) != 0
        assert len_sum > 0

        # AllStudiesView
        view_all_studies = AllStudiesView.as_view()
        patient_uid = '0123456789'
        request_all_studies = factory.get('qidors/studies?PatientID={0}'.format(patient_uid))
        response = view_all_studies(request_all_studies)
        assert response.status_code == 200
        resp_json = json.loads(response.content)
        studies_lst_1 = resp_json['list_study_uid']
        print('studies_lst_1', studies_lst_1)
        request_all_studies = factory.get('qidors/studies?00100020={0}'.format(patient_uid))
        response = view_all_studies(request_all_studies)
        assert response.status_code == 200
        resp_json = json.loads(response.content)
        studies_lst_2 = resp_json['list_study_uid']
        print('studies_lst_2', studies_lst_2)
        assert len(studies_lst_1) == len(studies_lst_2)
        assert len(studies_lst_1) != 0


class WadoRSMetadataTests(APITestCase):
    """
    Test class for wadors metadata
    """
    fixtures = [FIXTURE_FILE]
    """
    Tests class
    """

    @staticmethod
    def test_wadors_metadata():
        """
        tests wadors metadata
        :return:
        """
        factory = APIRequestFactory()

        #
        # metadata of study
        #

        view_study_metadata = MetadataStudyView.as_view()

        print("study metadata")
        request_study_metadata = factory.get('wadors/studies/<study>/metadata/')
        for study in INSTANCES_BY_STUDY_SERIES.keys():
            response = view_study_metadata(request_study_metadata, study)
            assert response.status_code == 200
            metadata_ref = get_metadata_from_study_uid(study)
            resp_json = json.loads(response.content)
            ret = compare_elements(metadata_ref, resp_json)
            assert ret

        #
        # metadata of series of study
        #

        view_series_metadata = MetadataSeriesView.as_view()
        print("series metadata")
        request_series_metadata = factory.get('wadors/studies/<study>/series/<series>/metadata/')
        for study in INSTANCES_BY_STUDY_SERIES.keys():
            for series in INSTANCES_BY_STUDY_SERIES[study].keys():
                response = view_series_metadata(request_series_metadata, study, series)
                assert response.status_code == 200
                metadata_ref = get_metadata_from_series_uid(series)
                resp_json = json.loads(response.content)
                ret = compare_elements(metadata_ref, resp_json)
                assert ret

        #
        # metadata of instances of series of study
        #

        view_instances_metadata = MetadataInstanceView.as_view()
        print("instances metadata")
        request_instances_metadata = factory.get(
            'wadors/studies/<study>/series/<series>/instances/<instances>/metadata/')
        for study in INSTANCES_BY_STUDY_SERIES.keys():
            for series in INSTANCES_BY_STUDY_SERIES[study].keys():
                for instance in INSTANCES_BY_STUDY_SERIES[study][series]:
                    response = view_instances_metadata(
                        request_instances_metadata, study, series, instance)
                    assert response.status_code == 200
                    metadata_ref = get_metadata_from_instance_uid(instance)
                    resp_json = json.loads(response.content)
                    ret = compare_elements(metadata_ref, resp_json)
                    assert ret


class WadoRSInstanceTests(APITestCase):
    """
    Tests class
    """
    fixtures = [FIXTURE_FILE]

    @staticmethod
    def test_waddors_instances():
        """
        test method to get instances
        :return: dicom
        """
        factory = APIRequestFactory()

        #
        # instances of study
        #

        view_study_instances = DCMInstancesOfSeriesOfStudyView.as_view()
        print("dicom instances of study")
        request_study_instances = factory.get('wadors/studies/<study>/')
        for study in INSTANCES_BY_STUDY_SERIES.keys():
            response = view_study_instances(request_study_instances, study)
            assert response.status_code == 200

        #
        # instances of series of study
        #

        view_series_instances = DCMInstancesOfSeriesView.as_view()
        print("dicom instances of series")
        request_series_instances = factory.get('wadors/studies/<study>/series/<series>/')
        for study in INSTANCES_BY_STUDY_SERIES.keys():
            for series in INSTANCES_BY_STUDY_SERIES[study].keys():
                response = view_series_instances(request_series_instances, study, series)
                assert response.status_code == 200

        #
        # instance of series of study
        #

        view_instances_instances = DCMInstanceView.as_view()
        print("dicom instances")
        request_instances = factory.get(
            'wadors/studies/<study>/series/<series>/instances/<instances>/')
        for study in INSTANCES_BY_STUDY_SERIES.keys():
            for series in INSTANCES_BY_STUDY_SERIES[study].keys():
                for instance in INSTANCES_BY_STUDY_SERIES[study][series]:
                    response = view_instances_instances(request_instances, study, series, instance)
                    assert response.status_code == 200


class MetadataConfTests(APITestCase):
    """
    Tests class
    """

    @staticmethod
    def test_metadata_tags():
        """
        test method to check matadata tags configuration
        :return:
        """
        # configuration value
        for elem in METADATA_TAGS:
            tag, keyword, column, model = elem
            value = 'lambda'
            if model == 'Study' and column == 'study_id':
                value = 0
            if model == 'Patient':
                res = Patient.objects.filter(**{column: value}).values()
            if model == 'Study':
                res = Study.objects.filter(**{column: value}).values()
            if model == 'Series':
                res = Series.objects.filter(**{column: value}).values()
            if model == 'Instance':
                res = Instance.objects.filter(**{column: value}).values()
            assert res is not None

        # false value
        try:
            Patient.objects.filter(**{'falsecolumn': 'nop'}).values()
            assert False
        except FieldError:
            pass
        try:
            Study.objects.filter(**{'falsecolumn': 'nop'}).values()
            assert False
        except FieldError:
            pass
        try:
            Series.objects.filter(**{'falsecolumn': 'nop'}).values()
            assert False
        except FieldError:
            pass
        try:
            Instance.objects.filter(**{'falsecolumn': 'nop'}).values()
            assert False
        except FieldError:
            pass
