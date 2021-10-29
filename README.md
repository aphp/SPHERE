# Presentation of SPHERE


## What is Sphere?

SPHERE (PACS solution for Health Research) is a PACS software developed by the EDS-Imaging team within the APHP.

A PACS (Picture Archiving and Communication System)
is a system for managing medical images through archiving functions. It allows communication
via network network (DICOM format) and therefore remote or local treatment.


The DICOM format, Digital Imaging and Communications in Medicine, is a standard for IT management of
data from medical imaging.


## Main features of the Pacs Sphere


- DICOM data collection
- The export of DICOM data

For this the possible actions are:

* **Runserver:** To launch the PACS
* **C-ECHO:** Ensure that PACS is listening
* **C-STORE:** Send medical images DICOM of a PACS to another PACS
* **C-FIND:** Search data on medical images DICOM in a PACS (on a database or directly in the files)
* **C-MOVE:** Move medical images DICOM between PACS
* **DICOMWEB:** Is the DICOM standard for web-based medical imaging. This is a set of RESTful services
    
    The main endpoints supported by SPHERE are:
    
    * **WADO-RS** for retrieving DICOM files, metadata in XML or JSON forms, bulk data separated from metadata and rendering images in consumer format
    * **STOW-RS** for storing (sending) DICOM files or separate metadata and bulk data
    * **QIDO-RS** for querying collections (databases, registers) of DICOM objects


* **API Annotation:** An API that allows you to manage annotations


## Prerequisites


> ** _ Note: _ ** The current implementation of the SPEHERE supports:
>- Versions of Python 3 of 3.6.1 to 3.8

## Contacts

The following people can be contacted according to the subject:

- Project Manager: **Aurélian Maire** @mail: **Aurelien.maire@aphp.fr**
- Lead Developer Python: **Ossama Achouri** @mail: **ossama.achouri-ext@aphp.fr**
