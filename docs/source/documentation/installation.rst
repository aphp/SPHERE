.. _installation-guide:

Installation guide
==================


Les étapes à suivre pour installer sphere en mode production (Si tu veux faire
des developpements sur sphere merci de voir la page  :doc:`development <development>` .

.. note::
    Cliquer :download:`ici <../../_static/sphere-1.11.2-py3-none-any.whl>` pour télécharger la dernière version de *sphere*.



Installez la version officielle
-------------------------------

*sphere*, étant une bibliothèque Python, nécessite `Python
<https://www.python.org/>`_. Si vous ne savez pas si votre version de Python est
prise en charge ou non, consultez :ref:`ce tableau<faq_install_version>`.

**Création un environnement virtuel:**

Avec conda
^^^^^^^^^^

Créer l'environnement et installer les modules ::

    $ conda create -n <nom_env> python=3.7

Activer l'environnement virtuel ::

    $ conda activate <nom_env>

Désactivate l'environnement::

    $ conda deactivate


Avec venv
^^^^^^^^^

Créer un environnement virtuel::

    $ python -m venv <nom_env>

Activer l'environnement virtuel ::

    $ source activate <nom_env>

Désactivate l'environnement::

    $ deactivate

**Supprimer tous les packages installés par pip:**

    - Sous Linux::

        $ pip freeze | xargs pip uninstall -y

    - Sous n'importe quelle systemes d'exploitation::

        $ pip freeze > requirements.txt
        $ pip uninstall -r requirements.txt -y

**Installer le package .whl**::

     $ pip install 'le fichier .whl'


Prerequisites
-------------

.. note::
        L'implémentation actuelle de la spehere prend en charge:
            - Versions de Python 3 de 3.6.1 à 3.8
            - Version minimale de Python prise en charge est 3.6.1

        Créer une base de donnée PostgreSQL ou SQLite
