Sample Module Repository
========================

This simple project is an example repo for Python projects.

`Learn more <http://www.kennethreitz.org/essays/repository-structure-and-python>`_.

---------------

If you want to learn more about ``setup.py`` files, check out `this repository <https://github.com/kennethreitz/setup.py>`_.



sphere
======

Description
-----------


Documentation
-------------


Installation
------------

If prerequisites are met, you can install psycopg like any other Python
package, using ``pip`` to download it from PyPI_::

    $ pip install sphere

or using ``setup.py`` if you have downloaded the source package locally::

    $ python setup.py build
    $ sudo python setup.py install


Usage
-----

utilisation::


    $ python manage.py runserver
    $ python manage.py echo 127.0.0.1 11111 -aec PACS1
    $ python manage.py store 127.0.0.1 11111 -aec PACS1 /home/oac/PACS/PACS1/data/4305052317 true -v 0
    $ python manage.py find 127.0.0.1 11111 -aec PACS1  -l STUDY -v 2 -o study_uid
    $ python manage.py move 127.0.0.1 11111 -aec PACS1 -aes PACS3  -l STUDY -v 0

