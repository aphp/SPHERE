#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
{Description module}
"""
DICT_SEARCH_FIND = {
    "UID": {
        "patientID": "PatientID",
        "studyUID": "StudyInstanceUID",
        "seriesUID": "SeriesInstanceUID"
    },
    # PATIENT
    "PATIENT": {
        "patientName": "PatientName",
        "patientSex": "PatientSex",
        "patientBirthDate": "PatientBirthDate"
    },
    # STUDY
    "STUDY": {
        "dateStudy": "StudyDate",
        "institutionName": "InstitutionName",
        "accessionNumber": "AccessionNumber",
        "protocolName": "ProtocolName",
        "studyDescription": "StudyDescription"
    },
    # SERIES
    "SERIES": {
        "modality": "Modality",
        "manufacturer": "Manufacturer",
        "manufacturerModelName": "ManufacturerModelName",
        "bodyPartExamined": "BodyPartExamined",
        "seriesDate": "SeriesDate",
        "seriesDescription": "SeriesDescription",
        "stationName": "StationName"
    }
}

