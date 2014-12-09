import unittest
import json
import os
from pyramid import testing
from mock import Mock

class FakeRequests(Mock):
    status_code = 200
    def __getitem__(self, dummy):
        #dummy_data = {  "ref":"refs/heads/dummy" }
        return '{"content":"objecccct"}'

class WebHookUnitTests(unittest.TestCase):
    """Testing..."""
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()
  
    def test_database_request(self):
        """Check if a request is sent to the database..."""
        from webhook.views import RootView
        json_data=open('testing_commits/add_from_master.json')
        mock_api = Mock()
        request = testing.DummyRequest()
        request.json_body = json.load(json_data)
        view_inst = RootView(request, api_service=mock_api)
        result = view_inst.default_view()
        mock_api.get.assert_called_with(os.environ.get('PUSH_URL'))

    #def test_master_branch(self):
    #    """Commit from master branch should pass..."""
    #    from webhook.views import RootView
    #    json_data=open('testing_commits/add_from_master.json')
    #    mock_api = Mock()
    #    mock_api.get = FakeRequests()
    #    request = testing.DummyRequest()
    #    request.json_body = json.load(json_data)
    #    view_inst = RootView(request, api_service=mock_api)
    #    result = view_inst.default_view()
    #    print mock_api.get.call_args
    #    print mock_api.get.method_calls
    #    self.assertIn('wrong branch',result.body)

    def test_wrong_branch(self):
        """Commit from wrong branch should fail..."""
        from webhook.views import RootView
        json_data=open('testing_commits/body_another_branch.json')
        mock_api = Mock(status_code=200)
        mock_api.get = Mock()
        request = testing.DummyRequest()
        request.json_body = json.load(json_data)
        view_inst = RootView(request, api_service=mock_api)
        result = view_inst.default_view()
        self.assertIn('wrong branch',result.body)
