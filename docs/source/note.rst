Note
====


run  :
    run PACS

echo :
    check un pacs
store:
    - store dicom all data in pacs
    - store one patient
    - store one study
    - store one series
find :
    search in a database:
        patient : return list of patients
        study : return list of study
        series : retrn list of series
    serach in a file
        patient : return list of patients
        study : return list of study
        series : retrn list of series
move :
    patient: move list of patient
    study: move list of study
    series : move list of series




find: Recherche dans un fichier et sur la base de données
    Patient:
        Recherche tous les patients dans une PACS
        Recherche un seul patient dans une PACS
    Study:
        Recherche tous les examens dans une PACS
        Recherche un seul examen dans une PACS
        Recherche tous les examens pour un patient dans une PACS
    Series:
        Recherche toutes les séries
        Recherche une seule série
        Recherche toutes les séries pour un patient
        Recherche toutes les séries pour un examen
        //Recherche toutes les séries pour un patient et un examen

store: file et base de donnée
        - store tous le dossier

    Patient:
        store un seul patient
    Study:
        store un examen
    Series
        store une série

move:
 fichier vers fichier et base de données
 base de données vers fichier et base de données

    Patient:
        Déplacer tous les patients
        Déplacer un seul patient
    Study:
        Déplacer tous les examens
        Déplacer un seul examen
        Déplacer tous les examen pour un patient
    Series:
        Déplacer toutes les séries
        Déplacer une seule série
        Déplacer toutes les séries pour un patient
        Déplacer toutes les séries pour un examen
        //Déplacer toutes les séries pour un patient et un examen


DicomWeb
--------

DICOMweb est le standard pour l'imagerie médicale sur le web. Il comprend principalement un ensemble de services RESTful.
DICOMWeb est une nouvelle version du protocole DICOM
DICOMweb ajoute des services HTTP à DICOM, basés sur le style REST (Representational State Transfer)


L’avantage majeur est que le protocole DICOM traditionnel est encore un protocole de niche qui est
utilisé uniquement à des fins médicales et, dans une moindre mesure, pour l'imagerie industrielle. Par conséquent, DICOMweb
offre un accès à un plus grand nombre d’outils, d’expertises et de ressources beaucoup plus grandes
que ce que nous avons disponible dans le domaine de l'imagerie médicale. De plus, nous obtenons un autre billet de faveur;
services Web très bien adaptés à une utilisation sur des appareils mobiles tels que tablettes, phablets,
téléphones, etc


QIDO-RS  (Query based on ID for DICOM Objects) : vous permettent de rechercher des études, des séries et des instances par ID patient et de recevoir leurs identifiants uniques

WADO-RS, (Web Access to DICOM Objects) : vous permet de récupérer des études, des séries et des instances au format XML ou JSON

studyUID=2.16.840.1.1.2.3&seriesUID=2.16.840.1.4.5.6&objectUID=2.16.840.1.7.8.9».
STOW-RS (STore Over the Web) : vous permet de stocker des instances spécifiques sur le serveur


WADO-URI, Le service WADOd'origine, maintenant appelé WADO-URI a été développé pour permettre la récupération d'instances DICOM à l'aide de paramètres de requête sur une ressource unique. Par exemple, l'URL d'une ressource de service WADO-URI peut ressembler à « https://myserver.com/wado?


DICOMWeb fournit un mécanisme simple pour accéder à un objet DICOM à l’aide de
protocoles Web, c’est-à-dire un protocole HTTP / HTTPS.
DICOMweb™
DIMSE
WADO-RS
C-GET
STOW-RS
C-STORE
QIDO-RS
C-FIND
