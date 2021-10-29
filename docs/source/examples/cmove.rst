Cmove
=====

Les étapes à suivre pour tester **Move** avec un study:

1 Créer Trois PACS (PACS1, PACS2, PACS3)

Il faut que tu aies déjà insert une instance dans le PACS1.
Pour cette instance par exemple le StudyUID égale 1.2.124.113532.10.149.172.6.20160906.93145.10227750

2 Lance la commande ci-dessous dans PACS1::

    $ cd PACS1
    $ python manage.py runserver

3 Lance la commande ci-dessous dans PACS3::

    $ cd PACS3
    $ python manage.py runserver

4 Lance la commande ci-dessous dans PACS2::

    $ cd PACS2
    $ python manage.py move 127.0.0.1 11111 -aec PACS1 -aes PACS3  -l STUDY -fUID study_uid


**Les verbosités des trois PACS:**

    * PACS1::

        C-STORE request status: 0x0000


        * PACS2::

        qr_level     :STUDY
        study_uid    :1.2.124.113532.10.160.160.59.20061018.132504.1343611
        ****************************************

        * PACS3::

        ######################### CURRENT SCP CSTORE ASSOC #########################
        # Server Association metadata
        # update date           : 2020-07-01 16:32:26.427960
        # simultaneous assoc : 6
        # ----------------------------------------------------------------------------
        # ----------------------------------------------------------------------------
        # action                : CSTORE
        # service               : SCP
        # final_status          : 0x0000 : Association Completed
        # Study UID             : 1.2.124.113532.10.160.160.59.20061018.132504.1343611
        # Series UID            : 1.2.840.113619.2.134.1762530585.2556.1161149296.444
        # Instance UID          : 1.2.840.113619.2.134.1762530585.2556.1161149296.459
        ##############################################################################

