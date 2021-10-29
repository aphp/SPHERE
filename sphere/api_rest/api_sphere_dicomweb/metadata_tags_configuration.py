""" Management of DICOM/tags filters configuration """


QS_FILTERS_STUDY = [
    (0x0008, 0x0005),
    (0x0008, 0x0020),
    (0x0008, 0x0030),
    (0x0008, 0x0050),
    (0x0008, 0x0056),
    (0x0008, 0x0061),
    (0x0008, 0x0090),
    (0x0008, 0x0201),
    (0x0008, 0x1190),
    (0x0010, 0x0010),
    (0x0010, 0x0020),
    (0x0010, 0x0030),
    (0x0010, 0x0040),
    (0x0020, 0x000D),
    (0x0020, 0x0010),
    (0x0020, 0x1206),
    (0x0020, 0x1208)
]

QS_FILTERS_SERIES = [
    (0x0008, 0x0005),
    (0x0008, 0x0056),
    (0x0008, 0x0201),
    (0x0008, 0x103E),
    (0x0008, 0x1190),
    (0x0020, 0x000E),
    (0x0020, 0x0011),
    (0x0020, 0x1209),
    (0x0040, 0x0244),
    (0x0040, 0x0245),
    (0x0040, 0x0275),
    (0x0040, 0x0009),
    (0x0040, 0x1001)
]

QS_FILTERS_INSTANCE = [
    (0x0008, 0x0005),
    (0x0008, 0x0016),
    (0x0008, 0x0018),
    (0x0008, 0x0056),
    (0x0008, 0x0201),
    (0x0008, 0x1190),
    (0x0020, 0x0013),
    (0x0028, 0x0010),
    (0x0028, 0x0011),
    (0x0028, 0x0100),
    (0x0028, 0x0008)
]


QS_FILTERS = {
    'instance': QS_FILTERS_INSTANCE,
    'series': QS_FILTERS_SERIES,
    'study': QS_FILTERS_STUDY
}

# ORM SqlAlchemy
METADATA_TAGS = [
    # Patient
    ['00100020', 'PatientID', 'patientID', 'Patient'],
    ['00100010', 'PatientName', 'patientName', 'Patient'],
    ['00100040', 'PatientSex', 'patientSex', 'Patient'],
    ['00100030', 'PatientBirthDate', 'patientBirthDate', 'Patient'],
    # Study
    ['0020000D', 'StudyInstanceUID', 'studyUID', 'Study'],
    ['00100020', 'PatientID', 'patientID', 'Study'],
    ['00080020', 'StudyDate', 'dateStudy', 'Study'],
    ['00080080', 'InstitutionName', 'institutionName', 'Study'],
    ['00080050', 'AccessionNumber', 'accessionNumber', 'Study'],
    ['00181030', 'ProtocolName', 'protocolName', 'Study'],
    ['00081030', 'StudyDescription', 'studyDescription', 'Study'],
    #['00200010', 'StudyID', 'study_id', 'Study'],
    #['00080020', 'StudyDate', 'date_study', 'Study'],
    # Series
    ['00100020', 'PatientID', 'patientID', 'Series'],
    ['0020000E', 'SeriesInstanceUID', 'seriesUID', 'Series'],
    ['0020000D', 'StudyInstanceUID', 'studyUID', 'Series'],
    ['00080060', 'Modality', 'modality', 'Series'],
    ['00080070', 'Manufacturer', 'manufacturer', 'Series'],
    ['00081090', 'ManufacturerModelName', 'manufacturerModelName', 'Series'],
    ['00180015', 'BodyPartExamined', 'bodyPartExamined', 'Series'],
    ['00080021', 'SeriesDate', 'seriesDate', 'Series'],
    ['0008103E', 'SeriesDescription', 'seriesDescription', 'Series'],
    ['00081010', 'StationName', 'stationName', 'Series'],
    # Instances
    ['00080018', 'SOPInstanceUID', 'instanceUID', 'Instance'],
    ['0020000E', 'SeriesInstanceUID', 'seriesUID', 'Instance'],
    ['0020000D', 'StudyInstanceUID', 'studyUID', 'Instance'],
    ['00100020', 'PatientID', 'patientID', 'Instance']
    #['00080016', 'SOPClassUID', 'implementation_ClassUID', 'Instance']
]


def parse_metadata_configuration():
    """
    Parse the meta tag array and gives two index:
    one by tag and the other by keyword

    :return: a tuple composed of (by tag, by keyword)
    :rtype tuple
    """
    metadata_by_query_by_tag = {}
    metadata_by_query_by_keyword = {}
    keyword_by_model = {}
    tag_by_model = {}

    for lis in METADATA_TAGS:
        tag = lis[0]
        keyword = lis[1]
        column = lis[2]
        query = lis[3]
        if query not in metadata_by_query_by_tag:
            metadata_by_query_by_tag[query] = {}
        metadata_by_query_by_tag[query][tag] = {
            'keyword': keyword,
            'column': column
        }
        if query not in metadata_by_query_by_keyword:
            metadata_by_query_by_keyword[query] = {}
        metadata_by_query_by_keyword[query][keyword] = {
            'tag': tag,
            'column': column
        }
        keyword_by_model[keyword] = query
        tag_by_model[tag] = query
    return metadata_by_query_by_tag, metadata_by_query_by_keyword, keyword_by_model, tag_by_model


def get_filter_columns(filters, modelname):
    """
    Gives the columns filter that will be used with django model
    to filter data in database

    :param filters: column filters
    :type filters: dict
    :param modelname: the model table (django) to use to filter
    :type modelname: str
    :return: django model filter
    :rtype: dict
    """
    METADATA_BY_QUERY_BY_TAG, METADATA_BY_QUERY_BY_KEYWORD, \
    keyword_by_model, tag_by_model = parse_metadata_configuration()
    colfilters = {}
    metadata_by_keyword = METADATA_BY_QUERY_BY_KEYWORD[modelname]
    metadata_by_tag = METADATA_BY_QUERY_BY_TAG[modelname]
    for k in filters.keys():
        if k in metadata_by_keyword:
            colfilters[metadata_by_keyword[k]['column']] = filters[k]
        elif k in metadata_by_tag:
            colfilters[metadata_by_tag[k]['column']] = filters[k]
    return colfilters
