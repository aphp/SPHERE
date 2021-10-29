.. _introduction:

Introduction
============

Qu'est-ce que Sphère ?
------------------------

Sphère (Solution PACS for HEalth REsearch) est un logiciel PACS développé par l'équipe EDS-Imagerie au sein de l'APHP.

Un PACS (système d'archivage et de transmission d'images, ou Picture Archiving and Communication System en anglais)
est un système permettant de gérer les images médicales grâce à des fonctions d'archivage. Il permet la communication
via réseau des images (format DICOM) et donc le traitement à distance ou en réseau local.


Le format DICOM, Digital imaging and communications in medicine, est une norme standard pour la gestion informatique des
données issues de l'imagerie médicale.


Fonctionnalités principales du PACS Sphère
------------------------------------------


- la collecte de données DICOM
- l'export de données DICOM

Pour cela les actions possibles sont :

* **C-ECHO  :** Assurer qu'un PACS est à l'écoute
* **C-STORE :** Envoyer les images medicale (DICOM) d'un PACS à un autre PACS
* **C-FIND  :** Chercher les données sur les images medicale (DICOM) dans un PACS (sur une base de données ou directement dans les fichiers)
* **C-MOVE  :** Déplacer les images medicale (DICOM) entre PACS
* **SphereDicomWeb :** C'est un RESTful DICOM services pour l' envoi, la récupération et l' interrogation des images médicales et des informations connexes.
* **Api Annotation :** Une Api qui vous permettez de lier les fichiers d'annotation avec des Instances ou des Séries et le sauvegarder dans un dossie

Architecture Cible Sphere
-------------------------


.. image:: ../../_static/Architecture_Cible_Sphere.pdf
  :width: 500
  :align: center



Définition
----------

Sphere
^^^^^^

SPHERE (Solution PACS for Health REsearch) est une solution de Picture Archiving and communication System (PACS)
(eq. en français un système d'archivage et de transmission d'images).
Il permet la communication via réseau d'image au format DICOM (Digital imaging and communications in medicine, en francais
imagerie digitale et communication en médecine) selon le protocole DICOM (https://www.dicomstandard.org/).
SPHERE permet également le stockage des fichiers DICOM sur le file system de la machine où est lancé SPHERE ou sur un
Hadoop Distributed File System (HDFS) cette partie nécessite un répertoire HDFS présent ainsi qu'une gestion des droits
permettant au logiciel d'écrire dans ce répertoire.
SPHERE est pourvue d'une base de données Postgresql qui se remplit a chaque réception de fichier DICOM cette partie nécessite
une base de données Postgresql, SPHERE permet également une utilisation sans base de données.
Dans le fonctionnement sans base de données a chaque requettes SPHERE parcours l'ensemble des DICOM présent dans son dossier
de stockage des DICOM ce qui prend beaucoup plus de temps qu'avec la base de données.
SPHERE respecte les standards DICOM fixé par la NEMA (National Electrical Manufacturers Association) donc il permet
la communication avec d'autres solutions PACS, ou des visualiseurs DICOM utilisant le protocole DICOM.
Un PACS SPHERE est capable d'utiliser les actions DICOM, c-store, c-move, c-find, c-echo aussi bien en écoute
(SCU, Service Class User) qu'en envoit (SCP, Service Class Provider). De plus, il incorpore
une API (interface de programmation applicative) dicomweb (activable ou non) qui permet la communication avec les visualiseurs
utilisant cette méthode de connexion plutôt que le protocole DICOM.

PACS
^^^^

Un système d'archivage d'image et de communication ( PACS ) est une imagerie médicale technologie qui permet
le stockage économique et un accès facile à des images provenant de plusieurs modalités (types de machines à la source).
Les images électroniques et les rapports sont transmis sous forme numérique via PACS; ce qui élimine la nécessité de déposer
manuellement, récupérer, ou transporter des vestes de films, les dossiers utilisés pour stocker et protéger des rayons X film.
Le format universel pour le stockage d'images PACS et le transfert est DICOM (Digital Imaging and Communications in Medicine) .
Les données non-image, tels que scannées des documents, peuvent être incorporés en utilisant des formats standards
de l' industrie des consommateurs comme format PDF (Portable Document Format) , une fois encapsulées dans DICOM.
Un PACS est constitué de quatre éléments principaux: Les modalités d'imagerie telles que la feuille (PF) brut de rayons X,
la tomographie par ordinateur (CT) et l' imagerie par résonance magnétique (IRM), une garantie réseau pour la transmission
de l' information du patient, des postes de travail pour l' interprétation et l' examen des images et des archives
pour le stockage et la récupération des images et des rapports. Combiné avec disponibles et émergents web technologie,
PACS a la capacité de fournir un accès rapide et efficace aux images, des interprétations et des données connexes.
PACS réduit les barrières physiques et le temps associés à la traditionnelle sous forme de film recherche d'images,
la distribution et l' affichage. [#f2]_


DICOM
^^^^^

Digital Imaging et des communications en médecine ( DICOM ) est la norme pour la communication et la gestion des informations
d'imagerie médicale et les données connexes. DICOM est le plus couramment utilisé pour le stockage et la transmission
d' images médicales permettant l'intégration d'appareils d'imagerie médicale tels que des scanners, des serveurs,
des postes de travail, des imprimantes, matériel de réseau et d' archivage d'images et de systèmes de communication (PACS)
provenant de plusieurs fabricants. Il a été largement adopté par les hôpitaux , et faire des incursions dans des applications
plus petites comme et des médecins des cabinets de dentistes.

Les fichiers DICOM peuvent être échangés entre deux entités qui sont capables de recevoir l' image et les données du patient
au format DICOM. Les différents appareils sont livrés avec déclarations de conformité DICOM qui indiquent clairement
quelles classes DICOM qu'ils soutiennent, et la norme comprend un format de fichier définition et un réseau protocole
de communication qui utilise le protocole TCP / IP pour communiquer entre les systèmes.

La National Electrical Manufacturers Association (NEMA) détient le droit d' auteur à cette norme qui a été élaboré
par le Comité des normes DICOM, dont les membres sont également en partie les membres de la NEMA. Il est également connu
sous le nom NEMA PS3 standard, et en tant que norme ISO 12052: 2017 « Informatique de santé - imagerie numérique
et de la communication en médecine (DICOM) , y compris la gestion des flux et des données ». [#f1]_



.. rubric:: Footnotes

.. [#f1] https://fr.qwe.wiki/wiki/DICOM
.. [#f2] https://fr.qwe.wiki/wiki/Picture_archiving_and_communication_system
