Cecho
=====


Les étapes à suivre pour tester **Echo**:

1 Créer deux PACS (PACS1, PACS2)

2 Lance la commande ci-dessous dans PACS1::

    $ cd PACS1
    $ python manage.py runserver

3 Lance la commande ci-dessous dans PACS2::

    $ cd PACS2
    $ python manage.py echo 127.0.0.1 11111 -aec PACS1


**Les verbosités des deux PACS:**

    * PACS1::

        ######################### CURRENT SCP CECHO ASSOC #########################
        # Server Association metadata
        # update date 		: 2020-03-13 16:38:51.295723
        # simultaneous assoc : 0
        # ---------------------------------------------------------------------------
        # ---------------------------------------------------------------------------
        # action		: CECHO
        # service		: SCP
        # final_status		: 0x0000 : Association Completed
        #############################################################################

    * PACS2::

        ######################### CURRENT SCU CECHO ASSOC #########################
        # Server Association metadata
        # update date 		: 2020-03-13 16:26:16.444246
        # ---------------------------------------------------------------------------
        # ---------------------------------------------------------------------------
        # action		: CECHO
        # service		: SCU
        # final_status		: 0x0000 : Association Completed
        #############################################################################
