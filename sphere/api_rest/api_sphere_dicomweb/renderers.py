from rest_framework import renderers


class MultiPartDicomRelatedRenderer(renderers.BaseRenderer):
    """
    The renderer for multipart related content
    """
    media_type = 'multipart/related; type="application/dicom"'
    format = 'dicom'


class MultiPartOctetStreamRelatedRenderer(renderers.BaseRenderer):
    """
    The renderer for multipart related content
    """
    media_type = 'multipart/related; type="application/octet-stream"'
    format = 'multipart_octet_stream'


class DicomJsonRenderer(renderers.BaseRenderer):
    """
    The renderer for dicom+json
    """
    media_type = 'application/dicom+json'
    format = 'dicomjson'


class ALLRenderer(renderers.BaseRenderer):
    """
    The renderer for html and all renderers
    """
    media_type = '*/*'
    format = 'html'


class DicomXmlRenderer(renderers.BaseRenderer):
    """
    The renderer for dicom+xml
    """
    media_type = 'application/dicom+xml'
    format = 'dicomxml'