import logging
from datetime import datetime

from qualys.qualys_item import QualysBaseItem
from qualys.server import Server
from qualys import cfg

logger = logging.getLogger('qualys.oat')

class Oat(QualysBaseItem):
    def __init__(self, server: Server, owner: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server = server
        self._oat_id = self._get_oat_id()
        self._oat_run_id = None
        self._owner = owner

    def _get_oat_id(self):

        with self._mysqlApi.get_cursor(db_name=cfg.OPS_DB) as cursor:
            sql = 'SELECT id FROM oat_ticket WHERE server_id = %s'
            values = self.server.id
            cursor.execute(sql, values)
            self._mysqlApi.commit()
            row = cursor.fetchone()
            if not row:
                # raise Exception('No oat found for server')
                logger.warning('No oat found for server: {}'.format(self.server.hostname))
            return row['id']

    def _add_oat_run_entry(self):
        with self._mysqlApi.get_cursor(db_name=cfg.OPS_DB) as cursor:
            # sql = "UPDATE qualys_scan SET status  = %s,  WHERE id = %s"

            sql = '''INSERT INTO oat_run SET
                        tester_name = %s,
                        input_method = %s,
                        rundatetime = %s,
                        oat_ticket_id = %s
                '''

            values = (
                self._owner,
                'script',
                str(datetime.now()),
                self._oat_id
                )
            cursor.execute(sql, values)
            self._mysqlApi.commit()
            self._oat_run_id = cursor.lastrowid
            # logger.debug('{} status updated ({})'.format(self.title, self.status))

    def _add_oat_check_entry(self, passed, message):
        with self._mysqlApi.get_cursor(db_name=cfg.OPS_DB) as cursor:
            sql = '''INSERT INTO oat_check SET
                        oat_run_id = %s,
                        oat_version = %s,
                        oat_type = %s,
                        oat_product = %s,
                        oat_group = %s,
                        oat_check = %s,
                        script_version  = %s,
                        how_checked = %s,
                        pass = %s,
                        output = %s,
                        problem = %s  
                    '''

            values = (
                self._oat_run_id,
                '1.0',
                'OS',
                self.server.os_category,
                'SECURITY',
                'SCRIPT_NAME_TBD',
                None,
                'script',
                passed,
                message,
                int(not passed)

            )
            cursor.execute(sql, values)
            self._mysqlApi.commit()

    def update_oat_flow(self, passed, message):
        self._add_oat_run_entry()
        self._add_oat_check_entry(passed, message)

    def test(self):
        with self._mysqlApi.get_cursor() as cursor:
            cursor.execute('show tables')
            print(cursor.fetchall())
