import pytest
from mock import call
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from qualys.db import get_data_from_file, init_db

servercmdb_file_content = '[{"id": 1, "hostname": "lxem1", "ip": "10.0.1.1", "platform": "linux", "region": "EMEA"}, {"id": 2, "hostname": "lxem2", "ip": "10.0.1.2", "platform": "linux", "region": "EMEA"}]'
servercmdb_data = [{'hostname': 'lxem1', 'id': 1, 'ip': '10.0.1.1', 'platform': 'linux', 'region': 'EMEA'},
                   {'hostname': 'lxem2', 'id': 2, 'ip': '10.0.1.2', 'platform': 'linux', 'region': 'EMEA'},
                   ]

@pytest.fixture
def get_sqlalchemy_session(module_scoped_):
    pass


def test_init_db(module_scoped_container_getter):
    test_db_uri = 'mysql+pymysql://root:123456@localhost:53307/qualys_scan'
    engine = init_db(test_db_uri)


    result = dict(engine.execute(('select * from `cmdb`.server where id = 1')).fetchone())

    assert result == servercmdb_data[0]


@pytest.mark.parametrize('file_content, expected', ((servercmdb_file_content, servercmdb_data),))
def test_get_data_from_file(mocker, file_content, expected):
    m = mocker.mock_open()
    mocker.patch('qualys.db.open', m)

    handle = m()
    handle.read.return_value = file_content

    result = get_data_from_file('file_name')

    assert m.call_args_list == [call(), call('file_name', 'r')]
    handle.read.assert_called_once_with()
    assert result == expected

