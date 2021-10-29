.. _working_environment:

Working environment
===================

Voilà le bon environnement de travail avec n'importe qu'elle projet

Installation de Git
-------------------

Avant de commencer à utiliser Git, il faut qu’il soit disponible sur votre ordinateur.
Même s’il est déjà installé, c’est probablement une bonne idée d’utiliser la dernière version disponible.

Installation sur Linux
^^^^^^^^^^^^^^^^^^^^^^

Si vous voulez installer les outils basiques de Git sur Linux via un installateur binaire, vous pouvez généralement le faire au moyen de l’outil de gestion de paquet fourni avec votre distribution. Sur Fedora, par exemple, vous pouvez utiliser dnf :

.. code-block:: shell

    $ dnf install git-all

Sur une distribution basée sur Debian, telle que Ubuntu, essayer apt-get :

.. code-block:: shell

    $ apt-get install git-all


PyCharm / IntelliJ IDEA
-----------------------

`PyCharm <https://www.jetbrains.com/pycharm/>`_ est développé par JetBrains, aussi connu pour IntelliJ IDEA.
Les deux partagent la même base de code et la plupart des fonctionnalités de
Il y a deux versions de PyCharm: une édition Professionnelle (avec 30 jours d’essai gratuits)
et une édition Communautaire (sous licence Apache 2.0) avec moins de fonctionnalités.

Paramétrage pour avoir la documentation technique
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Voici un petit exemple de documentation manuelle

.. py:function:: my_fonction(arg00, arg01, arg03='4')

   :param arg00: first argument
   :type arg00: int
   :param arg01: second argument
   :type arg01: dict
   :param arg02: third argument
   :type arg02: str
   :return: all the elements requests
   :rtype: list

Pour avoir la même structure comme dans l'exemple ci-dessus automatiquement dans PyCharm voilà les étapes:

- Cliquer sur **File** dans le menu principal du logiciel
- Aller à **Settings** > **Editor** > **General** > **Smart Keys**
- Cochez la case qui dit **Insert type placeholders in the documentation comment stub**

L'en-tête du module python
^^^^^^^^^^^^^^^^^^^^^^^^^^

Voilà l'en-tête de chaque module que tu le crées avec python.

``
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
{Description module}
"""

# Futures
from __future__ import print_function

# Built-in/Generic Imports
import os
import sys

# Libs
import pandas as pd # Or any other

# Own modules
from path import class
``
Les étapes pour l'avoir automatiquement sous PyCharm:

- Cliquer sur **File** dans le menu principal du logiciel
- Aller à **Settings** > **Editor** > **File and Code Templete**
- Cliquer sur **Python Script**
- Copier le l'en-tête que j'ai déjà mis ci-dessus et le color dans l'enderoit vide à deroit
- Cochez la case qui dit **Insert type placeholders in the documentation comment stub**
- Cliquer sur **Apply** puis **OK**

Vérification du code (Pylint)
-----------------------------

Pylint est un logiciel de vérification de code source et de la qualité du code
pour le langage de programmation Python. Il utilise les recommandations officielles de style PEP8.

Installer Pylint::

    Avec Conda::

        conda install pylint=2.4.4

    Avec virtualenv::

        pip install pylint==2.4.4

MiniConda
---------

Miniconda est un installateur minimal pour Conda qui permet de gérer des bibliothèques pour développer en python.
C'est une version réduite d'Anaconda qui inclut uniquement Conda, Python, les paquets dont ils dépendent.


Démarrer avec conda
^^^^^^^^^^^^^^^^^^^

Dans un navigateur internet, ouvrez la page du site Miniconda https://conda.io/miniconda.html
puis cliquez sur le lien 64-bit (bash installer) correspondant à Linux et Python 3.7.
Bien sur, si votre machine est en 32-bit (ce qui est maintenant assez rare), vous cliquerez sur le lien 32-bit (bash installer).

1- Téléchargement de Miniconda

Vous allez télécharger un fichier dont le nom ressemble à quelque chose du type ::

    $ Miniconda3-latest-Linux-x86_64.sh.

Tu peux le télécharger via ligne de commande::

    $ wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    $ chmod +x Miniconda3-latest-Linux-x86_64.sh


2- Installation de Miniconda

Dans un shell, lancez l’installation de Miniconda avec la commande ::

    $ bash Miniconda3-latest-Linux-x86_64.sh


Démarrer avec python-sphinx
---------------------------

 Les étapes pour la création d'une documentation avec Sphinx

1- Installation de Sphinx si n'est installé::

   pip install Sphinx

2- Créer le dossier docs::

   mkdir docs
   cd docs

3- Lancer Sphinx::

   sphinx-quickstart

4- Ouvrier source/config.py

   Ajoute 'sphinx.ext.autodoc' dans la liste extensions

   Modifier le theme si tu veux

   Ajoute les path des modules du projet avec cette commande ::

        sys.path.insert(0, os.path.abspath('../..'))

5- Générer les fichiers .rst du projet::

        sphinx-apidoc  -o source/package/ ../sphere/  -f -M -e

6- Créer la documentation dans un fichier HTML:

   make html

7- Supprimer les fichiers HTML générer par "make html"::

   make clean



Autres outils
-------------

IPython
^^^^^^^


IPython fournit une boîte à outils riche pour vous aider à tirer le meilleur parti de l’interactivité de Python. Ses principales composantes sont:

- Shells Python puissants (basés sur le terminal et Qt)
- Un “notebook” basé sur le Web avec les mêmes caractéristiques de base, mais le support de médias riches, du texte, du code, des expressions mathématiques et des graphiques intégrés “inline”.
- Support pour la visualisation interactive de données et l’utilisation de boîtes à outils avec interface graphique.
- Interpréteurs flexibles, intégrables à charger dans vos propres projets.
- Outils pour le traitement parallèle interactif et de haut niveau.

.. code-block:: shell

    $ pip install ipython

Pour télécharger et installer IPython avec toutes ses dépendances optionnelles pour le notebook, qtconsole, les tests et les autres fonctionnalités

.. code-block:: shell

    $ pip install ipython[all]

