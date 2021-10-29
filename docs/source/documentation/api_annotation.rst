.. _api_annotation:

API Annotation
==============

Objectif
--------

- On reçoit un fichier et une instance qui doivent permettre d'identifier l'instance ou la série relié à cette annotation.
- Stockage dans une table BDD avec comme objectif de stocker l'instance uid et le chemin du fichier.
- Le fichier doit-être stocké dans un dossier préciser via la config.
- Un nom unique de fichier est généré à chaque ajout.

Table
-----
Nom de la table : mapping_annotation

les champs de la table:
 - uid_dicom
 - level
 - uuid_generator



Définitation
------------
L'api d'annotation permet de sauvgarder le fichier d'annotation dans dossier et de mettre le chemain dans la base de donnée.
Une annotation est liée à une instance ou une series.

Exemple
-------

Exemple de Json::

    {
        "file_path": "/home/oac/Bureau/test_annotation",
        "uid": "1.2.124.113532.10.160.160.59.20111004.93208.3593882",
        "level": "instance"  # On a trois niveaux: ``instance``, ``series``, ``study``
    }

URL::

    http://127.0.0.1:8000/api_annotation/
