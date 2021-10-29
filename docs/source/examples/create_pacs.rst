Créer un PACS
=============

Pour Créer des nouveaux PACS taper la commande **sphere-admin** suivie du nom du PACS :

* Exemple de création du PACS *PACS_test* :

.. code-block:: Bash

    sphere-admin PACS_test


Voilà la structure du  PACS que tu viens de le créer::

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


Tu trouves la description dans la page :doc:`usage <../../documentation/usage>` .