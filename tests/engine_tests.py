from pyramid import testing
import unittest
from webhook import engine

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

    def test_add_two_tables(self):
        """Adding two tables..."""
        dummy_data = { "commits":[\
        {\
         "added":[\
            "table.json",\
            "table2.json"\
         ],\
         "removed":[],\
         "modified":[]}]}
        result = engine.get_changes(dummy_data)
        self.assertIn('table.json',result[0])
        self.assertIn('table2.json',result[0])
        self.assertFalse(result[1])
