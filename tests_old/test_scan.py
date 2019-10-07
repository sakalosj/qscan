import pytest
import mock

# @mock.patch('qualys.scan.qualysServer')
from qualys.api import QualysApi
from qualys.scan import Scan
# from qualys.request import QualysRequest
from qualys.server import Server

qualys_scan_param = {'qualys_request': mock.MagicMock('QualysRequest'),
                     'region': 'EMEA',
                     'server': 'test.server.tst'
                     }

mock_qualysServer = mock.MagicMock(spec=Server)
mock_qualysApi = mock.MagicMock(spec=QualysApi)
# mock_qualysRequest = mock.MagicMock(spec=QualysRequest)


ops_server_table_sample = [
    {"id": 0,
     "status": "Running",
     "scan_title": "title0",
     },
    {"id": 1,
     "status": "Finished",
     "scan_title": "title1",
     },
    {"id": 2,
     "status": "ERR_test",
     "scan_title": "title2",
     },
]


# @mock.patch('qualys.qualys_item.MysqlApi', spec=True)
@mock.patch('qualys.qualys_item.QualysApi', mock.MagicMock(), spec=True)
class TestQualysScan:

    # mock_mysqlApi =
    # @pytest.mark.parametrize()
    # def test_check_if_exist_return_value(self, mock_mysqlApi, mock_qualysRequest, *args):
    #     m = mock_mysqlApi(ops_server_table_sample[1])
    #     test_scan = QualysScan(mock_qualysRequest(), 'EMEA', [mock_qualysServer],
    #                            'test_scan', mysqlApi=m)
    #
    #     assert True

    @pytest.mark.parametrize('server_query',
                             ops_server_table_sample,
                             ids=['valid_runnig', 'valid_finished', 'valid_err']
                             )
    def test__init__existent_server(self, server_query, mock_mysqlApi, mock_qualysRequest):
        """
            TODO: add self.servers to assert if entry found, ???split test???
        """
        # def __init__(self, qualys_request, region, servers, title, *args, **kwargs):
        test_scan = Scan(mock_qualysRequest(), 'EMEA', [mock_qualysServer], 'test_scan',
                         mysqlApi=mock_mysqlApi(server_query), qualysApi=mock_qualysApi)
        current = {
            'id': test_scan._id,
            'status': test_scan.status,
            'scan_title': test_scan.title,
        }

        expected = server_query
        # current = {k: v for k, v in test_scan.__dict__.items() if k in expected.keys()}
        assert expected == current

    @pytest.mark.parametrize('server_query',
                             [None],
                             ids=['none']
                             )
    def test__init__nonexistent_server(self, server_query, mock_mysqlApi, mock_qualysRequest, *args):
        """
            TODO: add self.servers to assert if entry found, ???split test???
        """
        # def __init__(self, qualys_request, region, servers, title, *args, **kwargs):
        test_scan = Scan(mock_qualysRequest(), 'EMEA', [mock_qualysServer], 'test_scan',
                         mysqlApi=mock_mysqlApi(server_query))
        current = {
            'id': test_scan._id,
            'status': test_scan.status,
            'scan_title': test_scan.title,
        }

        expected = {
            'id': None,
            'status': 'New',
            'scan_title': test_scan.title,
        }

        assert expected == current
