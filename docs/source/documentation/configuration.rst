.. _configuration:

Configuration
=============


.. _file_settings:

File settings.yml
-----------------

Le fichier principal de la configuration du PACS SPHERE, voilà le fichier de base :download:`settings.yml <../../_static/settings.yml>`.

Configuration principale
~~~~~~~~~~~~~~~~~~~~~~~~

ApplicationEntity
+++++++++++++++++

Les informations principales du PACS

Les paramètres::

    port: 11112  # The of PACS
    AET: PExport  # The name of PACS (Application Entity Title) unique for each PACS

    # Parameters of ApplicationEntity (ae)
    ae_params:
        required_call_aet: False  # The *Called AE Title* must match the AE title.; If there is a problem, the default value is 'False'
        max_assoc_idle_second : 50 # The max_assoc_idle_second ; If there is a problem, the default value is '50'
        max_assoc: 100  # The number of maximum associations. ; If there is a problem, the default value is '100'
        pdu_size: 0  # The maximum PDU size ; If there is a problem, the default value is '0'
        acse_timeout: 60  # The ACSE timeout (in seconds) ; If there is a problem, the default value is '60'
        dimse_timeout: 60  # The DIMSE timeout (in seconds) ; If there is a problem, the default value is '60'
        network_timeout: 60  # The network timeout (in seconds) ; If there is a problem, the default value is '60'

    context: default  # The context used ; If there is a problem, the default value is 'default'


Database
++++++++

Les paramètres::

    db:
        engine: postgresql  # possible value: 'postgresql' or 'sqlite'
        params:
            ip: 10.172.146.19
            port: 5432
            database: pacs
            schema: sphere_test
            login:
            password:
        save_delay: 5 # the delay (in second)  between 2 save in the database have to be int, if none or not int given default value 5 is set
        engine_pool_size: 20 # If there is a problem, the default value is '20'
        engine_pool_overflow: 90 # If there is a problem, the default value is '90'
        engine_pool_recycle: 70 # If there is a problem, the default value is '70'
        engine_pool_timeout: 10 # If there is a problem, the default value is '10'
        verbose_error: False # If there is a problem, the default value is 'False'

    name_file_copy_extended_db: ./app/.copy_extended.json

Configuration secondaire
~~~~~~~~~~~~~~~~~~~~~~~~

DICOM message service element (DIMSE)
+++++++++++++++++++++++++++++++++++++

Les paramètres::

    scp_services:
    - c-echo
    - c-store
    - c-find
    - c-move

DICOM Storage
+++++++++++++

Les paramètres::

    # DICOM storage
    storage_method: FS  # possible value: 'FS', 'HDFS', 'HBASE' or 'MIXED'; # If there is a problem, the default value is 'FS'
    tar_size: 10
    fs:
        path: ./data # If there is a problem, the default value is './data'
    path_white_list: ./app/white_list # If there is a problem, the default value is './app/white_list'
    hdfs:
        # Param HDFS
        start_move_hdfs: False  # Move with HDFS
        free_hard_drive: 50  # Minimum empty hard drive space to launch cmove; (in gigabyte)
        time_sleep_thread_hdfs: 10  # The time before launching the thread Hdfs (in seconds)
        time_slep_hdfs: 60  # Time to wait for the HDFS command to put files in the data folder then we launch the c_store (in seconds)
        number_uid: 5  # Number of (patient, studies or series) to be launched in parallel (If equal zero all uid)
        remove_file: True # Delete the file after sending
        path_file_csv_hdfs: ./data/
        name_file_csv_hdfs: uid.txt
        path_script: /app/scripts/avro-tools/SPHERE_HDFS_TO_FS.sh
        path: ./hdfs_data # If there is a problem, the default value is './hdfs_data'
    hbase:
        path: ./hbase_data # If there is a problem, the default value is './hbase_data'
    tmp_path: .tmp_data # If there is a problem, the default value is '.tmp_data'


Api Rest
++++++++

Les paramètres::

    api:
        start: False
        ip: 127.0.0.1
        port: 5555
        dicomweb:
            start: False
            decompress_pixels: False
        annotation:
            start: False
            path_data: ./data_annotation
            # Internal: I use the basic module of python uuid
            # External: I only search from API uuid_generator
            # Mixed : I search from API uuid_generator or I use the basic module of python uuid if I can't generate the id with API uuid_generator.
            type_uuid_generator: INTERNAL
            url_uuid_generator: http://127.0.0.1:8000/generate_uuid/annotation/INSTANCE


Verbose
+++++++

Les paramètres::

    console_verbose_level : 1 # O is quiet mode, 1 is verbose mode, 2 is ultra-verbose mode
    database_verbose_level : 0 # O is quiet mode, 1 is verbose mode, 2 is ultra-verbose mode  Not used

Log
+++

Les paramètres::

    log:
        path_folder: ./log/
        create_file_uid: True  # Create a file that contains the study_uid, series_uid and instances_uid method cstore_response() (True | False);
        file_name_uid: study_series_instances.uid # Filename to create the uid file; If create_file_uid equal True and there is a problem, the default value is 'study_series_instances.uid'
        file_log_config_logging: config_logging.log  # The logging_config.yml configuration file logs If there is a problem, the default value is 'config_logging.log'
        # The default logs if we have a problem with the logging configuration file
        default_log: True  # possible value (True | False); If there is a problem, the default value is 'True'
        file_log_main: main.log
        log_stream_level: WARNING  # possible value: 'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG' or 'NOTSET' If there is a problem, the default value is 'WARNING'
        log_file_level: DEBUG  # possible value: 'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG' or 'NOTSET' If there is a problem, the default value is 'DEBUG'
        color_message: True  # The color of log; If there is a problem, the default value is 'True'
        formatter_color: '%(log_color)s%(asctime)s :: %(levelname)-8s :: %(name)-20s :: %(reset)s %(blue)s %(message)s'
        formatter: '%(asctime)s :: %(levelname)-8s :: %(name)-20s :: %(message)s'
        max_baytes: 10485760  # 10MB  # If there is a problem, the default value is '10485760'
        backup_count: 2  # If there is a problem, the default value is '2'


File logging_config.yml
-----------------------

Le fichier de la configuration des logs, voilà le fichier de base  :download:`logging_config.yml <../../_static/logging_config.yml>`.


File tags.yml
-------------

Le fichier qui contients tous les tags pour générer le fichier extended_db.yml, voilà un exemple de fichier :download:`tags.yml <../../_static/tags.yml>`.

File white_list/example.yml
---------------------------

Le fichier qui contients les PACS autoriser, voilà le fichier de base  :download:`example.yml <../../_static/example.yml>`.

File extended_db.yml
--------------------

Le fichier qu'on l'utilise pour l'extended database, voilà un exemple de fichier :download:`extended_db.yml <../../_static/extended_db.yml>`.