from types import SimpleNamespace

status = {'NEW': 'new',
          'STARTING': 'starting',
          'RUNNING': 'running',
          'FINISHED': 'finished',
          'FAILED': 'failed'
          }

test_report_data = {'datetime': '2019-09-11T01:16:18+00:00', 'id': 6,
                    'servers': [{'ip': '10.0.2.3'}, {'ip': '20.0.2.3'}, {'ip': '30.0.1.1'}, {'ip': '30.0.2.3'}],
                    'servers_data': {'10.0.2.3': {'patches': [{'qid': 1, 'severity': 5, 'title': 'Patch 1'},
                                                              {'qid': 12, 'severity': 1, 'title': 'Patch 12'},
                                                              {'qid': 21, 'severity': 1, 'title': 'Patch 21'},
                                                              {'qid': 26, 'severity': 2, 'title': 'Patch 26'},
                                                              {'qid': 30, 'severity': 3, 'title': 'Patch 30'},
                                                              {'qid': 31, 'severity': 5, 'title': 'Patch 31'},
                                                              {'qid': 36, 'severity': 5, 'title': 'Patch 36'},
                                                              {'qid': 38, 'severity': 4, 'title': 'Patch 38'},
                                                              {'qid': 40, 'severity': 3, 'title': 'Patch 40'},
                                                              {'qid': 49, 'severity': 4, 'title': 'Patch 49'}],
                                                  'vulners': [{'patch_qid_fk': '1', 'qid': 5, 'severity': 4,
                                                               'title': 'Vulner 5'},
                                                              {'patch_qid_fk': '12', 'qid': 229, 'severity': 1,
                                                               'title': 'Vulner 229'},
                                                              {'patch_qid_fk': '21', 'qid': 418, 'severity': 5,
                                                               'title': 'Vulner 418'},
                                                              {'patch_qid_fk': '26', 'qid': 512, 'severity': 2,
                                                               'title': 'Vulner 512'},
                                                              {'patch_qid_fk': '30', 'qid': 593, 'severity': 1,
                                                               'title': 'Vulner 593'},
                                                              {'patch_qid_fk': '31', 'qid': 617, 'severity': 1,
                                                               'title': 'Vulner 617'},
                                                              {'patch_qid_fk': '36', 'qid': 715, 'severity': 4,
                                                               'title': 'Vulner 715'},
                                                              {'patch_qid_fk': '38', 'qid': 757, 'severity': 3,
                                                               'title': 'Vulner 757'},
                                                              {'patch_qid_fk': '40', 'qid': 799, 'severity': 1,
                                                               'title': 'Vulner 799'},
                                                              {'patch_qid_fk': '49', 'qid': 967, 'severity': 3,
                                                               'title': 'Vulner 967'}]}, '20.0.2.3': {
                        'patches': [{'qid': 1, 'severity': 5, 'title': 'Patch 1'},
                                    {'qid': 12, 'severity': 1, 'title': 'Patch 12'},
                                    {'qid': 21, 'severity': 1, 'title': 'Patch 21'},
                                    {'qid': 22, 'severity': 5, 'title': 'Patch 22'},
                                    {'qid': 26, 'severity': 2, 'title': 'Patch 26'},
                                    {'qid': 29, 'severity': 2, 'title': 'Patch 29'},
                                    {'qid': 30, 'severity': 3, 'title': 'Patch 30'},
                                    {'qid': 31, 'severity': 5, 'title': 'Patch 31'},
                                    {'qid': 34, 'severity': 5, 'title': 'Patch 34'},
                                    {'qid': 35, 'severity': 2, 'title': 'Patch 35'},
                                    {'qid': 36, 'severity': 5, 'title': 'Patch 36'},
                                    {'qid': 38, 'severity': 4, 'title': 'Patch 38'},
                                    {'qid': 39, 'severity': 4, 'title': 'Patch 39'},
                                    {'qid': 40, 'severity': 3, 'title': 'Patch 40'},
                                    {'qid': 44, 'severity': 2, 'title': 'Patch 44'},
                                    {'qid': 46, 'severity': 4, 'title': 'Patch 46'},
                                    {'qid': 48, 'severity': 5, 'title': 'Patch 48'},
                                    {'qid': 49, 'severity': 4, 'title': 'Patch 49'}],
                        'vulners': [{'patch_qid_fk': '12', 'qid': 236, 'severity': 4, 'title': 'Vulner 236'},
                                    {'patch_qid_fk': '22', 'qid': 434, 'severity': 5, 'title': 'Vulner 434'},
                                    {'patch_qid_fk': '29', 'qid': 561, 'severity': 2, 'title': 'Vulner 561'},
                                    {'patch_qid_fk': '34', 'qid': 666, 'severity': 5, 'title': 'Vulner 666'},
                                    {'patch_qid_fk': '35', 'qid': 692, 'severity': 3, 'title': 'Vulner 692'},
                                    {'patch_qid_fk': '39', 'qid': 772, 'severity': 1, 'title': 'Vulner 772'},
                                    {'patch_qid_fk': '44', 'qid': 879, 'severity': 2, 'title': 'Vulner 879'},
                                    {'patch_qid_fk': '46', 'qid': 906, 'severity': 5, 'title': 'Vulner 906'},
                                    {'patch_qid_fk': '46', 'qid': 919, 'severity': 4, 'title': 'Vulner 919'},
                                    {'patch_qid_fk': '48', 'qid': 955, 'severity': 5, 'title': 'Vulner 955'}]},
                                     '30.0.1.1': {'patches': [{'qid': 1, 'severity': 5, 'title': 'Patch 1'},
                                                              {'qid': 11, 'severity': 5, 'title': 'Patch 11'},
                                                              {'qid': 12, 'severity': 1, 'title': 'Patch 12'},
                                                              {'qid': 14, 'severity': 5, 'title': 'Patch 14'},
                                                              {'qid': 19, 'severity': 4, 'title': 'Patch 19'},
                                                              {'qid': 21, 'severity': 1, 'title': 'Patch 21'},
                                                              {'qid': 22, 'severity': 5, 'title': 'Patch 22'},
                                                              {'qid': 26, 'severity': 2, 'title': 'Patch 26'},
                                                              {'qid': 29, 'severity': 2, 'title': 'Patch 29'},
                                                              {'qid': 30, 'severity': 3, 'title': 'Patch 30'},
                                                              {'qid': 31, 'severity': 5, 'title': 'Patch 31'},
                                                              {'qid': 34, 'severity': 5, 'title': 'Patch 34'},
                                                              {'qid': 35, 'severity': 2, 'title': 'Patch 35'},
                                                              {'qid': 36, 'severity': 5, 'title': 'Patch 36'},
                                                              {'qid': 37, 'severity': 5, 'title': 'Patch 37'},
                                                              {'qid': 38, 'severity': 4, 'title': 'Patch 38'},
                                                              {'qid': 39, 'severity': 4, 'title': 'Patch 39'},
                                                              {'qid': 40, 'severity': 3, 'title': 'Patch 40'},
                                                              {'qid': 43, 'severity': 3, 'title': 'Patch 43'},
                                                              {'qid': 44, 'severity': 2, 'title': 'Patch 44'},
                                                              {'qid': 46, 'severity': 4, 'title': 'Patch 46'},
                                                              {'qid': 48, 'severity': 5, 'title': 'Patch 48'},
                                                              {'qid': 49, 'severity': 4, 'title': 'Patch 49'}],
                                                  'vulners': [{'patch_qid_fk': '11', 'qid': 204, 'severity': 4,
                                                               'title': 'Vulner 204'},
                                                              {'patch_qid_fk': '12', 'qid': 231, 'severity': 2,
                                                               'title': 'Vulner 231'},
                                                              {'patch_qid_fk': '14', 'qid': 273, 'severity': 4,
                                                               'title': 'Vulner 273'},
                                                              {'patch_qid_fk': '19', 'qid': 364, 'severity': 5,
                                                               'title': 'Vulner 364'},
                                                              {'patch_qid_fk': '26', 'qid': 511, 'severity': 5,
                                                               'title': 'Vulner 511'},
                                                              {'patch_qid_fk': '37', 'qid': 737, 'severity': 2,
                                                               'title': 'Vulner 737'},
                                                              {'patch_qid_fk': '43', 'qid': 846, 'severity': 4,
                                                               'title': 'Vulner 846'},
                                                              {'patch_qid_fk': '43', 'qid': 850, 'severity': 3,
                                                               'title': 'Vulner 850'},
                                                              {'patch_qid_fk': '44', 'qid': 871, 'severity': 1,
                                                               'title': 'Vulner 871'},
                                                              {'patch_qid_fk': '48', 'qid': 950, 'severity': 2,
                                                               'title': 'Vulner 950'}]}, '30.0.2.3': {
                            'patches': [{'qid': 1, 'severity': 5, 'title': 'Patch 1'},
                                        {'qid': 8, 'severity': 5, 'title': 'Patch 8'},
                                        {'qid': 11, 'severity': 5, 'title': 'Patch 11'},
                                        {'qid': 12, 'severity': 1, 'title': 'Patch 12'},
                                        {'qid': 14, 'severity': 5, 'title': 'Patch 14'},
                                        {'qid': 19, 'severity': 4, 'title': 'Patch 19'},
                                        {'qid': 21, 'severity': 1, 'title': 'Patch 21'},
                                        {'qid': 22, 'severity': 5, 'title': 'Patch 22'},
                                        {'qid': 23, 'severity': 3, 'title': 'Patch 23'},
                                        {'qid': 26, 'severity': 2, 'title': 'Patch 26'},
                                        {'qid': 29, 'severity': 2, 'title': 'Patch 29'},
                                        {'qid': 30, 'severity': 3, 'title': 'Patch 30'},
                                        {'qid': 31, 'severity': 5, 'title': 'Patch 31'},
                                        {'qid': 32, 'severity': 3, 'title': 'Patch 32'},
                                        {'qid': 34, 'severity': 5, 'title': 'Patch 34'},
                                        {'qid': 35, 'severity': 2, 'title': 'Patch 35'},
                                        {'qid': 36, 'severity': 5, 'title': 'Patch 36'},
                                        {'qid': 37, 'severity': 5, 'title': 'Patch 37'},
                                        {'qid': 38, 'severity': 4, 'title': 'Patch 38'},
                                        {'qid': 39, 'severity': 4, 'title': 'Patch 39'},
                                        {'qid': 40, 'severity': 3, 'title': 'Patch 40'},
                                        {'qid': 43, 'severity': 3, 'title': 'Patch 43'},
                                        {'qid': 44, 'severity': 2, 'title': 'Patch 44'},
                                        {'qid': 46, 'severity': 4, 'title': 'Patch 46'},
                                        {'qid': 48, 'severity': 5, 'title': 'Patch 48'},
                                        {'qid': 49, 'severity': 4, 'title': 'Patch 49'}],
                            'vulners': [{'patch_qid_fk': '8', 'qid': 150, 'severity': 3, 'title': 'Vulner 150'},
                                        {'patch_qid_fk': '23', 'qid': 454, 'severity': 1, 'title': 'Vulner 454'},
                                        {'patch_qid_fk': '29', 'qid': 566, 'severity': 3, 'title': 'Vulner 566'},
                                        {'patch_qid_fk': '31', 'qid': 608, 'severity': 2, 'title': 'Vulner 608'},
                                        {'patch_qid_fk': '32', 'qid': 632, 'severity': 5, 'title': 'Vulner 632'},
                                        {'patch_qid_fk': '32', 'qid': 640, 'severity': 4, 'title': 'Vulner 640'},
                                        {'patch_qid_fk': '37', 'qid': 734, 'severity': 2, 'title': 'Vulner 734'},
                                        {'patch_qid_fk': '38', 'qid': 749, 'severity': 2, 'title': 'Vulner 749'},
                                        {'patch_qid_fk': '38', 'qid': 754, 'severity': 4, 'title': 'Vulner 754'},
                                        {'patch_qid_fk': '48', 'qid': 945, 'severity': 3, 'title': 'Vulner 945'}]}},
                    'status': 'finished', 'title': 'test'}