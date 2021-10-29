Cstore
======


Les étapes à suivre pour tester **Store**:

1 Créer deux PACS (PACS1, PACS2)

2 Lance la commande ci-dessous dans PACS1::

    $ cd PACS1
    $ python manage.py runserver

3 Lance la commande ci-dessous dans PACS2::

    $ cd PACS2
    $ python manage.py store 127.0.0.1 11111 -aec PACS1 -sp fs -pd data/


**Les verbosités des deux PACS:**

    * PACS1::

        ######################### CURRENT SCP CSTORE ASSOC #########################
        # Server Association metadata
        # update date 		: 2020-07-01 17:28:18.978911
        # simultaneous assoc : 1
        # ----------------------------------------------------------------------------
        # ----------------------------------------------------------------------------
        # action		: CSTORE
        # service		: SCP
        # final_status		: 0x0000 : Association Completed
        # Study UID		: 1.2.124.113532.10.160.160.59.20061018.132504.1343611
        # Series UID		: 1.2.840.113619.2.25.1.1762530585.22006.190.1161189593.1
        # Instance UID		: 1.2.840.113619.2.25.22006.190.1.1161185374
        ##############################################################################

    * PACS2::

        ######################### CURRENT SCU CSTORE ASSOC #########################
        # Server Association metadata
        # update date 		: 2020-07-01 17:28:18.983414
        # ----------------------------------------------------------------------------
        # ----------------------------------------------------------------------------
        # action		: CSTORE
        # service		: SCU
        # final_status		: 0xff00 : Association Pending
        # Study UID		: 1.2.124.113532.10.160.160.59.20061018.132504.1343611
        # Series UID		: 1.2.840.113619.2.25.1.1762530585.22006.190.1161189593.1
        # Instance UID		: 1.2.840.113619.2.25.22006.190.1.1161185374
        ##############################################################################


