# Présentation SPHERE <!-- omit in toc -->


## Qu'est-ce que Sphère ?

Sphère (Solution PACS for HEalth REsearch) est un logiciel PACS développé par l'équipe EDS-Imagerie au sein de l'APHP.

Un PACS (système d'archivage et de transmission d'images, ou Picture Archiving and Communication System en anglais)
est un système permettant de gérer les images médicales grâce à des fonctions d'archivage. Il permet la communication
via réseau des images (format DICOM) et donc le traitement à distance ou en réseau local.


Le format DICOM, Digital imaging and communications in medicine, est une norme standard pour la gestion informatique des
données issues de l'imagerie médicale.


## Fonctionnalités principales du PACS Sphère


- la collecte de données DICOM
- l'export de données DICOM

Pour cela les actions possibles sont :

* **C-ECHO  :** Assurer qu'un PACS est à l'écoute
* **C-STORE :** Envoyer les images medicale (DICOM) d'un PACS à un autre PACS
* **C-FIND  :** Chercher les données sur les images medicale (DICOM) dans un PACS (sur une base de données ou directement dans les fichiers)
* **C-MOVE  :** Déplacer les images medicale (DICOM) entre PACS
* **SphereDicomWeb :** C'est un RESTful DICOM services pour l' envoi, la récupération et l' interrogation des images médicales et des informations connexes.
* **Api Annotation :** Une Api qui vous permettez de lier les fichiers d'annotation avec des Instances ou des Séries et le sauvegarder dans un dossie


## Prerequisites


> **_NOTE:_** L'implémentation actuelle de la spehere prend en charge:
                 - Versions de Python 3 de 3.6.1 à 3.8
                 - Version minimale de Python prise en charge est 3.6.1
              Créer une base de donnée PostgreSQL

## Contacts

Les personnes suivantes peuvent êre contacté en fonction du sujet :

- Chef de projet : Aurélien MAIRE @mail: aurelien.maire@aphp.fr
- Lead développeur Python : Ossama ACHOURI @mail : ossama.achouri-ext@aphp.fr

