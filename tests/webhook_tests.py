import unittest
import json
import os
from pyramid import testing
from mock import Mock

class WebHookFunctionalTests(unittest.TestCase):
    """Testing..."""
    def setUp(self):
        testing.setUp()
        self.config = testing.setUp()
        from webhook import main
        app = main.main({})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_root(self):
        """Getting from root should display info msg..."""
        res = self.testapp.get('/', status=200)
        self.assertTrue('This is a github webhook' in res.body)

    def tearDown(self):
        testing.tearDown()

class WebHookUnitTests(unittest.TestCase):
    """Testing..."""
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    # Mock in gevent is erroring
    # def test_database_request(self):
    #     """Check if a request is sent to the database..."""
    #     from webhook.views import RootView
    #     json_data=open('testing_commits/add_from_master.json')
    #     mock_api = Mock()
    #     request = testing.DummyRequest()
    #     request.json_body = json.load(json_data)
    #     view_inst = RootView(request, api_service=mock_api)
    #     result = view_inst.default_view()
    #     mock_api.get.assert_called_with(os.environ.get('GITHUB_WEBHOOK_GIT_URL'))

    def test_wrong_branch(self):
        """Commit from wrong branch should fail..."""
        from webhook.views import RootView
        json_data=open('testing_commits/body_another_branch.json')
        mock_api = Mock()
        request = testing.DummyRequest()
        request.json_body = json.load(json_data)
        view_inst = RootView(request, api_service=mock_api)
        result = view_inst.default_view()
        self.assertIn('wrong branch',result['error'])
