import pytest
from mock import Mock, MagicMock, patch

from qualys.api import QualysApi
from qualys.request import Request
from qualys.db import DictCursorLogged, MysqlApi
from qualys.server import Server


@pytest.fixture
def mock_qualysApi():
    q_api = Mock(spec=QualysApi)
    return q_api


@pytest.fixture
def mock_qualysServer():
    def mock_qualysServer_factory():
        mock_qualysServer
        return mock_qualysServer
    return mock_qualysServer_factory



@pytest.fixture(scope='class')
def patch_QualysServer2Req():
    with patch('qualys.request.QualysServer2Req', spec=True):
        yield

# @pytest.fixture
# def mock_mysqlApi(request):
#     mock_mysqlApi = MagicMock(spec=MysqlApi)
#     mock_cursor = MagicMock(spec=DictCursorLogged)
#     mock_mysqlApi.get_cursor().__enter__.return_value = mock_cursor
#     mock_cursor.fetchone.return_value = request.param
#     return mock_mysqlApi


@pytest.fixture
def mock_mysqlApi():
    """
    Mocks MysqlApi class and sets reutn value for both fetchone() and fetchall()

    Notes:
        In case function will use both calls it will have to be reworked
    Returns:

    """
    def _mock_mysqlApi_factory (db_entry_dict):
        mock_mysqlApi = MagicMock(spec=MysqlApi)
        mock_cursor = MagicMock(spec=DictCursorLogged)
        mock_mysqlApi.get_cursor().__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = db_entry_dict
        mock_cursor.fetchall.return_value = db_entry_dict

        return mock_mysqlApi
    return _mock_mysqlApi_factory


@pytest.fixture
def instance_qualysRequest(mock_mysqlApi, mock_qualysApi):
    def _qualysRequest_factory(data):
        test_request = Request(data['id'], qualysApi=mock_qualysApi, mysqlApi=mock_mysqlApi(data))
        return test_request
    return _qualysRequest_factory


@pytest.fixture
def instance_qualysScan(mock_mysqlApi, mock_qualysApi):
    def _qualysRequest_factory(data):
        test_request = Request(data['id'], qualysApi=mock_qualysApi, mysqlApi=mock_mysqlApi(data))
        return test_request
    return _qualysRequest_factory

@pytest.fixture
def mock_qualysRequest():
    def _qualysRequest_mock_factory(id=0):
        _mock_qualysRequest = MagicMock(spec=Request, id=id)
        return _mock_qualysRequest
    return _qualysRequest_mock_factory

# @pytest.fixture
# def data():
#     _db_dict_data = {
#         'id': 433,
#         'scan_title': 'test1',
#         'status': 'New',
#         'ip': '2.253.233.233,2.253.233.233,2.253.234.57,2.253.234.75',
#         'option_title': 'UNIX/LINUX',
#         'iscanner_name': 'test_appliance_name',
#         'date_time': '2018-07-30 11:05:31',
#         'owner': 'test_user'
#     }
#     return _db_dict_data


# def mockCursor():
#    mock_cursor
