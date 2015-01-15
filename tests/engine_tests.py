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

    def test_whitelist(self):
        """only .json files and files/name.ext should pass..."""
        valid_files = ['table.json', 'lala/files/hha/lala.tst']
        result = engine._whitelist(valid_files)
        self.assertEquals(valid_files,result)

        valid_files = ['lala/json/lala.json.table.jison', 'lala/filess/lala.tst']
        result = engine._whitelist(valid_files)
        for items in valid_files:
            self.assertNotIn(items,result)

    def test_get_base_url(self):
        """Getting base URL from GIT webhook JSON..."""
        dummy_data = {'commits':[{'url':'https://github.com/andrecp/github_webhook/commit/852d05ed0c096df331'}]}
        result = engine.get_base_url(dummy_data)
        self.assertEquals('https://github.com/andrecp/github_webhook/',result)
        
   
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
