import sys
from pprint import pprint

import pytest
import mock
import requests

from qualys.request import Request, QualysServer2Req
from tests.data_test_db import data_dict_e, test_data_simple, test_data_combined, template_valid




@pytest.mark.usefixtures('patch_QualysServer2Req')
# @mock.patch('qualys.scan.qualysServer')
class TestQualysRequest:

    @pytest.mark.parametrize('data', test_data_simple)
    def test_update_db_call(self, instance_qualysRequest, data):
        test_request = instance_qualysRequest(data)
        test_request.update()
        expected = ('UPDATE request SET status = %s WHERE id = %s', (data['status'], int(data['id'])))
        test_request._mysqlApi.get_cursor().__enter__.return_value.execute.assert_any_call(*expected)

    @pytest.mark.parametrize('data', test_data_combined)
    def test_initalize_by_id_valid(self, instance_qualysRequest, data):
        test_request = instance_qualysRequest(data)
        expected = {
            '_id': data['id'],
            '_status': data['status'],
            'title': data['scan_title'],
            # '_ip': [], #
            '_owner': data['owner'],
            'platform': 'UX' if data['option_title'] == 'UNIX/LINUX' else 'WIN' # TODO: rework? same as function implementation
        }

        current = {k:v for k,v in test_request.__dict__.items() if k in expected.keys()}
        assert current == expected

    @pytest.mark.parametrize('data', template_valid)
    def test_initialize_servers(self, instance_qualysRequest, data):
        # test_request = instance_qualysRequest(test_data_simple[0])
        test_request = instance_qualysRequest(data)
        assert all([isinstance(item, QualysServer2Req) for item in test_request.servers.values()])



    # @pytest.mark.parametrize(
    #     ("n", "m"),
    #     [
    #         # (1, 2),
    #         # 1/0
    #         # 1/0
    #         pytest.param(1, 0, id='testname', marks=[pytest.mark.xfail(raises=ZeroDivisionError)]),
    #         pytest.param(1, 0, marks=[pytest.mark.skipif(2 > 1, reason='Testin multiple marks'),
    #                                   pytest.mark.xfail(raises=ZeroDivisionError)]),
    #         pytest.param(1, 0,
    #                      marks=[pytest.mark.xfail(raises=ZeroDivisionError), pytest.mark.xfail(raises=(TypeError))]),
    #         pytest.param(1, 0, marks=[pytest.mark.xfail(raises=(ZeroDivisionError, TypeError))]),
    #     ],
    #     # ids=['prva','druha']
    # )
    # def test_xfail(self, n, m):
    #     n / m
    #     assert 1

    # @pytest.mark.parametrize('m',[1,2])
    # @pytest.mark.parametrize('n',[3,4])
    # def test_mutltiple_param(self, n, m):
    #     print('m:{}\nn:{}'.format(m, n))
    #     assert 1

    # @pytest.mark.parametrize(
    #     ("n", "expected"),
    #     [
    #         (1, 2),
    #         pytest.param(1, 0, marks=pytest.mark.xfail),
    #         pytest.param(1, 3, marks=pytest.mark.xfail(reason="some bug")),
    #         (2, 3),
    #         (3, 4),
    #         (4, 5),
    #         pytest.param(
    #             10, 11, marks=pytest.mark.skipif(sys.version_info >= (3, 0), reason="py2k")
    #         ),
    #     ],
    # )
    # def test_increment(self, n, expected):
    #     assert n + 1 == expected
