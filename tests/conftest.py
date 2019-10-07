import functools
import itertools

import pytest
import session_pool
from pytest_mock import mocker
from session_pool import send_task

import qualys
from qualys import report, Server, Request, Report, Vulner, Patch
import qualys.api as api


class BreakLoop(Exception): pass


status_flow_finished = ['new', 'started', 'running', 'finished']
status_flow_failed = ['new', 'started', 'running', 'failed']
status_flow_only_failed = ['failed', ]


# @pytest.fixture(params=(status_flow_finished, status_flow_failed, status_flow_only_failed))
# def mock_send_task(monkeypatch, request):
#     # status = ['new', 'started', 'running', 'finished', 'failed']
#     status_dict = {'status': request.param}
#
#     status_iter = iter(request.param)
#     class ResponseMock:
#         @staticmethod
#         def json():
#             sd = {'status': next(status_iter)}
#             return sd
#
#         def __init__(self, *args, **kwargs):
#             pass
#
#     def _mock_send_task(*args, **kwargs):
#         sd = {'status': next(status_iter)}
#         # print(sd)
#         return sd
#
#     monkeypatch.setattr(session_pool, 'send_task', ResponseMock)
#
# @pytest.fixture(params=['new', 'started', 'running', 'finished', 'failed'])
# def mock_send_task2(monkeypatch, request):
#     status_dict = {'status': request.param}
#
#
#     def _mock_send_task(*args, **kwargs):
#         return status_dict
#
#     monkeypatch.setattr(session_pool, 'send_task', _mock_send_task)


@pytest.fixture
def mock_api(monkeypatch, mocker):
    """
    Fixture to mock api
    """
    _mock_api = mocker.Mock(spec_set=api.Api)

    monkeypatch.setattr(qualys.api, 'Api', _mock_api)


# @pytest.fixture(params=(status_flow_finished, status_flow_failed, status_flow_only_failed))
@pytest.fixture
def mock_api_get_return_value(monkeypatch, request, mocker):
    """
    Fixture to mock api and set return values for .get() via side_effect
    """

    _mock_api = mocker.Mock(spec_set=api.Api)
    _mock_api().get.return_value = request.param
    monkeypatch.setattr(qualys.api, 'Api', _mock_api)


@pytest.fixture
def mock_api_get_side_effect(monkeypatch, request, mocker):
    """
    Fixture to mock api and set return values for .get() via side_effect
    """

    _mock_api = mocker.Mock(spec_set=api.Api)
    _mock_api().get.side_effect = request.param
    monkeypatch.setattr(qualys.api, 'Api', _mock_api)


@pytest.fixture
def mock_api_post_return_value(monkeypatch, request, mocker):
    """
    Fixture to mock api and set return values for .post() via side_effect
    """
    _mock_api = mocker.Mock(spec_set=api.Api)
    _mock_api().post.return_value = request.param
    monkeypatch.setattr(qualys.api, 'Api', _mock_api)


@pytest.fixture
def mock_api_post_side_effect(monkeypatch, request, mocker):
    """
    Fixture to mock api and set return values for .post() via side_effect
    """
    _mock_api = mocker.Mock(spec_set=api.Api)
    _mock_api().post.side_effect = request.param
    monkeypatch.setattr(qualys.api, 'Api', _mock_api)


@pytest.fixture
def server_mock(mocker, request):
    def server_mock_factory(init_data=None):
        _server_mock = mocker.Mock(spec=Server)
        if init_data:
            _server_mock.id = init_data.get('id',None)
            _server_mock.last_report = init_data.get('last_report', None)
        return _server_mock

    return server_mock_factory


@pytest.fixture
def request_mock(mocker, request):
    def request_mock_factory(init_data=None):
        _request_mock = mocker.Mock(spec_set=Request)
        if init_data:
            _request_mock.id = init_data.get('id', None)
            _request_mock.last_report = init_data.get('last_report', None)
        return _request_mock

    return request_mock_factory


@pytest.fixture
def patch_mock(mocker, request):
    def patch_mock_factory(init_data=None):
        _patch_mock = mocker.Mock(spec_set=Patch)
        if isinstance(init_data, dict):
            _patch_mock.qid = init_data.get('qid', None)
        return _patch_mock

    return patch_mock_factory


@pytest.fixture
def vulner_mock(mocker, request):
    def vulner_mock_factory(init_data=None):
        _vulner_mock = mocker.Mock(spec_set=Vulner)
        if isinstance(init_data, dict):
            _vulner_mock.qid = init_data.get('qid', None)
        return _vulner_mock

    return vulner_mock_factory


@pytest.fixture
def report_mock(mocker):
    def report_mock_factory(cls, init_data=None):
        mocker.patch.object(Report, 'servers')
        mocker.patch.object(Report, 'request')
        test_report = Report()
        test_report.servers = {'1.1.1.1': server_mock(), '2.2.2.2': server_mock()}

