from pyramid import testing
import unittest
import json
from webhook import engine
from mock import Mock

class EngineUnitTests(unittest.TestCase):
    """Testing..."""
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()
  
    def test_get_author(self):
        """Should return dummy author..."""
        dummy_data = { "commits":[ { "author":{  "name":"dummy"  }}]}
        result = engine.get_author(dummy_data)
        self.assertEquals('dummy',result)

    def test_get_branch(self):
        """Should return dummy branch..."""
        dummy_data = {  "ref":"refs/heads/dummy" }
        result = engine.get_branch(dummy_data)
        self.assertEquals('dummy',result)

    #def test_github_json(self):
    #    dummy_data = {  "content":"refs/heads/dummy" }
    #    request = testing.DummyRequest()
    #    request.json = Mock(return_value=json.dumps(dummy_data))
    #    result = engine.get_github_json(request)
    #    self.assertEquals('dummy',result)
        
   
    def test_add_one_table(self):
        """Adding one table..."""
        dummy_data = { "commits":[\
        {\
         "added":[\
            "table.json"\
         ],\
         "removed":[],\
         "modified":[]}]}
        result = engine.get_changes(dummy_data)
        self.assertEquals('table.json',''.join(result[0]))
        self.assertFalse(result[1])

    def test_add_two_tables_update_one(self):
        """Adding two tables and updating one..."""
        dummy_data = { "commits":[\
        {\
         "added":[\
            "table.json",\
            "table2.json"\
         ],\
         "removed":[],\
         "modified":["table3.json"]}]}
        result = engine.get_changes(dummy_data)
        self.assertIn('table.json',result[0])
        self.assertIn('table2.json',result[0])
        self.assertIn('table3.json',result[1])
        self.assertFalse(result[2])

    def test_add_two_tables_update_one_remove_one(self):
        """Adding two tables, updating one and removing other..."""
        dummy_data = { "commits":[\
        {\
         "added":[\
            "table.json",\
            "table2.json"\
         ],\
         "removed":["table3.json"],\
         "modified":["table4.json"]}]}
        result = engine.get_changes(dummy_data)
        self.assertIn('table.json',result[0])
        self.assertIn('table2.json',result[0])
        self.assertIn('table3.json',result[2])
        self.assertIn('table4.json',result[1])
