.. _release_notes:

#############
Release Notes
#############

Change log
==========

v1.4.0
------
:Date: 23/12/2019

- Résoudre les ralentissements de create or update
- Gestion des erreurs de base de données - supprimer le récursif dans la base de données
- Gerér l'erreur "Error in databse access. Retry 1 time (Process stopped for 500 ms)
- l'insertion des données en mode asynchrone
- Mise en place du bulk pour chargement bdd

v1.4.1
------
:Date: 15/01/2020

- Bug: Vérifier les keyword suivantes patientName, patientSex and dateStudy

v1.5.0
------
:Date: 10/02/2020

- Tester et améliorer le code de la méthode index_dicom_folder() du module file_system_access et ajouter un nouveau param pour index.
- Ajout de table sans drop la base de données
- SubClasse -> ajouter le support des classes compressées
- Gestion de contexte différents dans les settings
- Nettoyer les settings des paramètres inutilise
- Controle si tous les paramètres sont dans settings.py et puisse être défini dans settings.yml
- Remise à plat de l'ensemble logs
- Initier  le Move-existing

v1.5.1
------
:Date: 12/02/2020

- File Meta Information Group Elements (0002,eeee) should be in their own Dataset object in the 'DcmFile.file_meta' attribute.

v1.6.0
------
:Date: 28/02/2020

- Packager la solution sphere et serveur
- La migration de pydicom 1.2 à 1.4.2
- La migration de pynetdicom 1.3 à 1.4.1
- La migration de sqlalchemy 1.2 à 1.3.13
- La migration de sqlalchemy-views 0.2.3 à 0.2.4
- La migration de pyyaml 3.13 à 5.3
- La migration de psycopg2-binary 2.7 à 2.8.4

v1.6.1
------
:Date: 21/04/2020

- Amélioration de la vitesse d’indexation + bug d'indexation
- Créer un schéma de base de données spécifique COVID 19
- Corriger un bug au niveau de thread index
- Corriger un bug au niveau de thread db

v1.6.2
------
:Date: 27/04/2020

- Suite au except AttributeError: 'DcmFile' object has no attribute 'Modality' afficher le path du fichier

v1.6.3
------
:Date: 28/04/2020

- Créer une modalité "Inconnue" si la Modalité n'existe pas dans un fichier dicom

v1.6.4
------
:Date: 29/06/2020

- Ajoute un nouvel argument pour choisir la source des paths dicom (database ou file system)
- Ajoute deux arguments le fichier des uids et model_name (patient, study, series ou instance) si la source des paths et database
- Store toutes les instances dans la base de données si on a * dans la première ligne du fichier des uids
- Recherche les paths dans la base de données

v1.7.0
------
:Date: 05/08/2020

- Initier API REST Annotation
- Initier SphereDicomWeb
- Initier la documentation de sphere
- Prévois de PIP et CONDA pour sphere
- La migration de python 3.5 à 3.6
- LOG database et sqlalchemy
- Utiliser tox pour lancer (test + documentation + packaging)
- Ajouter la saisie automatique de d8maj pour le rechargement de données en bdd lors d'un cstore
- Au moment de charger la liste de requete uid c-move vérifier si chacune existe dans le PACS Tampon (avec c-find)
- créer une table execution d'une liste id

v1.8.0
------
:Date: 21/10/2020

- Programmer un script qui parse les pages suivantes:
    http://dicom.nema.org/medical/dicom/current/output/chtml/part06/chapter_6.html
    http://dicom.nema.org/dicom/2013/output/chtml/part06/chapter_7.html
    http://dicom.nema.org/dicom/2013/output/chtml/part06/chapter_8.html
- Générer un fichier csv qui contient Tag, Keyword, Attribute name, VR, Field name of a table, Type, Size if type settings
- Développer un script qui généré un fichier YML (tag, keyword, type, VR, field name) à partir de liste des tags
- Générer le schema de la base de donnée dynamiquement (à partir d'un fichier YML)
- Améliorer et restructuré la documentation

v1.8.1
------
:Date: 10/11/2020

- Bug : les tags protocolName, studyDescription, ... prendre des valeurs None dans la base de donnée après indexation

v1.9.0
------
:Date: 10/12/2020

- Tester et qualifier l'API d'annotation
- Créer Automatiquement la table ``mapping_annotation`` si on active l'API annotation et la table n'existe pas
- Ajoute Pending ``0xFF00`` pour ``cmove`` et donne le choix aux utilisateurs avec cette paramettre ``pending_responses_move`` (True ou False)
- Vérifier si on se connecte à la base de données avant de lancer le PACS ``runserver``
- Ajouter un argument ``-f`` avec la valeur ``True`` ou ``False`` pour les commandes `drop`` et ``clean``
- Demande de confirmation si on lance les commandes ``drop`` ou ``clean`` sans ajouter l'argument ``-f`` avec True ou False
- Lance ``Store`` ou ``Move`` sans base de données
- Lancer PACS (``runserver``) sans avoir les paramètres de la base de données
- Vider (pour la sécurité) les parametres de la base de données avant de l'afficher dans les logs
- Créer un fichier ``error/index.rst`` dans la documentation spécifique pour ajouter les erreurs
- Dockorisation de ``sphere``

v1.9.1
------
:Date: 18/01/2021

- Basculer la dépendance pydicom sur> = 2.1.2
- Basculer la dépendance pynetpydicom sur> = 1.5.5

v1.10.0
-------
:Date: 18/02/2021

- Tester et qualifier l'API DicomWeb
- Utiliser OHIF avec notre DicomWeb
- Gestion des hostnames dans le fichier whitelist
- Cérer les docker-compose suivante (docker-compose.ohif.yml, docker-compose.headless.yml, docker-compose.sphere-only.yml, docker-compose.two-pacs.yml
- Utilisation de variable d'environements pour configurer SPHERE

v1.11.0
-------
:Date: 00/04/2021

**Sphere**

- Nouveau schéma de la base de données de Sphere:

    - Supprimer les tables ``instance`` et ``stotage_metadata``
    - Ajouter les champs suivants `dt_first_insertion` et `dt_completion` dans la table `series`
    - Crée un nouveau table ``file_storage_metadata_dicom``

- C-Find response pour les tags suivants::

    # level PATIENT
       PatientName, PatientSex et PatientBirthDate

    # level STUDY
        StudyDate, InstitutionName, AccessionNumber, ProtocolName et StudyDescription

    # level SERIES
        Modality, Manufacturer, ManufacturerModelName, BodyPartExamined, SeriesDate, SeriesDescription et StationName

    - Avec la base de données et file system (sans base de données)

- Bug C-Find et C-Move avec la version pynetdicom 1.5.5
- Ajouter le support des variables d’environnement 'host_available' et 'webdicom'

- Afficher les versions :
    Version de sphere : ``python manage.py -v``
    Version avec laquelle le pacs est créé : ``python manage.py -vp``

**DicomWeb**

- Supprimer ORM_DJANGO et utiliser seulement ORM_SQLALCHEMY dans l'API SphereDicomWeb
- Teste offset, limit, filters de WebDicomSphere avec l'ORM_SQLALCHEMY
- Support des filtres par UID au niveau study, serie et instance QIDO-RS

    Exemple de liens avec filtres:
        - qidors/studies?PatientID=${PatientID}
        - qidors/studies/{StudyInstanceUID}/series?PatientID=${PatientID}

    - Chercher avec un ou plusieurs critères
    - Chercher avec un ou plusieurs ``like`` (rechercher les enregistrements dont la valeur d’une colonne commence par telle ou telle lettre)
    - Chercher avec mixe entre critères et ``like``

- Coriger les URLs renvoient les métadonnées sous une forme non compatible `JSON DICOM <http://dicom.nema.org/dicom/2013/output/chtml/part18/sect_F.2.html>`_ sur l'endpoint QIDO-RS
- Supprimer le paramètre 'fmt' pour l'endpoint QIDO-RS
- Support du Header Accept pour déterminer le type de contenu à renvoyer pour l'endpoint QIDO-RS
- Supporter le paramètre 'includefield' pour l'endpoint QIDO-RS

v1.11.1
-------
:Date: 28/05/2021

**DicomWeb**

- Corriger mauvais encodage DICOMWeb

v1.11.2
-------
:Date: 05/07/2021

- Indexation bloquée lors d'ingestion de données DICOM

Bug::

    2021-06-15 07:30:39,845 :: index_data           :: WARNING  :: thread_index.py    :: line: 97   :: There is a problem in the main process, because we are in a loop for more than 5 minutes, the thread list: [<_MainThread(MainThread, started 140340329346880)>, <Thread(name='thread_index')>].

- Trop de clients postgres instanciés avec sqlalchemy sans être fermés

Bug::

    FATAL:  sorry, too many clients already

- Ajoute un sleep de n minutes entre chaque store de (patient_id, study_uid, series_uid ou instance_uid)
- Ajoute une parametre `sleep_in_store` pour définir le nombre de minutes de sleep entre les uids  (par default: 0)
- Store un uid de (patient, study, series ou instance) directe sans passer par un fichier (ajouter un argument `-UID` suivie par l'uid dans la commande `Store`)