.. _developer-guide:

Developer guide
===============

La première choise à faire c'est de Cloner le code source à partir de GitHub, pour le visualiser.

Cloner le code::

    git clone url.git

Conda or virtualenv environment
-------------------------------

Conda Environment
^^^^^^^^^^^^^^^^^

Créer l'environnement et installer les modules::

    conda env create -f requirements.yml

Activer l'environnement::

    conda activate env_sphere

Désactivate l'environnement::

    conda deactivate

Mis à jour de l'environnement::

    conda env update --name env_sphere --file requirements.yml


Les étapes pour utiliser les fonctions de gestion (C-ECHO, C-STORE, C-MOVE, C-FIND, ...)

- Cloner le code à partir de Gitlab

Environnement virtuel
^^^^^^^^^^^^^^^^^^^^^

- Créer un environnement virtuel::

   python -m venv nom_de_environnement_virtuelle

- Installer les modules à partir du fichier requirements.txt qui existe dans le projet cloner::

   pip install -r requirements.txt

- Upgrade package (par exemple pydicom 1.4.2 ==> 2.1.2)::

    pip install --upgrade somepackage pydicom==2.1.2

Install an editable version
---------------------------

- Installer le projet en mode éditable ( dans notre cas c'est SPHERE) ::

   pip install -e SPHERE

Lancer les tests unitaires
--------------------------

.. code-block:: shell

    py.test unit_tests/* -v

Lancer les tests fonctionnels
-----------------------------

 Les étapes pour la lancer les tests fonctionnels avec pytest

1- Intaller le module *pytest*

    Avec Conda::

        conda install pytest=5.3.5

    Avec virtualenv::

        pip install pytest==5.3.5

2- Entrer dans le dossier SPHERE

3- Pour tester toutes fonctions ( echo, store, find, move) lancer la commande ::

    python -m pytest  tests/functional_tests/test_main.py

4- Pour lancer l'une des fonctions::

    python -m pytest tests/functional_tests/test_[echo, store, find, move].py


Documentation avec Sphinx pour SPHERE
-------------------------------------

- Installation les modules qui existe dans docs/requirements.txt :

    - Si Conda::

        pip install -r docs/requirements.txt

    - Si virtualenv::

        pip install -r docs/requirements.txt

- Générer la documentation technique du projet::

    sphinx-apidoc  -o source/package/ ../sphere/  -f -M -e

- Créer la documentation dans un fichier HTML::

    make html

- Supprimer les fichiers HTML générer par "make html"::

   make clean


Packaging
---------

Lancer le packaging.

- Test le packaging::

    python setup.py test

- Générer le packaging::

    python setup.py bdist_wheel

- Générer le packaging + module zipper::

    python setup.py sdist bdist_wheel


Lancer teste, documentation  et packaging
-----------------------------------------

Installer tox:

    - Avec Conda::

        conda install -c conda-forge tox tox-conda

    - Avec virtualenv::

        pip install tox==2.8.1

Lancer tox::

   tox


Sphere dicomweb
---------------


Indexation de données de tests en fichier template de fixtures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

La procédure est à faire lorsque des modifications sont faites sur les données dicom de tests.

La base est à paramétrer dans les settings côté instance Sphere et côté projet api_sphere_dicomweb via le paramétrage Django.

Contrainte (ou bug?), Django ne crée pas de schéma au lancement des tests, le schéma public doit être utilisé.


1. Effectuer dans une instance PACS de Sphere, une indexation des données de tests::

    python manage.py data index

La base de données est à présent initialisée

2. Dans le projet api_sphere_dicomweb, exporter les données dans un fichier json::

    python manage.py dumpdata api_sphere_dicomweb | tee <votre_fichier_fixture>.json

3. Modifier les chemins dcm_path dans le modèle StorageMetadata::

    # remplacer le nom du fichier /path/to/data/patient123/study par /DATA_ROOT/patient123/study

4. Enregistrer le fichier modifié dans api_sphere_dicomweb/test/fixtures/<votre_fichier_fixture>.template


Les tests peuvent être lancés.

Tests
^^^^^

Décommenter la database des tests

Initialisation de la base::

    python manage.py makemigrations
    python manage.py migrate

Lancement des tests::

    python manage.py test


Documentation avec Swagger
^^^^^^^^^^^^^^^^^^^^^^^^^^

Installer drf-yasg:

    - Avec Conda ou pip::

        pip install drf-yasg==1.17.1

