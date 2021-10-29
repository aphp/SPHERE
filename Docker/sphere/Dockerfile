# Image de base dédiée à la compilation du wheel Python de SPHERE
FROM python:3.8.6-slim-buster as builder

LABEL MAINTAINER="kevin.zgrzendek-ext@aphp-fr"

# Récupération des packages nécéssaires à la compilation
RUN apt-get update &&\
    apt-get install -y --no-install-recommends build-essential gcc &&\
    apt-get clean

#Création d'un environement virtuel qui pourra être porté sur l'image finale
RUN python -m venv /opt/sphere/env

# Ajout de l'environement virtuel au PATH
ENV PATH="/opt/sphere/env/bin:$PATH"

# Répertoire de build
WORKDIR /tmp/build

# Copie de la distribution à installer présente dans le répertoire dist/ 
# Version dummy dans le container pour éviter de devoir maj la dockerfile à chaque changement de version applicative
COPY dist/sphere-*-py3-none-any.whl dist/sphere-1.0-py3-none-any.whl

# Installation du wheel dans l'environement virtuel dédié
RUN pip3 install --no-cache-dir --upgrade pip &&\
    pip3 install --no-cache-dir  dist/sphere-1.0-py3-none-any.whl &&\
    rm -rf dist/


# Image finale ne contenant que l'application SPHERE
FROM python:3.8.6-slim-buster

# Création du user applicatif dédié et du groupe correspondant
RUN addgroup sphere &&\
    useradd sphere -g sphere -s /bin/false

# Récupération de l'environement virtuel l'image précédente et application des droits pour le user applicatif
COPY --from=builder --chown=sphere:sphere /opt/sphere/ /opt/sphere/

# Répertoire appplicatif (FHS)
WORKDIR /opt/sphere

# Utilisation du user applicatif pour le container
USER sphere

# Ajout de l'environement virtuel de l'application SPHERE au PATH du user applicatif
ENV PATH="/opt/sphere/env/bin:$PATH"

# Création du PACS
RUN sphere-admin pacs

# Répertoire d'éxecution du PACS SPHERE
WORKDIR /opt/sphere/pacs

# Commande par défaut lors du démarrage du container (non-overidable) : lancement du serveur PACS SPHERE 
ENTRYPOINT ["python3", "manage.py", "runserver"]

# Exposition des ports PACS SPHERE + API REST
EXPOSE 8080 11112