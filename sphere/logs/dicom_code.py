""" Define DICOM code """


class DicomCode:
    """ Dicom code"""
    DICOM_CODE_SUCCESS = 0x0000
    DICOM_CODE_ASSOC_REJECTED_ABORTED = 0xD000
    DICOM_CODE_UNAUTHORIZED_ACCESS = 0xA801
    DICOM_CODE_ASSOCIATION_ABORTED = 0xA801
    DICOM_CODE_CSTORE_METHOD_ERROR = 0xC211
    DICOM_CODE_PENDING = 0xff00

    DICOM_CODE_LOG_MESSAGE = {
        '0xc211': 'C-STORE SCP implementation error',
        '0xd000': 'Association rejected or aborted',
        '0xa801': 'Association aborted',
        '0x0000': 'Association Completed',
        '0xff00': 'Association Pending'
    }
