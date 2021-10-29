#!/bin/bash

#############INIT_DB################################################################################################
# Script de création de deux bases PACS sur un même daemon Postgre contenerisé.                                    #
# A utiliser pour des fins e dévelopements / environements locaux uniquement.                                      #
# Script adapté sur la base du repo suivant :                                                                      #
# https://github.com/mrts/docker-postgresql-multiple-databases/blob/master/create-multiple-postgresql-databases.sh #
####################################################################################################################

set -e
set -u

function create_user_and_database() {
	local database=$1
	echo "  Creating user and database '$database'"
	psql -v ON_ERROR_STOP=1 --username postgres <<-EOSQL
	    CREATE USER $database WITH PASSWORD '$database';
	    CREATE DATABASE $database;
	    GRANT ALL PRIVILEGES ON DATABASE $database TO $database;
		REVOKE ALL PRIVILEGES ON DATABASE $database FROM PUBLIC
EOSQL

    echo "  Creating PACS Schema for database '$database'"
    psql -v ON_ERROR_STOP=1 --dbname "$database" --username "$database" <<-EOSQL
        CREATE SCHEMA pacs AUTHORIZATION $database;
EOSQL
    
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
	echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
	for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
		create_user_and_database $db
	done
	echo "Multiple databases created"
fi