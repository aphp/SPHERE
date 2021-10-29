.. _spheredicomweb:

Sphere DicomWeb
===============

I. Définitation DICOMweb
------------------------

DICOMweb ™ est un terme appliqué à la famille des RESTful  `DICOM <https://fr.qwe.wiki/wiki/DICOM>`_ services ® définis pour l' envoi,
la récupération et l' interrogation des images médicales et des informations connexes.

Le but est de fournir un appareil mobile léger et le navigateur web mécanisme convivial pour un accès des images qui peuvent être mises en œuvre par
les développeurs qui ont la connaissance minimale avec le DICOM ® standard et qui utilise l' application
des consommateurs mécanismes sympathiques comme http , JSON et types de médias ( comme "image / jpeg") possible dans la mesure maximale.

La norme est formellement définie dans DICOM® PS3.18 Web Services .

Les services DICOMweb ™ se distinguent des autres services Web DICOM® par le suffixe "-RS", indiquant leur nature RESTful.

Les principaux endpoints supportés par SPHERE sont :

    * WADO-RS pour la récupération des fichiers DICOM® PS3.10, les méta - données dans les formulaires XML ou JSON, les données en vrac séparés des méta - données et rendu des images au format des consommateurs
    * STOW-RS  pour le stockage (envoi) de fichiers DICOM® PS3.10 ou séparés des méta - données et des données en vrac
    * QIDO-RS pour l' interrogation des collections (bases de données, registres) d'objets DICOM®

II. Configuration et log
------------------------

Configuration
^^^^^^^^^^^^^
la configuration (le fichier settings.yml)::

    api:
        start: False  # ==> Activer les APIs
        ip: 127.0.0.1 # ==> l'ip de l'Api
        port: 5555    # ==> Le port
        allowed_hosts:# ==> Les hôtes autorisés (liste)
            - '*'     # ==> Tous les hôtes
            - 127.0.0.1  # ==> Une IP spécifique
        dicomweb:
            start: False  ==> Activer l'Api DicomWeb
            jwt_validate: False  ==> Utiliser la validation jwt (True ou False)

Log
~~~

Par defaut le log sont au niveau `INFO` (le fichier logging_config.yml) ::


    api_dicomweb_handler: # api_dicomweb
        class: logging.handlers.RotatingFileHandler
        level: INFO
        formatter: extended_color
        filename: './log/api_dicomweb.log'
        maxBytes: 10485760 # 10MB
        backupCount: 20
        encoding: utf8


III. QIDO-RS
------------


Il permet la recherche :

    - des studies
    - des series
    - des instances

Avec des critères de recherche sur les metadata, et gestion de la pagination.

Les filtres possibles pour le moment (on peut chercher avec les tags ou les keyword)::

    # Patient
        '00100020' ou PatientID
        '00100010' ou PatientName
        '00100040' ou PatientSex
        '00100030' ou PatientBirthDate

    # Study
        '0020000D' ou StudyInstanceUID
        '00100020' ou PatientID
        '00080080' ou InstitutionName
        '00080050' ou AccessionNumber
        '00181030' ou ProtocolName
        '00081030' ou StudyDescription
        '00080020' ou StudyDate

    # Series
        '00100020' ou PatientID
        '0020000E' ou SeriesInstanceUID
        '0020000D' ou StudyInstanceUID
        '00080060' ou Modality
        '00080070' ou Manufacturer
        '00081090' ou ManufacturerModelName
        '00180015' ou BodyPartExamined
        '00080021' ou SeriesDate
        '0008103E' ou SeriesDescription
        '00081010' ou StationName

    # Instances
        '00080018' ou SOPInstanceUID
        '0020000E' ou SeriesInstanceUID
        '0020000D' ou StudyInstanceUID
        '00100020' ou PatientID

.. note::
    La QIDO-RS des studies, series et instance supporte les paramètres: **fittres**, **limit**, **offset** et **includefield**

Les formats de réponse sont spécifiés par `accept`, et pour le moment seul le media type ``application/dicom+json`` est supporté et renvoyé par défaut.
Le support du media type ``accept: application/dicom+xml`` est pour l'instant prévu pour la version version 1.12.0.



Toutes les requêtes peuvent comprendre une liste de filtres sur les metadata (jointes par l'opérateur booléen 'et'). Voir la page swagger pour
l'exhaustivité des filtres employés http://``${IP}``:``${PORT}``/swagger/)

.. hint::
    Le Header ``application/dicom+json`` n'est pas obligatoire puisqu'il s'agit du media type renvoyé par défaut.

1. Recherche de study
^^^^^^^^^^^^^^^^^^^^^
Voilà la liste des tags possible à retourner pour les studies:

+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| Attribute Name                           | Tag               |  Condition                                                                  |
+==========================================+===================+=============================================================================+
| ``Study Date``                           | ``(0008,0020)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Study Time``                           | ``(0008,0030)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Accession Number``                     | ``(0008,0050)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Instance Availability``                | ``(0008,0056)``   | Shall be present if known                                                   |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Modalities in Study``                  | ``(0008,0061)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Referring Physician's Name``           | ``(0008,0090)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Timezone Offset From UTC``             | ``(0008,0201)``   | Shall be present if known                                                   |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Retrieve URL``                         | ``(0008,1190)``   | Shall be present if the Instance is retrievable by the Retrieve transaction |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Patient's Name``                       | ``(0010,0010)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Patient ID``                           | ``(0010,0020)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Patient's Birth Date``                 | ``(0010,0030)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Patient's Sex``                        | ``(0010,0040)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Study Instance UID``                   | ``(0020,000D)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Study ID``                             | ``(0020,0010)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Number of Study Related Series``       | ``(0020,1206)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Number of Study Related Instances``    | ``(0020,1208)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+

* Totalité des studies::

    $ curl -X GET "http://127.0.0.1:8000/qidors/studies" -H  "accept: application/dicom+json"

Retourne un élément au format json::

     [
          {
                "00080005": {
                      "Value": [
                        "ISO_IR 100"
                      ],
                      "vr": "CS"
                },
                "00080020": {
                      "Value": [
                        "20010101"
                      ],
                      "vr": "DA"
                },
                ...
          },
          ...
     ]


* Studies avec filtres:

En passant le keyword DICOM StudyInstanceUID::

    $ curl -X GET "http://127.0.0.1:8000/qidors/studies?StudyInstanceUID=1.3.46.423632.132218.1415242681.6" -H  "accept: application/dicom+json"

Ou le tag::

    $ curl -X GET "http://127.0.0.1:8000/qidors/studies?0020000D=1.3.46.423632.132218.1415242681.6" -H  "accept: application/dicom+json"

Les deux requêtes retournent un élément au format json::

    [
          {
                "00080005": {
                      "Value": [
                        "ISO_IR 100"
                      ],
                      "vr": "CS"
                },
                "00080020": {
                      "Value": [
                        "20010101"
                      ],
                      "vr": "DA"
                },
                ...
          },
          ...
     ]

2. recherche de series
^^^^^^^^^^^^^^^^^^^^^^

Voilà la liste des tags possible à retourner pour les series:

+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| Attribute Name                           | Tag               |  Condition                                                                  |
+==========================================+===================+=============================================================================+
| ``Modality``                             | ``(0008,0060)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Timezone Offset From UTC``             | ``(0008,0201)``   |                  Shall be present if known                                  |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Series Description``                   | ``(0008,103E)``   | Shall be present if known                                                   |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Retrieve URL``                         | ``(0008,1190)``   | Shall be present if the Instance is retrievable by the Retrieve transaction |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Series Instance UID``                  | ``(0020,000E)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Series Number``                        | ``(0020,0011)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Number of Series Related Instances``   | ``(0020,1209)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Performed Procedure Step Start Date``  | ``(0040,0244)``   | Shall be present if known                                                   |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Performed Procedure Step Start Time``  | ``(0040,0245)``   | Shall be present if known                                                   |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Request Attributes Sequence``          | ``(0040,0275)``   | Shall be present if known                                                   |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``>Scheduled Procedure Step ID``         | ``(0040,0009)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``>Requested Procedure ID``              | ``(0040,1001)``   |                                                                             |
+------------------------------------------+-------------------+-----------------------------------------------------------------------------+

* Totalité des series ::

    $ curl -X GET "http://127.0.0.1:8000/qidors/series" -H  "accept: application/dicom+json"

Retourne::

    [
          {
                "00080005": {
                  "Value": [
                    "ISO_IR 100"
                  ],
                  "vr": "CS"
                },
                "00080201": {
                  "Value": [
                    "+0000"
                  ],
                  "vr": "SH"
                },
                ...
          },
          ...
    ]


La même requête, requérant une réponse en xml:

    $ curl -X GET "http://127.0.0.1:8000/qidors/series"

Retourne::

    En cours de développement

* Recherche des series d'une study::

    $ curl -X GET "http://127.0.0.1:8000/qidors/studies/1.3.46.423632.132218.1415242681.6/series" -H  "accept: application/dicom+json"

Retourne un élément au format json::

     [
          {
                "00080005": {
                  "Value": [
                    "ISO_IR 100"
                  ],
                  "vr": "CS"
                },
                "00080201": {
                  "Value": [
                    "+0000"
                  ],
                  "vr": "SH"
                },
                ...
          },
          ...
    ]

3. recherche d’instances
^^^^^^^^^^^^^^^^^^^^^^^^

Voilà la liste des tags possible à retourner pour les instances:

+-------------------------------+-------------------+-----------------------------------------------------------------------------+
| Attribute Name                | Tag               |  Condition                                                                  |
+===============================+===================+=============================================================================+
| ``SOP Class UID``             | ``(0008,0016)``   |                                                                             |
+-------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``SOP Instance UID``          | ``(0008,0018)``   |                                                                             |
+-------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Instance Availability``     | ``(0008,0056)``   | Shall be present if known                                                   |
+-------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Timezone Offset From UTC``  | ``(0008,0201)``   | Shall be present if known                                                   |
+-------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Retrieve URL``              | ``(0008,1190)``   | Shall be present if the Instance is retrievable by the Retrieve transaction |
+-------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Instance Number``           | ``(0020,0013)``   |                                                                             |
+-------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Rows``                      | ``(0028,0010)``   | Shall be present if known                                                   |
+-------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Columns``                   | ``(0028,0011)``   | Shall be present if known                                                   |
+-------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Bits Allocated``            | ``(0028,0100)``   | Shall be present if known                                                   |
+-------------------------------+-------------------+-----------------------------------------------------------------------------+
| ``Number of Frames``          | ``(0028,0008)``   | Shall be present if known                                                   |
+-------------------------------+-------------------+-----------------------------------------------------------------------------+


* Totalité des instances::

    $ curl -X GET "http://127.0.0.1:8000/qidors/instances" -H  "accept: application/dicom+json"

Retourne::

    [
          {
                "00080016": {
                      "Value": [
                        "1.2.840.10008.5.1.4.1.1.2"
                      ],
                      "vr": "UI"
                },
                    "00080018": {
                      "Value": [
                        "1.3.6.1.4.1.5962.1.1.0.0.0.1194734704.16302.0.14"
                      ],
                      "vr": "UI"
                }
                ...
          },
          ...
    ]

La même requête, requérant une réponse en xml::

    $ curl -X GET "http://127.0.0.1:8000/qidors/instances" -H  "accept: application/dicom+xml"

Retourne::

    En cours de développement

* Instances d'une study::

    $ curl -X GET "http://127.0.0.1:8000/qidors/studies/1.3.46.670589.11.0.1.1996082307380006/instances" -H  "accept: application/dicom+json"

Retourne::

    [
          {
                "00080016": {
                      "Value": [
                        "1.2.840.10008.5.1.4.1.1.2"
                      ],
                      "vr": "UI"
                },
                    "00080018": {
                      "Value": [
                        "1.3.6.1.4.1.5962.1.1.0.0.0.1194734704.16302.0.14"
                      ],
                      "vr": "UI"
                }
                ...
          },
          ...
    ]

La même requête, requérant une réponse en xml::

    $ curl -X GET "http://127.0.0.1:8000/qidors/studies/1.3.46.670589.11.0.1.1996082307380006/instances"

Retourne::

    En cours de développement

* Instances d’une series et d’une study::

    $ curl -X GET "http://127.0.0.1:8000/qidors/studies/1.3.46.423632.132218.1415242681.6/series/1.3.46.423632.132218.1415243125.23/instances" -H  "accept: application/dicom+json"

Retourne::

   [
          {
                "00080016": {
                      "Value": [
                        "1.2.840.10008.5.1.4.1.1.2"
                      ],
                      "vr": "UI"
                },
                    "00080018": {
                      "Value": [
                        "1.3.6.1.4.1.5962.1.1.0.0.0.1194734704.16302.0.14"
                      ],
                      "vr": "UI"
                }
                ...
          },
          ...
   ]

La même requête, requérant une réponse en xml::

    $ curl -X GET "http://127.0.0.1:8000/qidors/studies/1.3.46.423632.132218.1415242681.6/series/1.3.46.423632.132218.1415243125.23/instances"

Retourne::

    En cours de développement

4. Récapitulatif des endpoints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Voir swagger partie qidors http://127.0.0.1:8000/swagger/

​- ``/qidors/instances``
​- ``/qidors/series``
​- ``/qidors/studies``
​- ``/qidors/studies/{StudyInstanceUID}/instances``
​- ``/qidors/studies/{StudyInstanceUID}/series``
​- ``/qidors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/instances``


IV. WADO-RS
-----------

Il permet la récupération des instances sous forme brutes et la récupération des metadata.
La récupération des frames d’une instance sop (non implémenté)


1. Récupération des metadata d'une study
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

À partir de son uid::

    $ curl -X GET "http://127.0.0.1:8000/wadors/studies/1.3.46.423632.132218.1415242681.6/metadata" -H  "accept: application/dicom+json"

Retourne la liste des métadonnées de toutes les instances liées au study_uid  sauf les pixels::

    [
      {
        "30020002": {
          "vr": "SH",
          "Value": [
            "iViewPortalImage"
          ]
        },
        "30020011": {
          "vr": "DS",
          "Value": [
            0.402,
            0.402
          ]
        },
        "30020012": {
          "vr": "DS"
        },
        "30020020": {
          "vr": "SH"
        },
        "30020022": {
          "vr": "DS",
          "Value": [
            1000
          ]
        }
      },
      ...
    ]



2. Récupération des metadata d'une study et series
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

À partir de son uid::

    $ curl -X GET "http://127.0.0.1:8000/wadors/studies/1.3.46.423632.132218.1415242681.6/series/1.3.46.423632.132218.1415243125.23/metadata" -H  "accept: application/dicom+json"

Retourne la liste des métadonnées de toutes les instances liées au study_uid et series_uid sauf les pixels::

    [
      {
        "30020002": {
          "vr": "SH",
          "Value": [
            "iViewPortalImage"
          ]
        },
        "30020011": {
          "vr": "DS",
          "Value": [
            0.402,
            0.402
          ]
        },
        "30020012": {
          "vr": "DS"
        },
        "30020020": {
          "vr": "SH"
        },
      },
      ...
    ]


3. Récupération le metadata d’une instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

À partir de la study uid, series uid et de la sop instance uid ::

    $ curl -X GET "http://127.0.0.1:8000/wadors/studies/1.3.46.423632.132218.1415242681.6/series/1.3.46.423632.132218.1415243125.23/instances/1.3.46.423632.132218.1438566266.11/metadata" -H  "accept: application/dicom+json"

Retourne tous les métadonnées de l'instance sauf le pixel::

    {
      "30020002": {
        "vr": "SH",
        "Value": [
          "iViewPortalImage"
        ]
      },
      "30020011": {
        "vr": "DS",
        "Value": [
          0.402,
          0.402
        ]
      },
      ...
    }


4. Récupération toutes les instances d'une study
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Retourne la liste des métadonnées et les data pixels de toutes les instances liées au study_uid.

* Exemple d'url::

        $ curl -X GET "http://127.0.0.1:8000/wadors/studies/1.3.46.423632.132218.1415242681.6" -H  "accept: multipart/related; type="application/dicom""


5. Récupération toutes les instances d’une study et series
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Retourne la liste des métadonnées et les data pixels de toutes les instances liées au study_uid et series_uid.

* Exemple d'url::

        $ curl -X GET "http://127.0.0.1:8000/wadors/studies/1.3.46.423632.132218.1415242681.6/series/1.3.46.423632.132218.1415243125.23" -H  "accept: multipart/related; type="application/dicom""


6. Récupération d'une instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Retourne la métadonnée et le data pixel d'une instance.


* Exemple d'url::

        $ curl -X GET "http://127.0.0.1:8000/wadors/studies/1.3.46.423632.132218.1415242681.6/series/1.3.46.423632.132218.1415243125.23/instances/1.3.46.423632.132218.1438566266.11" -H  "accept: multipart/related; type="application/dicom""


7. Récupération d'une frame
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Retourne la data pixel d'une frame (instance), la vateur de keyword ``PixelData`` et le tag ``7fe00010``

.. warning::
    Pour le moment le numéro de frame n'est pas géré, par defaut on retourne la valeur de keyword ``PixelData``

* Exemple d'url::

    $ curl -X GET "http://127.0.0.1:8000/wadors/studies/1.3.46.423632.132218.1415242681.6/series/1.3.46.423632.132218.1415243125.23/instances/1.3.46.423632.132218.1438566266.11/frames/1" -H  "multipart/related; type="application/octet-stream""


.. note::
    Il est possible que certaines ``DICOM tranfer syntax`` ne soient pas supportées, notament côté visualiseur. Dans ce cas, vous pouvez passer la paramètre ``DECOMPRESS_PIXELS`` à ``true``, ce qui aura pour effet de décompresser à la volée les pixels, et de les envoyer avec la tranfer syntax ``1.2.840.10008.1.2.1``

8. Récapitulatif des endpoints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Voir swagger partie wadors http://127.0.0.1:8000/swagger/

 - ``/wadors/studies/{StudyInstanceUID``
 - ``/wadors/studies/{StudyInstanceUID}/metadata``
 - ``/wadors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID``
 - ``/wadors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/metadata``
 - ``/wadors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/instances/{SOPInstanceUID``
 - ``/wadors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/instances/{SOPInstanceUID}/metadata``
 - ``/wadors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/instances/{SOPInstanceUID}/frames/{frame``

