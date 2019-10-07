import itertools
from collections import defaultdict

import pytest

from qualys import Report, Patch, Vulner

# status_flow_finished = ['new', 'started', 'running', 'finished']
# status_flow_failed = ['new', 'started', 'running',  'failed']
# status_flow_only_failed = ['failed',]
# status_flows = [status_flow_finished, status_flow_failed, status_flow_only_failed]
status_flows = [['new', 'started', 'running', 'finished'],
                ['new', 'started', 'running', 'failed'],
                ['failed', ]]
status_flows_json = [[{'status': status} for status in single_flow] for single_flow in status_flows]

test_report_data = {'datetime': '2019-09-26T00:23:04', 'id': 42,
                    'servers': [{'ip': '1.1.1.1'}, {'ip': '2.2.2.2'}],
                    'servers_data': {
                        '1.1.1.1': {
                            'patches': [{'qid': 1, 'severity': 1, 'title': 'Patch 1'},
                                        {'qid': 11, 'severity': 11, 'title': 'Patch 11'}, ],
                            'vulners': [{'patch_qid_fk': '1', 'qid': 1, 'severity': 1, 'title': 'Vulner 1'},
                                        {'patch_qid_fk': '11', 'qid': 11, 'severity': 11, 'title': 'Vulner 11'},
                                        ]},
                        '2.2.2.2': {
                            'patches': [{'qid': 2, 'severity': 2, 'title': 'Patch 2'},
                                        {'qid': 22, 'severity': 22, 'title': 'Patch 22'}],
                            'vulners': [{'patch_qid_fk': '2', 'qid': 2, 'severity': 2, 'title': 'Vulner 2'},
                                        {'patch_qid_fk': '22', 'qid': 22, 'severity': 22, 'title': 'Vulner 22'}]}},
                    'status': 'finished',
                    'title': 'oat-req525-report-null_user-1909252223'}
test_patches = [{'qid': 1, 'severity': 1, 'title': 'Patch 1'},
                            {'qid': 2, 'severity': 2, 'title': 'Patch 2'},
                            {'qid': 3, 'severity': 3, 'title': 'Patch 3'}, ]
test_vulners = [{'qid': 1, 'severity': 1, 'title': 'Vulner 1'},
                {'qid': 2, 'severity': 2, 'title': 'Vulner 2'},
                {'qid': 3, 'severity': 3, 'title': 'Vulner 3'}, ]


class TestReport:

    @pytest.mark.parametrize('mock_api_get_side_effect', status_flows_json,
                             indirect=True)
    def test_get_result_flow(self, mock_api_get_side_effect):
        test_report = Report()
        test_report.init_api()

        response = test_report._get_result(sleep_time=0)
        assert response['status'] == 'finished' or 'failed'

    @pytest.mark.parametrize('mock_api_get_return_value', [{'status': 'running'}], indirect=True)
    def test_get_result_timeout(self, mock_api_get_return_value):
        test_report = Report()
        test_report.init_api()

        with pytest.raises(TimeoutError):
            test_report._get_result(sleep_time=0, timeout=0)

    @pytest.mark.parametrize('mock_api_post_return_value', [{'status': 'running', 'id': '42'}], indirect=True)
    def test_launch_report_state_change(self, mocker, mock_api_post_return_value):
        """

        """
        test_report = Report(title='test title')
        test_report.init_api()
        mocker.patch.object(test_report, '_get_ip_list')
        test_report._get_ip_list.return_value = ['1.1.1.1', '2.2.2.2']
        test_report._launch_report()

        assert test_report.qid == '42'
        assert test_report.status == 'running'
        test_report.api.post.assert_called_once_with({'servers': ['1.1.1.1', '2.2.2.2'], 'title': 'test title'})

    @pytest.mark.parametrize('mock_api_post_return_value', [{'status': 'running', 'id': '42'}], indirect=True)
    def test_launch_report_api_call(self, mocker, mock_api_post_return_value):
        """

        """
        test_report = Report(title='test title')
        test_report.init_api()
        mocker.patch.object(test_report, '_get_ip_list')
        test_report._get_ip_list.return_value = ['1.1.1.1', '2.2.2.2']
        test_report._launch_report()

        test_report.api.post.assert_called_once_with({'servers': ['1.1.1.1', '2.2.2.2'], 'title': 'test title'})

    def test_get_ip_list(self, mocker):
        mocker.patch.object(Report, 'servers')
        test_report = Report()
        test_report.servers = {'1.1.1.1': 'testserver1', '2.2.2.2': 'testserver2'}
        assert test_report._get_ip_list() == ['1.1.1.1', '2.2.2.2']

    @pytest.mark.parametrize('all_patches,already_assigned_patches',[pytest.param(test_patches, [], id='all_new'),
                                                                    pytest.param(test_patches, test_patches[:1], id='one_already_assigned')])
    def test_process_response_patches(self, mocker, patch_mock, all_patches, already_assigned_patches):
        mocker.patch.object(Patch, 'get_one_or_create')
        Patch.get_one_or_create = lambda x, **y: patch_mock(init_data=y)

        mocker.patch.object(Report, 'request')
        Report.request.request_servers['ip'].patches = [patch_mock(patch_dict) for patch_dict in already_assigned_patches]

        test_report = Report()
        session_mock = mocker.Mock()
        test_report._process_response_patches(session_mock, 'ip', all_patches)

        assert [patch['qid'] for patch in all_patches] == [patch.qid for patch in test_report.request.request_servers['ip'].patches ]

    @pytest.mark.parametrize('all_vulners,already_assigned_vulners',[pytest.param(test_vulners, [], id='all_new'),
                                                                     pytest.param(test_vulners, test_vulners[:1], id='one_already_assigned')])
    def test_process_response_vulners(self, mocker, vulner_mock, all_vulners, already_assigned_vulners):
        mocker.patch.object(Vulner, 'get_one_or_create')
        Vulner.get_one_or_create = lambda x, **y: vulner_mock(init_data=y)

        mocker.patch.object(Report, 'request')
        Report.request.request_servers['ip'].vulners = [vulner_mock(vulner_dict) for vulner_dict in already_assigned_vulners]

        test_report = Report()
        session_mock = mocker.Mock()
        test_report._process_response_vulners(session_mock, 'ip', all_vulners)

        assert [vulner['qid'] for vulner in all_vulners] == [vulner.qid for vulner in test_report.request.request_servers['ip'].vulners ]

    def test_process_response(self,mocker,server_mock,request_mock,patch_mock,vulner_mock):
        mocker.patch.object(Report, 'servers')
        mocker.patch.object(Report, '_process_response_patches')
        mocker.patch.object(Report, '_process_response_vulners')

        test_report = Report(id=42)
        test_report.servers = defaultdict(mocker.Mock)

        session_mock = mocker.Mock()
        test_report._process_response(test_report_data, session_mock)
        a=1

    # # @pytest.mark.parametrize('test_data', test_report_data)
    # def test_process_response(self,mocker,server_mock,request_mock,patch_mock,vulner_mock):
    #
    #     mocker.patch.object(Report, 'servers')
    #     mocker.patch.object(Report, 'request')
    #     test_report = Report()
    #     # test_report.servers = {'1.1.1.1': server_mock(), '2.2.2.2': server_mock()}
    #     test_report.servers = {server['ip']: server_mock() for server in test_report_data['servers'] }
    #     test_report.request = request_mock()
    #     test_report.request.request_servers = {ip: test_report.servers[ip] for ip in test_report.servers.keys()}
    #     for ip in test_report.servers.keys():
    #         test_report.request.request_servers[ip].patches = []
    #         test_report.request.request_servers[ip].vulners = []
    #     session_mock = mocker.Mock()
    #     test_report._process_response(test_report_data, session_mock)
    #     a = 1
