filtres possible pa.. _user-guide:

User guide
==========

Create the PACS
---------------

.. code-block:: Bash

   sphere-admin nom_de_la_PACS

Voilà la structure du pacs::

    Name of PACS
    ├── app
    │   ├── __init__.py
    │   ├── all_dicom_elements.csv
    │   ├── logging_config.yml
    │   ├── main_extended_db.py
    │   ├── settings.py
    │   ├── settings.yml
    │   ├── tags.yml
    │   └── white_list
    │       └── example.yml
    ├── manage.py
    └── version_pacs.py

Description de la stucture de PACS :

- **app:** Le dossier qui contient tous les fichiers settings du PACS

    - **all_dicom_elements.csv:** Le fichier qui contient tous les tags (Tag, Keyword, Attribute name, VR, Field name of a table, Type et Size if settings)
    - **logging_config.yml:**  Le fichier de la configuration des logs
    - **main_extended_db.py:** Le module python qui génére le fichier extended_db.yml à partir de *tags.yml*
    - **settings.py:**  Le module qui lie le fichier *settings.yml*
    - **settings.yml:** Le fichier principal de paramétrage, pour le comprendre consultez :ref:`ce doc <file_settings>`.
    - **tags.yml:**  Pour Ajouter des champs extended dans la base de données il faut ajouter les tags dans le fichier
    - **white_list:** Le dossier qui contient les fichiers de white_list

        - **example.yml:**  Un fichier d'exemple de white_list.
- **data:** Le dossier qui contient tous les données DICOM (instances)
- **manage.py:** Le programme principal pour lancer toutes les commandes de PACS

.. important::
    Pour plus d'information sur les fichiers de configuration clique :doc:`ici <configuration>`.

.. Note::
    Dans le fichier `manage.py` sont répertoriés l'ensemble des fonctionnalités de base.

Pour retrouver ces arguments::

    $ python manage.py -h

Runserver PACS
--------------

La commande pour lancer le PACS::

    $ python manage.py runserver


Modifier les paramètres du PACS Sphère créé
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Modifier le nom et le port du PACS :**


Editer le fichier `settings.yml`::

    $ vim settings.yml

Puis se rendre dans la section `ApplicationEntity`, `Dicom Server Configuration` modifier le `port` et l'`AET`
(Application Entity Title : correspondant au nom du PACS).

- **Modifier la configuration de la database PostgreSQL ou SQLITE :**

Éditer le fichier `settings.yml`::

    $ vim settings.yml

Puis se rendre dans la section `Database`.


Fonctionnalités / Services disponible
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ci-dessous vous trouverez comment exécuter les différentes actions :

- C-ECHO
- C-STORE
- C-FIND
- C-MOVE

C-ECHO
------

Usage du C-ECHO
^^^^^^^^^^^^^^^

S'assurer qu'un PACS est à l'écoute / actif.


.. Note::
    Avant de lancer la commande C-ECHO vérifier que le PACS émetteur est bien autorisé dans la white_list,
    sinon il faut l'ajouter.

Ajouter le PACS dans la whitelist pour autoriser l'action
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Éditer le fichier `white_list/example.yml`.::

    $ vim app/white_list/example.yml

Respecter ce format ::

    <Nom_PACS> :
        ip   : <ip_PACS>
        port : <port_PACS>


Par exemple, dans un terminal j'ai éxecuté::

    $ python runserver

Donc mon PACS est actif. Je souhaite vérifier tout de même en passant par un autre terminal que celui-ci est bien en
écoute. Pour cela je vais interroger le PACS avec un C-ECHO, mais avant ça je vais ajouter dans la white_liste les
informations du PACS interrogé.

.. code-block:: Bash

    $ vim app/white_list/example.yml


Lancer C-ECHO pour vérifier si le pacs est bien actif
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Une fois que mon PACS a été renseigné dans la white_list, dans le terminal je me déplace dans le dossier du PACS créé
puis je lance la commande ::

    $ python3 manage.py echo <ip_pacs> <port_pacs> -aec <nom_pacs>

Les paramètres `ip, port et aec` sont renseignés dans le fichier `app/settings.yml`.

Output de la commande C-ECHO
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Si PACS Actif**

>Vous trouverez deux messages, un dans le terminal qui interroge et un autre dans le PACS interrogé.

Voici l'output que vous devez obtenir dans le terminal qui interroge si votre PACS est bien actif. Le `final_status`
doit indiquer `Association Completed`.::


    ######################### CURRENT SCU CECHO ASSOC #########################
    # Server Association metadata
    # update date           : 2020-07-30 11:57:04.832535
    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------
    # action                : CECHO
    # service               : SCU
    # final_status          : 0x0000 : Association Completed
    #############################################################################


Voici l'output affiché dans le PACS qui est lancé `final_status`: `Association Completed`.::


    ######################### CURRENT SCP CECHO ASSOC #########################
    # Server Association metadata
    # update date           : 2020-07-30 11:57:04.829283
    # simultaneous assoc : 0
    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------
    # action                : CECHO
    # service               : SCP
    # final_status          : 0x0000 : Association Completed
    #############################################################################


- **Si PACS Non Associé**

Si vous obtenez cet ouptut dans le terminal qui intérroge, c'est que vous n'avez pas bien configuré votre PACS dans la
white_list.::

    ######################### CURRENT SCU CECHO ASSOC #########################
    # Server Association metadata
    # update date           : 2020-07-30 11:41:48.145867
    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------
    # action                : CECHO
    # service               : SCU
    # final_status          : 0xa801 : Association aborted
    #############################################################################


Dans le terminal du PACS lancé vous verrez cet output ::

    ######################### CURRENT SCP CECHO ASSOC #########################
    # Server Association metadata
    # update date           : 2020-07-30 11:22:53.925932
    # simultaneous assoc : 0
    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------
    # action                : CECHO
    # service               : SCP
    # final_status          : 0xa801 : Association aborted
    #############################################################################
    2020-07-30 11:22:53,926 :: ERROR    :: pacs.transaction_dicom ::   Association Failed
    2020-07-30 11:22:53,926 :: WARNING  :: pynetdicom.service-c ::   Unknown 'status' value returned by the handler bound to 'evt.EVT_C_ECHO' - 0xa801


- **Si PACS non actif**


Voici l'output qui apparait dans le terminal qui intérroge le PACS si celui-ci n'est pas actif.::

    2020-07-30 12:30:31,177 :: ERROR    :: pynetdicom.transport ::   Association request failed: unable to connect to remote
    2020-07-30 12:30:31,178 :: ERROR    :: pynetdicom.transport ::   TCP Initialisation Error: Connection refused

    ######################### CURRENT SCU CECHO ASSOC #########################
    # Server Association metadata
    # update date           : 2020-07-30 12:30:31.180896
    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------
    # action                : CECHO
    # service               : SCU
    # final_status          : 0xa801 : Association aborted
    #############################################################################
    2020-07-30 12:30:31,180 :: ERROR    :: pacs.transaction_dicom ::   Cecho request; Association Failed




C-STORE
-------

Usage du C-STORE
^^^^^^^^^^^^^^^^
Action qui permet de demander à un PACS d'envoyer des DICOM à un autre PACS.


Tout d'abord lancer le PACS qui recevra les DICOM dans un terminal.::

    $ python3 manage.py runserver


Source des données : Depuis un dossier
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pour connaitre les arguments nécessaires à cette commande ::

    $ python3 manage.py store -h

Ici il faut préciser le `-sp (source_path)` qui est un `fs (file_system)` et ajouter le `-pd ( PATH_DICOM_DIRE_OR_FILE)`.::

    $ python3 manage.py store <ip_pacs> <port_pacs> -aec <nom_pacs> -sp fs -pd <PATH_DICOM_DIRE_OR_FILE>

Clean database
^^^^^^^^^^^^^^

Cette commande permet de supprimer la base de donnée et de la recréer.

⚠️ ATTENTION ⚠️ TOUTES les entrées dans la base de donnée seront supprimées.::

    $ python3 manage.py database clean

Après avoir `clean database` il faut ré-indexer les données contenues dans le dossier `data` du PACS dans la base de
donnée pour régénérer la base de données DICOM ::

    $ python3 manage.py data index

Indexation : c'est une action qui est faite par défaut quand un DICOM est envoyé d'un PACS à un autre PACS. Afin de
faciliter la recherche et pour éviter de parcourir l'ensemble des fichiers DICOM, l'indexation permet de stocker dans une
base de donnée un certain nombre d'informations (tag) plus facilement accessible.



Output de la commande C-STORE
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Si DICOMs ajoutés**


Dans le terminal qui exécute l'envoie via la commande C-STORE, pour chaque image ajoutée voici un exemple de l'output qui
apparait `Association Pending` ::

    ######################### CURRENT SCU CSTORE ASSOC #########################
    # Server Association metadata
    # update date           : 2020-07-30 15:14:53.491961
    # ----------------------------------------------------------------------------
    # ----------------------------------------------------------------------------
    # action                : CSTORE
    # service               : SCU
    # final_status          : 0xff00 : Association Pending
    # Study UID             : 1.2.124.113532.10.149.172.6.20180403.83831.11226567
    # Series UID            : 1.2.840.113619.2.408.5282380.5894125.26837.1525323437.936
    # Instance UID          : 1.2.840.113619.2.408.5282380.5894125.23557.1525323569.503
    ##############################################################################
    Execution time : 00:00:02

Une fois que le PACS lancé, donc PACS receveur de l'image, réceptionne celles-ci, un output apparait comme ci-dessous
`Association Completed` ::


    # ----------------------------------------------------------------------------
    # ----------------------------------------------------------------------------
    # action                : CSTORE
    # service               : SCP
    # final_status          : 0x0000 : Association Completed
    # Study UID             : 1.2.124.113532.10.149.172.6.20180403.83831.11226567
    # Series UID            : 1.2.840.113619.2.408.5282380.5894125.26837.1525323437.936
    # Instance UID          : 1.2.840.113619.2.408.5282380.5894125.23557.1525323569.503
    ##############################################################################
    =========== SIZE QUEUE PACS4 : 1
    Prepare to insert :
     - 1 patient
     - 1 study
     - 1 series
     - 1 instance
    ---- Start patient bulk temporary insert ---
    ---- Start de-duplicate patient insert ---
    ---- Start merge upsert patient ---
    ---- End patient insert ---
    ---- Start study bulk temporary insert ---
    ---- Start de-duplicate study insert ---
    ---- Start merge upsert study ---
    INSERT INTO sphere_oac_pacs3.study (d8ins,d8maj,d8del,patient_uid,date_study,institution_name,accession_number,protocol_name,study_description,study_uid, patient_id)
                            SELECT tmp_33333_study.d8ins,tmp_33333_study.d8maj,tmp_33333_study.d8del,tmp_33333_study.patient_uid,tmp_33333_study.date_study,tmp_33333_study.institution_name,tmp_33333_study.accession_number,tmp_33333_study.protocol_name,tmp_33333_study.study_description,tmp_33333_study.study_uid, patient_id
                            FROM sphere_oac_pacs3.tmp_33333_study JOIN sphere_oac_pacs3.patient ON (sphere_oac_pacs3.patient.patient_uid=sphere_oac_pacs3.tmp_33333_study.patient_uid)
                            ON CONFLICT (study_uid)
                            DO NOTHING
    ---- End study insert ---
    ---- Start series bulk temporary insert ---
    ---- Start de-duplicate series insert ---
    ---- Start merge upsert series ---
    INSERT INTO sphere_oac_pacs3.series (d8ins,d8maj,d8del,study_uid,patient_uid,modality,manufacturer,manufacturer_model_name,body_part_examined,series_date,series_description,station_name,dt_first_insertion,dt_completion,series_uid, patient_id, study_id)
                            SELECT tmp_33333_series.d8ins,tmp_33333_series.d8maj,tmp_33333_series.d8del,tmp_33333_series.study_uid,tmp_33333_series.patient_uid,tmp_33333_series.modality,tmp_33333_series.manufacturer,tmp_33333_series.manufacturer_model_name,tmp_33333_series.body_part_examined,tmp_33333_series.series_date,tmp_33333_series.series_description,tmp_33333_series.station_name,tmp_33333_series.dt_first_insertion,tmp_33333_series.dt_completion,tmp_33333_series.series_uid, patient.patient_id, study_id
                            FROM sphere_oac_pacs3.tmp_33333_series JOIN sphere_oac_pacs3.patient ON (sphere_oac_pacs3.patient.patient_uid=sphere_oac_pacs3.tmp_33333_series.patient_uid)
                            JOIN sphere_oac_pacs3.study ON (sphere_oac_pacs3.study.study_uid=sphere_oac_pacs3.tmp_33333_series.study_uid)
                            ON CONFLICT (series_uid)
                            DO NOTHING
    ---- End series insert ---
    ---- Start instance bulk temporary insert ---
    ---- Start de-duplicate instance insert ---
    ---- Start merge upsert instance ---
    INSERT INTO sphere_oac_pacs3.file_storage_metadata (d8ins,d8maj,d8del,series_uid,study_uid,patient_uid,file_type,storage_method,file_path,filesize,storage_status,dt_deb_storage,dt_end_storage,instance_uid, patient_id, study_id, series_id)
                            SELECT tmp_33333_file_storage_metadata.d8ins,tmp_33333_file_storage_metadata.d8maj,tmp_33333_file_storage_metadata.d8del,tmp_33333_file_storage_metadata.series_uid,tmp_33333_file_storage_metadata.study_uid,tmp_33333_file_storage_metadata.patient_uid,tmp_33333_file_storage_metadata.file_type,tmp_33333_file_storage_metadata.storage_method,tmp_33333_file_storage_metadata.file_path,tmp_33333_file_storage_metadata.filesize,tmp_33333_file_storage_metadata.storage_status,tmp_33333_file_storage_metadata.dt_deb_storage,tmp_33333_file_storage_metadata.dt_end_storage,tmp_33333_file_storage_metadata.instance_uid, patient.patient_id, study.study_id, series_id
                            FROM sphere_oac_pacs3.tmp_33333_file_storage_metadata JOIN sphere_oac_pacs3.patient ON (sphere_oac_pacs3.patient.patient_uid=sphere_oac_pacs3.tmp_33333_file_storage_metadata.patient_uid)
                            JOIN sphere_oac_pacs3.study ON (sphere_oac_pacs3.study.study_uid=sphere_oac_pacs3.tmp_33333_file_storage_metadata.study_uid)
                            JOIN sphere_oac_pacs3.series ON (sphere_oac_pacs3.series.series_uid=sphere_oac_pacs3.tmp_33333_file_storage_metadata.series_uid)
                            ON CONFLICT (instance_uid)
                            DO NOTHING
    ---- End instance insert ---



- **Si erreur de config de la base de donnée**

Voici un exemple de l'erreur obtenu si le paramétrage de la base de donnée n'a pas été correctement réalisé. Il est
possible de changer ces paramètres dans le fichier `settings.yml`.::

    2020-07-30 15:14:54,759 :: ERROR    :: pacs.database      ::   (psycopg2.OperationalError) FATAL:  no pg_hba.conf entry for host "10.188.194.246", user "None", database "pacs", SSL off



C-FIND
------

Usage du C-FIND
^^^^^^^^^^^^^^^

Pour vérifier qu'un examen ou qu'une serie a bien été ajouté(e), l'action possible est le C-FIND. Ou pour trouver un
patient, une study, une series.

Pour connaitre les arguments nécessaires à cette commande ::

    $ python3 manage.py find -h


- Rechercher un patient::

    $ python3 manage.py find <ip_pacs> <port_pacs> -aec <nom_pacs> -paID <patient_id>


- Rechercher une study::

    $ python3 manage.py find <ip_pacs> <port_pacs> -aec <nom_pacs> -stUID <study_uid>


- Rechercher une serie::

    $ python3 manage.py find <ip_pacs> <port_pacs> -aec <nom_pacs> -seUID <serie_uid>


- Cfind response : Les filtres possibles par niveau

    On peut filter avec tous les niveaux des tags suivantes:

        - PatientID
        - StudyInstanceUID
        - SeriesInstanceUID

    Pour **PATIENT** on peut filter sur:

        - PatientName
        - PatientSex
        - PatientBirthDate

    Pour **STUDY** on peut filter sur:

        - StudyDate
        - InstitutionName
        - AccessionNumber
        - ProtocolName
        - StudyDescription

    Pour **SERIES** on peut filter sur:

        - Modality
        - Manufacturer
        - ManufacturerModelName
        - BodyPartExamined
        - SeriesDate
        - SeriesDescription
        - StationName

Output de la commande C-FIND
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Si élement bien retrouvé dans le PACS**


Le terminal dans lequel la commande C-FIND est exécué retourne ::

    qr_level     :STUDY
    study_uid    :1.2.124.113532.10.149.172.6.20180403.83831.11226567
    ****************************************


    ######################### CURRENT SCU CFIND ASSOC #########################
    # Server Association metadata
    # update date           : 2020-07-30 17:32:26.059449
    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------
    # action                : CFIND
    # service               : SCU
    # ---------------------------------------------------------------------------
    # LOG
    # ---------------------------------------------------------------------------
    # last_log      : Equal number of STUDY is 1
    #############################################################################

Ici une Study a été trouvé pour cette correspondance.

Et dans le terminal du PACS un output apparait similaire ::

    =========== SIZE QUEUE PACS4 : 0
    I'm waiting for the data to be saved in the database
    (0008, 0052) Query/Retrieve Level                CS: 'STUDY'
    (0020, 000d) Study Instance UID                  UI: 1.2.124.113532.10.149.172.6.201823423.84332423.114455543
    The search is done in the database :


Vérifier qu'un examen (study) a bien été ajouté dans la bdd PostgreSQL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Tout d'abord se connecter à la base de donnée ::

    $ PGPASSWORD='$PGPASSWORD' psql -U <user_login> -d <database_name> -h <ip> -p <port>

Requête pour afficher les studies ajoutées ::

    >>> SELECT * FROM <MY_SCHEMA>.<TABLE>; #SELECT * FROM my_schema.study;


C-MOVE
------

Usage du C-MOVE
^^^^^^^^^^^^^^^

Le C-MOVE va interroger un PACS puis va réaliser l'action d'envoyer soit les éléments rattachés à un patient ou bien à un
examen (study).

Pour connaitre les arguments nécessaires à cette commande ::

    $ python3 manage.py move -h


    -l [QR_LEVEL] deux choix possibles pour cet argument `STUDY` ou `PATIENT`.
    -stUID [STUDY_UID] préciser après un study_uid ou
    -fUID [STUDY_UID_File] préciser le path d'un .csv contenant une liste de study_uid à envoyer


- **Cas d'utilisation entre deux PACS :**


Ici le PACS1 va envoyer au PACS2 un examen (study) basé sur un study_uid.

Exemple ::

    PACS1 | ip : 127.0.0.1 port : 1111 -aec PACS1 white_list : PACS1 + PACS2
    PACS2 | ip : 127.0.0.1 port : 2222 -aec PACS2 white_list : PACS1 + PACS2

.. Note::
    Il est nécessaire d'ajouter le PACS1 à sa propre white_list, en plus du PACS2, car il va d'abord s'intérroger lui
    même pour vérifier qu'il a bien l'examen (study_uid).

Requête pour afficher les studies ajoutées
.. code-block:: Bash

    $ vim <PACS_PATH>/app/white_list/example.yml

Une fois les white_list complétées. Il faut lancer les deux PACS (PACS1 et PACS2) dans deux terminaux différents ::

    PACS1$ python3 manage.py runserver

    PACS2$ python3 manage.py runserver

Dans un troisième terminal lancer la commande ci-dessous ::

    $ python3 manage.py move 127.0.0.1 1111 -aec PACS1 -aes pacs2 -l STUDY -stUID <STUDY_UID>

API Annotation
--------------

Pour lancer API rest d'annotation il faut modifier la paramètre api_annotation.start à True

* L'Api va être lancer au même moment que le serveur PACS
* Le dossier est sauvgardé

Exemple d'object json à lancer avec l'api:

    { "file_path": "/home/oac/Bureau/test_annotation", "uid": "1.2.840.113619.2.25.22006.190.4.1161185374", "level": "instance"}


lancer avec curl:

.. code-block:: shell

    curl  -d '{"file_path": "/home/oac/Bureau/test_annotation", "uid": "1.2.840.113619.2.25.22006.190.4.1161185374", "level": "instance"}'
     -H "Content-Type: application/json"  -X POST  http://127.0.0.1:5555/save_annotation/


Le lien: http://127.0.0.1:5555/save_annotation/




API Sphere DicomWeb
-------------------

Pour lancer API Sphere DicomWeb il faut modifier la paramètre api.start et api.dicomweb.start à True.
Pour plus d'information cliquer :doc:`ici <configuration>` et voir la partir *Api Rest*


DICOM file management and export
--------------------------------

Index data
^^^^^^^^^^

lancer l'indexation des instances dans la base de donnée::

    python manage.py data index

Export data
^^^^^^^^^^^

Copier le dossier de données vers une autre destination::

    python manage.py data export ../PACS8/data/

Manage Database
---------------

Les commandes de base pour gérer la base de données (create, drop, clean, check, find)

Create Database
^^^^^^^^^^^^^^^
 Créer une base de données::

    python manage.py database create


Drop Database
^^^^^^^^^^^^^

 Supprimer une base de données::

    python manage.py database drop *répertoire cible*



Clean Database
^^^^^^^^^^^^^^

Supprimer et créer une base de données::

    python manage.py database clean


Check Database
^^^^^^^^^^^^^^

Vérifier les donnes dans la base de données

Find Database
^^^^^^^^^^^^^

Récherche des données dans la base de donnée


PACS statistics
---------------

Statistique sur les modalités et la vitesse d'insertiondans la base de donnée

Exemple de la commande modality::

    python manage.py modality speed -d full


Exemple de la commande speed::

    python manage.py monitor speed -d full


