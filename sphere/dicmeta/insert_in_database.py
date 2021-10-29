""" Insert data in database with bulk"""
# pylint: disable=too-many-locals
from sphere.dicmeta.database_pacs import DatabasePACS
from sphere.logs.logs import LOG_DATABASE


class InsertData:
    number_insert = 0

    def __init__(self, db_pacs=None):
        if db_pacs is None:
            # TODO better integration with no dynamic import
            from .thread import g_queue_to_load
            self.db_pacs = DatabasePACS(g_queue_to_load)
        else:
            self.db_pacs = db_pacs

    def bulk_insert_from_queue(self, queue):
        """

        :param queue:
        :type queue:
        """
        group_dict = {
            'patient': {},
            'study': {},
            'series': {},
            'instance': {}
        }

        # Tous les element dans la queue sont dedupliquer
        size = 0
        while not queue.empty() and size < 10000:
            LOG_DATABASE.debug('in while dcm save %s', queue.qsize())
            #print('in while dcm save ', queue.qsize())
            for model, m_inst in queue.get().items():
                group_dict[model][getattr(m_inst, m_inst.KEY)] = m_inst
            size += 1
            if size > 10000:
                break
        LOG_DATABASE.info('Prepare to insert :')
        print('Prepare to insert :')
        self.number_insert = size
        for model in group_dict:
            msg = " - %s %s" % (len(group_dict[model]), model)
            LOG_DATABASE.debug(msg)
            print(msg)

        session = self.db_pacs.create_session()

        # Vide les tables temporaires
        list_model_tmp = [
            self.db_pacs.TempPatientModel.__table__,
            self.db_pacs.TempStudyModel.__table__,
            self.db_pacs.TempSeriesModel.__table__,
            self.db_pacs.TempFileStorageMetadataModel.__table__
        ]

        self.db_pacs.metadata_table.drop_all(self.db_pacs.engine,
                                             list_model_tmp)
        self.db_pacs.metadata_table.create_all(self.db_pacs.engine,
                                               list_model_tmp)

        # Chargement des données
        self.patient_bulk_insert(group_dict['patient'], session)
        self.study_bulk_insert(group_dict['study'], session)
        self.series_bulk_insert(group_dict['series'], session)
        self.instance_bulk_insert(group_dict['instance'], session)

        # Vide les tables temporaires
        self.db_pacs.metadata_table.drop_all(self.db_pacs.engine,
                                             list_model_tmp)

        session.close()

    @staticmethod
    def columns_generator(model, table=None):
        """
        Generate list of model columns excluse id and d8

        :param model: The model
        :type model: :py:class:`sphere.dicmeta.temp_models.temp_patient_model.TempPatientModel` or
            :py:class:`sphere.dicmeta.temp_models.temp_study_model.TempStudyModel` or ...
        :param table: Name of table
        :type table: str
        :return: List of table column name
        :rtype: list [str]
        """

        keys = model.__table__.columns.keys()

        sub_columns = []
        for v in keys:  # pylint: disable=invalid-name
            # if 'd8' not in v and 'tmp_' not in v: sub_columns += ['.'.join(filter(None, [table,v]))]
            if 'tmp_' not in v:
                sub_columns += ['.'.join(filter(None, [table, v]))]
        return sub_columns

    def patient_bulk_insert(self, data, session):
        """
        Insert the patients in the temporary patient table then in the base table

        :param data: The data of patient
        :type data: dict
        :param session: The session
        :type session: :py:class:`sqlalchemy.orm.session.Session`
        """
        model = self.db_pacs.PatientModel()
        tmp_model = self.db_pacs.TempPatientModel()

        key = 'patient_uid'
        tmp_table = tmp_model.table_full_name()
        table = model.table_full_name()
        columns = self.columns_generator(tmp_model)

        msg = "---- Start patient bulk temporary insert ---"
        LOG_DATABASE.info(msg)
        print(msg)
        data_to_insert = [v.dict_data() for k, v in data.items()]
        session.bulk_insert_mappings(tmp_model, data_to_insert)
        session.commit()

        msg = "---- Start de-duplicate patient insert ---"
        LOG_DATABASE.info(msg)
        print(msg)
        request_deduplicate = """DELETE FROM
                                %s x
                                USING %s y
                                WHERE
                                x.d8ins < y.d8ins
                                AND x.%s = y.%s;""" % (
                                    tmp_table, tmp_table, key, key)

        session.execute(request_deduplicate)
        session.commit()

        msg = "---- Start merge upsert patient ---"
        LOG_DATABASE.info(msg)
        print(msg)

        upsert_request = """INSERT INTO %s (%s)
                        SELECT %s
                        FROM %s
                        ON CONFLICT (%s)
                        DO NOTHING""" % (table, ','.join(columns),
                                         ','.join(columns),
                                         tmp_table,
                                         key,)

        session.execute(upsert_request)
        session.commit()

        msg = "---- End patient insert ---"
        LOG_DATABASE.info(msg)
        print(msg)

    def study_bulk_insert(self, data, session):
        """
        Insert the studies in the temporary study table then in the base table

        :param data: The data of study
        :type data: dict
        :param session: The session
        :type session: :py:class:`sqlalchemy.orm.session.Session`
        """
        model = self.db_pacs.StudyModel()
        tmp_model = self.db_pacs.TempStudyModel()

        key = 'study_uid'
        tmp_table = tmp_model.table_full_name()
        table = model.table_full_name()
        columns = self.columns_generator(tmp_model)
        columns_table = self.columns_generator(tmp_model,
                                               tmp_model.__tablename__)

        patient_key = 'patient_uid'
        patient_id = 'patient_id'
        patient_table = self.db_pacs.PatientModel().table_full_name()

        msg = "---- Start study bulk temporary insert ---"
        LOG_DATABASE.info(msg)
        print(msg)
        data_to_insert = [v.dict_data() for k, v in data.items()]
        session.bulk_insert_mappings(tmp_model, data_to_insert)
        session.commit()

        msg = "---- Start de-duplicate study insert ---"
        LOG_DATABASE.info(msg)
        print(msg)
        request_deduplicate = """DELETE FROM
                                %s x
                                USING %s y
                                WHERE
                                x.d8ins < y.d8ins
                                AND x.%s = y.%s;""" % (
                                    tmp_table, tmp_table, key, key)

        session.execute(request_deduplicate)
        session.commit()

        msg = "---- Start merge upsert study ---"
        LOG_DATABASE.info(msg)
        print(msg)

        upsert_request = """INSERT INTO %s (%s, %s)
                        SELECT %s, %s
                        FROM %s JOIN %s ON (%s=%s)
                        ON CONFLICT (%s)
                        DO NOTHING""" % (table, ','.join(columns), patient_id,
                                         ','.join(columns_table), patient_id,
                                         tmp_table, patient_table,
                                         '.'.join([patient_table, patient_key]),
                                         '.'.join([tmp_table, patient_key]),
                                         key,)
        LOG_DATABASE.debug("upsert_request = %s", upsert_request)
        print(upsert_request)
        session.execute(upsert_request)
        session.commit()

        msg = "---- End study insert ---"
        LOG_DATABASE.info(msg)
        print(msg)

    def series_bulk_insert(self, data, session):
        """
        Insert the series in the temporary series table then in the base table

        :param data: The data of series
        :type data: dict
        :param session: The session
        :type session: :py:class:`sqlalchemy.orm.session.Session`
        """
        model = self.db_pacs.SeriesModel()
        tmp_model = self.db_pacs.TempSeriesModel()

        key = 'series_uid'
        tmp_table = tmp_model.table_full_name()
        table = model.table_full_name()
        columns = self.columns_generator(tmp_model)
        columns_table = self.columns_generator(tmp_model,
                                               tmp_model.__tablename__)

        patient_key = 'patient_uid'
        patient_id = 'patient_id'
        patient_table = self.db_pacs.PatientModel().table_full_name()

        study_key = 'study_uid'
        study_id = 'study_id'
        study_table = self.db_pacs.StudyModel().table_full_name()

        msg = "---- Start series bulk temporary insert ---"
        LOG_DATABASE.info(msg)
        print(msg)
        data_to_insert = [v.dict_data() for k, v in data.items()]
        session.bulk_insert_mappings(tmp_model, data_to_insert)
        session.commit()

        msg = "---- Start de-duplicate series insert ---"
        LOG_DATABASE.info(msg)
        print(msg)
        request_deduplicate = """DELETE FROM
                                %s x
                                USING %s y
                                WHERE
                                x.d8ins < y.d8ins
                                AND x.%s = y.%s;""" % (
                                    tmp_table, tmp_table, key, key)

        session.execute(request_deduplicate)
        session.commit()

        msg = "---- Start merge upsert series ---"
        LOG_DATABASE.info(msg)
        print(msg)

        upsert_request = """INSERT INTO %s (%s, %s, %s)
                        SELECT %s, %s, %s
                        FROM %s JOIN %s ON (%s=%s)
                        JOIN %s ON (%s=%s)
                        ON CONFLICT (%s)
                        DO NOTHING""" % (
            table, ','.join(columns), patient_id, study_id,
            ','.join(columns_table), '.'.join(['patient', patient_id]), study_id,
            tmp_table, patient_table, '.'.join([patient_table, patient_key]),
            '.'.join([tmp_table, patient_key]),
            study_table, '.'.join([study_table, study_key]),
            '.'.join([tmp_table, study_key]),
            key,)

        LOG_DATABASE.debug("upsert_request = %s", upsert_request)
        print(upsert_request)
        session.execute(upsert_request)
        session.commit()

        msg = "---- End series insert ---"
        LOG_DATABASE.info(msg)
        print(msg)

    def instance_bulk_insert(self, data, session):
        """
        Insert the instances in the temporary instance table then in the base table

        :param data: The data of instance
        :type data: dict
        :param session: The session
        :type session: :py:class:`sqlalchemy.orm.session.Session`
        """
        model = self.db_pacs.FileStorageMetadataDicomModel()
        tmp_model = self.db_pacs.TempFileStorageMetadataModel()

        key = 'instance_uid'
        tmp_table = tmp_model.table_full_name()
        table = model.table_full_name()
        columns = self.columns_generator(tmp_model)
        columns_table = self.columns_generator(tmp_model,
                                               tmp_model.__tablename__)

        patient_key = 'patient_uid'
        patient_id = 'patient_id'
        patient_table = self.db_pacs.PatientModel().table_full_name()

        study_key = 'study_uid'
        study_id = 'study_id'
        study_table = self.db_pacs.StudyModel().table_full_name()

        series_key = 'series_uid'
        series_id = 'series_id'
        series_table = self.db_pacs.SeriesModel().table_full_name()

        msg = "---- Start instance bulk temporary insert ---"
        LOG_DATABASE.info(msg)
        print(msg)
        data_to_insert = [v.dict_data() for k, v in data.items()]
        session.bulk_insert_mappings(tmp_model, data_to_insert)
        session.commit()

        msg = "---- Start de-duplicate instance insert ---"
        LOG_DATABASE.info(msg)
        print(msg)

        request_deduplicate = """DELETE FROM
                                %s x
                                USING %s y
                                WHERE
                                x.d8ins < y.d8ins
                                AND x.%s = y.%s;""" % (
                                    tmp_table, tmp_table, key, key)

        session.execute(request_deduplicate)
        session.commit()

        msg = "---- Start merge upsert instance ---"
        LOG_DATABASE.info(msg)
        print(msg)

        upsert_request = """INSERT INTO %s (%s, %s, %s, %s)
                        SELECT %s, %s, %s, %s
                        FROM %s JOIN %s ON (%s=%s)
                        JOIN %s ON (%s=%s)
                        JOIN %s ON (%s=%s)
                        ON CONFLICT (%s)
                        DO NOTHING""" % (
            table, ','.join(columns), patient_id, study_id, series_id,
            ','.join(columns_table), '.'.join(['patient', patient_id]),
            '.'.join(['study', study_id]), series_id,
            tmp_table, patient_table, '.'.join([patient_table, patient_key]),
            '.'.join([tmp_table, patient_key]),
            study_table, '.'.join([study_table, study_key]),
            '.'.join([tmp_table, study_key]),
            series_table, '.'.join([series_table, series_key]),
            '.'.join([tmp_table, series_key]),
            key,)

        LOG_DATABASE.debug("upsert_request = %s", upsert_request)
        print(upsert_request)
        session.execute(upsert_request)
        session.commit()

        msg = "---- End instance insert ---"
        LOG_DATABASE.info(msg)
        print(msg)
