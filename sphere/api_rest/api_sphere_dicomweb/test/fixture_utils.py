""" Management of fixture files for embedding data in tests """

import os

import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = BASE_DIR + '/test/data/'
FIXTURES_DIR = BASE_DIR + '/test/fixtures/'


def update_fixture_fsys_path(fixture_template_file):
    """
    Changes occurrences of dicom file path with actual ones

    :param fixture_template_file: the template fixture file
    :type fixture_template_file: str
    :return: the fixture json file
    """
    template_file = FIXTURES_DIR + fixture_template_file
    json_file = fixture_template_file.replace(".template", ".json")
    abs_json_file = FIXTURES_DIR + json_file

    # print("template_file:", template_file)
    # print("json_file:", json_file)

    with open(template_file) as ffixture:
        sfixture = ffixture.read()
    tmp_fixtures = json.loads(sfixture)
    fixtures = []
    for elem in tmp_fixtures:
        if elem['model'] == 'api_sphere_dicomweb.storagemetadata':
            dcm_path = elem['fields']['file_path']
            dcm_path = dcm_path.replace('DATA_ROOT/', DATA_DIR)
            elem['fields']['file_path'] = dcm_path
        fixtures.append(elem)
    with open(abs_json_file, "w") as fout:
        fout.write(json.dumps(fixtures))
    return json_file
