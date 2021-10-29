import os
import uuid
import shutil
import ast
from datetime import datetime

from sqlalchemy import func
import requests

from sphere.dicmeta.database_pacs import DatabasePACS
from sphere.settings import ANNOTATION_PATH_FOLDER, URL_UUID, TYPE_UUID_GENERATOR, DB_PARAMS
from sphere.logs.logs import LOG_API_ANNOTATION
from sphere.utilities.other_utils import check_url


class SaveFile:
    """ save file annotation"""
    def __init__(self, uuid_annotation, file_path=None):
        self.dir_path = ANNOTATION_PATH_FOLDER
        self.source_file_path = file_path
        self.uuid_annotation = uuid_annotation

    def make_dir(self):
        """
        Create folder if not exist
        """
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

    def save(self):
        """
        Save DICOM file

        :return: Absolute path of the DICOM file
        :rtype: str
        """
        destination_file_path = os.path.join(self.dir_path, self.uuid_annotation)
        try:
            # Create sub folder if not exist
            self.make_dir()
            LOG_API_ANNOTATION.debug("destination_file_path = %s", destination_file_path)
            LOG_API_ANNOTATION.info(
                'the file ' + self.source_file_path +
                'was successfully saved at ' + destination_file_path)

            if os.path.exists(self.source_file_path):
                shutil.copy(self.source_file_path, destination_file_path)
            else:
                LOG_API_ANNOTATION.error("This file name '%s' does not exists."
                                         , self.source_file_path)

            return os.path.abspath(destination_file_path)
        except Exception as exc:
            LOG_API_ANNOTATION.error('Error in the save of %s', self.source_file_path)
            LOG_API_ANNOTATION.exception(exc)
            return os.path.abspath(destination_file_path)


class FileInstance:
    """ Insert annotation in database"""
    uuid_annotation = 0

    def __init__(self):
        self.db_pacs = DatabasePACS()

    @classmethod
    def uuid_internal(cls):
        """ get uuid internal"""
        cls.uuid_annotation = str(uuid.uuid1().int)
        LOG_API_ANNOTATION.info("UID Internal (python uuid)")
        LOG_API_ANNOTATION.debug("I used the basic python uuid. "
                                 "uuid_annotation = %s", cls.uuid_annotation)

    @classmethod
    def uuid_external(cls):
        """ Get uuid external"""
        dict_uuid = ast.literal_eval(
            requests.get(URL_UUID).content.decode("utf-8"))
        cls.uuid_annotation = dict_uuid['uuid']
        LOG_API_ANNOTATION.debug(
            "I used the API. uuid_annotation = %s",
            cls.uuid_annotation)

    @classmethod
    def get_uuid(cls):
        """ Get uuid """
        # URL_UUID = "http://127.0.0.1:8000/generate_uuid/annotation/INSTANCE"
        if TYPE_UUID_GENERATOR == 'INTERNAL':
            cls.uuid_internal()
        elif TYPE_UUID_GENERATOR == "EXTERNAL":
            if check_url(URL_UUID):
                cls.uuid_external()
            else:
                LOG_API_ANNOTATION.error(
                    "No uuid because this url '%s' is disable so no insertion "
                    "in database. You must modify this 'type_uuid_generator' "
                    "parameter with 'INTERNAL' or 'MIXED' if you want to add"
                    " the annotations.", URL_UUID)
        elif TYPE_UUID_GENERATOR == "MIXED":
            LOG_API_ANNOTATION.info(
                "UID Mixed (Used API or Python uuid if API not found")
            if check_url(URL_UUID):
                cls.uuid_external()
            else:
                LOG_API_ANNOTATION.warning("This url '%s' is disable so I used "
                                           "uuid_internal")
                cls.uuid_internal()
        else:
            LOG_API_ANNOTATION.error("%s not in this list ['INTERNAL', "
                                     "'MIXED', 'EXTERNAL']", TYPE_UUID_GENERATOR)

    def check_uid_exist(self, column_name, uid):
        """
        Check if uid exists

        :param column_name: The column name
        :type column_name: str
        :param uid: The uid
        :type uid: str
        :return: True if uid exists else False
        :rtype: bool
        """
        try:

            session = self.db_pacs.create_session()
            if "instance" in column_name:
                query = session.query(self.db_pacs.FileStorageMetadataDicomModel)
                query = query.filter(self.db_pacs.FileStorageMetadataDicomModel.instanceUID == uid)
            else:
                query = session.query(self.db_pacs.SeriesModel)
                query = query.filter(self.db_pacs.SeriesModel.seriesUID == uid)
            query = query.with_entities(func.count())
            id_count = query.scalar()
            LOG_API_ANNOTATION.debug("Number of '%s'  is %s", column_name, id_count)
            self.db_pacs.clear_session(session)
            if not id_count:
                LOG_API_ANNOTATION.error("This %s '%s' does not exists in "
                                         "database", column_name, uid)
                return False
            return True
        except Exception as exc:
            LOG_API_ANNOTATION.exception(exc)
            return False

    def insert_annotation(self, data_json=None):
        """ Insert annotation in table storage_metadata """
        # List all files

        file_path = data_json.get('file_path')
        uid = data_json.get('uid')
        level = data_json.get('level')

        try:
            if level.upper() == "INSTANCE":
                column_name = "instance_uid"
            else:  # SERIES
                column_name = "series_uid"

            res_check = self.check_uid_exist(column_name, uid)

            self.get_uuid()
            if res_check and self.uuid_annotation:
                LOG_API_ANNOTATION.debug(
                    "Start insert annotation data_json = %s", data_json)

                save_file = SaveFile(self.uuid_annotation, file_path)
                destination_file_path = save_file.save()

                # storage_metadata = sm
                file_sm_dicom = self.db_pacs.FileStorageMetadataDicomModel()

                file_sm_dicom.dt_deb_storage = datetime.now()
                file_sm_dicom.instanceUID = self.uuid_annotation
                file_sm_dicom.filesize = os.stat(file_path).st_size
                file_sm_dicom.storageMethod = 'api_annotation'
                file_sm_dicom.storageStatus = 0
                file_sm_dicom.filePath = destination_file_path
                file_sm_dicom.dt_end_storage = datetime.now()

                self.db_pacs.create_or_update_model(
                    file_sm_dicom, check_key=False, update=True, nested_level=2)
                # self.db_pacs.insert(storage_metadata, nested_level=2)

                # mapping_annotation
                mapping_annotation = self.db_pacs.MappingAnnotationModel()
                mapping_annotation.uid_dicom_source = uid
                mapping_annotation.uid_annotation = self.uuid_annotation
                mapping_annotation.level_dicom_source = level
                mapping_annotation.storage_metadata_id = file_sm_dicom.id

                # create table if not exists
                tablename = self.db_pacs.MappingAnnotationModel.__tablename__
                schema = DB_PARAMS['schema']
                is_exists = self.db_pacs.table_exists(tablename, schema)
                if not is_exists:
                    self.db_pacs.create_tables()
                    LOG_API_ANNOTATION.warning(
                        "The '%s' table does not exist in database so I will "
                        "create it in this schema '%s'.", tablename, schema)

                self.db_pacs.insert(mapping_annotation, nested_level=2)

        except Exception as error:
            LOG_API_ANNOTATION.exception(error)
