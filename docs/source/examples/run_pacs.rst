Runserver
=========

Les étapes à suivre pour tester **runserver**:

1 Créer deux PACS (PACS1)

Lance avec Sphere::

   $ cd PACS1
   $ python manage.py runserver

**Résultat dans la console**::

    Starting thread_db_save
    =========== SIZE QUEUE PACS1 : 0
    I'm waiting for the data to be saved in the database
    #+++++++++++++++++++++++++++
    # DICOM Server PACS1
    # Port : 11111
    # (SCP)C-ECHO   ON
    # (SCP)C-STORE  ON
    # (SCP)C-FIND   ON
    # (SCP)C-MOVE   ON
    # Thread database save  ON
    # Extended database     ON
    # Api Sphere DicomWeb   OFF
    # Api Annotation        OFF
    #+++++++++++++++++++++++++++
