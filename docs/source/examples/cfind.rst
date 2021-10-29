Cfind
=====


Les étapes à suivre pour tester **Find**:

Description: Recherche tous les study UID dans le PACS1 et le sauvgarder dans le fichier list_study.csv

1 Créer deux PACS (PACS1, PACS2)

2 Lance la commande ci-dessous dans PACS1::

    $ cd PACS1
    $ python manage.py runserver

3 Lance la commande ci-dessous dans PACS2::

    $ cd PACS2
    $ python manage.py  find 127.0.0.1 11111  -aec PACS1 -l STUDY -o list_study.csv -v 1


**Les verbosités des deux PACS:**

    * PACS1::

        (0008, 0052) Query/Retrieve Level                CS: 'STUDY'
        (0020, 000d) Study Instance UID                  UI: *

    * PACS2::

        ######################### CURRENT SCU CFIND ASSOC #########################
        # Server Association metadata
        # update date           : 2020-05-15 17:49:34.206717
        # ---------------------------------------------------------------------------
        # ---------------------------------------------------------------------------
        # action                : CFIND
        # service               : SCU
        # ---------------------------------------------------------------------------
        # LOG
        # ---------------------------------------------------------------------------
        # last_log      : Equal number of STUDY is 3
        #############################################################################


