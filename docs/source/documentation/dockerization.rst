.. _dockerization:

Docker
=======

Pré-requis
----------

Avant de débuter l’installation, vous devez vous assurer des points
suivants :

- Avoir accès au repository EDSImagerie/Dev-SPHERE, et avoir le droit à minima de puller le code et les images Docker de ce projet. 
- Avoir cloner le repository GIT du projet sur votre poste 
- Avoir docker installé sur son environement 
- Avoir docker-compose installé sur son environement 

**Note :** Par convention, le chemin du répertoire GIT que vous avez cloné portera le nom ``${REPO_GIT}`` dans cette documentation.


Compilation depuis poste local
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Si vous êtes sur un laptop connecté à votre propre réseau internet, vous n’avez pas besoin de renseigner de paramètres de proxy particuliers.

Vous pouvez donc vous placer dans le dossier ``${REPO_GIT}/Docker/sphere/``, et entrer la commande suivante :

::

   sudo docker build -t sphere:latest .

Configuration
-------------

Fichier de configuration applicative
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
La configuraton applicative se trouve dans des volumes dédiés à l’emplacement suivant : ``${REPO_GIT}/Docker/sphere/volumes/``

Dans les dossiers ``confXX/`` se trouvent les configurations applicatives des deux PACS de l'environement de dévelopement. Les dossiers ``dataXX`` contiennet les données DICOM que chaque PACS peut manipuler.

Configuration depuis des variables d'environmment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Les paramètres critiques de l'application peuvent également être configurés via des variables d'environemnet, afin de faciliter la gestion des déploiemnets Docker.
**Attention** : Les parmaètres renseignés en variable d'environement écraseront ceux présents dans le fichier au démarrage du conteneur.

Le tableau ci-dessous regroupe les paramètres configurabmes via des variables d'environement :

+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| Nom de la variable                | Paramètre correspondant           | Descrition                                                                                                                              | Valeurs possibles                                            |
+===================================+===================================+=========================================================================================================================================+==============================================================+
| ``DICOM_PORT``                    | ``port``                          | Port utilisé pour les communications DICOM                                                                                              | Plage de 49152 à 65536                                       |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``DICOM_AET``                     | ``AET``                           | Nom utilisé pour les communications DICOM (Application Entity Name)                                                                     | Chaîne de 16 caractères maximum                              |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``THREAD_NUMBER``                 | ``thread.number``                 | Nombre de threads dédiés à l'application SPHERE                                                                                         | Plage de 2 à 16                                              |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``STORAGE_METHOD``                | ``storage_method``                | Type de stockage des données                                                                                                            | ``FS``, ``HDFS``, ``HBASE`` ou ``MIXED``                     |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``FS_DATA_PATH``                  | ``fs.path``                       | Chemin vers le dossier où seront stockes les données **si le type de stockage "FS" à été retenu**                                       | Chemin dans le conteneur (peut être un volume bindé)         |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``HDFS_DATA_PATH``                | ``hdfs.path``                     | Chemin vers le dossier où seront stockes les données **si le type de stockage "HDFS" à été retenu**                                     | Chemin dans le conteneur (peut être un volume bindé)         |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``HBASE_DATA_PATH``               | ``hbase.path``                    | Chemin vers le dossier où seront stockes les données **si le type de stockage "HBASE" à été retenu**                                    | Chemin dans le conteneur (peut être un volume bindé)         |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``WHITELIST_PATH``                | ``path_white_list``               | Chemin vers la liste blanche concernant les PACS autorisés à communiquer avec cette instance de SPHERE                                  | Chemin dans le conteneur (peut être un volume bindé)         |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``DB_ENGINE``                     | ``db.engine``                     | Moteur de BDD utilisé pour l'application SPHERE                                                                                         | ``postgresql`` ou ``sqlite``                                 |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``POSTGRE_HOST``                  | ``db.params.ip``                  | IP ou hostname de la BDD postgresql **si le moteur de BDD "postgresql" à été retenu**                                                   | Addresse IP ou hostname                                      |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``POSTGRE_PORT``                  | ``db.params.port``                | Port de la BDD postgresql **si le moteur de BDD "postgresql" à été retenu**                                                             | Plage de 1024 à 49152                                        |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``POSTGRE_NAME``                  | ``db.params.database``            | Nom de la BDD postgresql **si le moteur de BDD "postgresql" à été retenu**                                                              | Chaîne de de 31 caractères maximum                           |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``POSTGRE_SCHEMA``                | ``db.params.schema``              | Schéma de la BDD postgresql **si le moteur de BDD "postgresql" à été retenu**                                                           | Chaîne de de 31 caractères maximum                           |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``POSTGRE_LOGIN``                 | ``db.params.login``               | Login de la BDD postgresql **si le moteur de BDD "postgresql" à été retenu**                                                            | Chaîne de de 31 caractères maximum                           |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``POSTGRE_PASSWORD``              | ``db.params.password``            | Mot de passe de la BDD postgresql **si le moteur de BDD "postgresql" à été retenu**                                                     | Chaîne de de 31 caractères maximum                           |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``SQLITE_FILEPATH``               | ``db.params.filepath``            | Chemin vers le fichier BDD **si le moteur de BDD SQLITE à été retenu**                                                                  | Chemin dans le conteneur (peut être un volume bindé)         |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``API_SERVER_ENABLED``            | ``api.start``                     | Activation ou non du serveur pour les APIs SPHERE                                                                                       | ``True`` ou ``False``                                        |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``API_SERVER_LISTENING_IP``       | ``api.ip``                        | IP d'écoute du serveur API SPHERE **si ce dernier est activé**                                                                          |  Addresse IP                                                 |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``API_SERVER_LISTENING_PORT``     | ``api.port``                      | Port d'écoute du serveur API SPHERE **si ce dernier est activé**                                                                        |  Plage de 1024 à 49152                                       |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``ALLOWED_HOSTS``                 | ``api.allowed_hosts``             | Liste des hostnames autorisés à se connecter au serveur API SPHERE **si ce dernier est activé**                                         |  Liste de hostnames séparés par ", "                         |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``API_DECOMPRESS_PIXELS``         | ``api.dicomweb.decompress_pixels``| Décompression à la volée des pixels lors de leur requête en DICOMWeb **nécéssite l'activation de l'API DICOMWeb**                       |  ``True`` ou ``False``(par défaut)                           |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``API_JWT_VALIDATION``            | ``api.dicomweb.jwt_validate``     | Validation du Token JWT par les APIs SPHERE **si ces dernières sont activés**                                                           |  ``True`` ou ``False``                                       |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``API_JWT_VALIDATION_URL``        | ``api.dicomweb.jwt_validate_url`` | URL du service de validation du Token JWT par les APIs SPHERE **si ces dernières sont activés**                                         |  Chaîne de caractères constituant une URL                    |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``API_DICOMWEB_ENABLED``          | ``api.dicomweb.start``            | Activation ou non de l'API Dicomweb. **Nécéssite l'activation du serveur API de SPHERE**                                                | ``True`` ou ``False``                                        |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``API_ANNOTATION_ENABLED``        | ``api.annotation.start``          | Activation ou non de l'API Dicomweb. **Nécéssite l'activation du serveur API de SPHERE**                                                | ``True`` ou ``False``                                        |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``ANNOTATION_PATH``               | ``api.annotation.path_data``      | Chemin vers le dossier où seront stockées les annotations. ** Nécéssite l'activation du serveur API de SPHERE et de l'API Annotation.** | Chemin dans le conteneur (peut être un volume bindé)         |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``LOG_STREAM_LEVEL``              | ``log.log_stream_level``          | Niveau de log de la sortie console                                                                                                      | ``CRITICAL``, ``ERROR``, ``WARNING``, ``INFO``, ou ``DEBUG`` |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``LOG_FILE_LEVEL``                | ``log.log_file_level``            | Niveau de log du fichier de log                                                                                                         | ``CRITICAL``, ``ERROR``, ``WARNING``, ``INFO``, ou ``DEBUG`` |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+

**Note** : Assurez-vous que le pacs est bien configuré pour utiliser la base PostgreSQL. Si vous voulez utiliser l’API REST, elle doit être activé, et écouter sur l’adresse IP 0.0.0.0 (configuration par défaut)
