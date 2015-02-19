import json
import webapp2
import server
import unittest
from google.appengine.datastore import datastore_stub_util
from google.appengine.ext import testbed
from syrup_utils import APIUtils, SyrupConfigException
import inspect
from config import APP

class SyrupTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.INVALID_ID = "9999999999999"
        self.endpoint = ''
        self.method = 'GET'
        self.response = ''
        self.params = {}
        self.response_data = ''
        self.patches = {}
        super(SyrupTest, self).__init__(*args)

    def setUp(self):
        super(SyrupTest, self).setUp()
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()

        # Next, declare which service stubs you want to use.
        if hasattr(self, 'policy'):
            self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)
        else:
            self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()
        self.restore_patches()

    def restore_patches(self):
        for func_name,val in self.patches.iteritems():
            func = val[0]
            import_val = val[1]
            exec(import_val)
            if inspect.isfunction(func):
                str = func_name + "=staticmethod(self.patches[func_name][0])"
            else:
                str = func_name + "=self.patches[func_name][0]"
            exec str

    #Patches a method for use in a single test only, restores the state of the patch in tearDown
    # example self.patch('external.MyModule.myfunction', 'myfunction_mock')
    def patch(self, import_val, function_name, replacement_name):
        exec(import_val)
        func = eval(function_name)
        self.patches[function_name] = [func,import_val]
        if inspect.isfunction(func):
            str = function_name + "=staticmethod(" + replacement_name + ")"
        else:
            str = function_name + "=" + replacement_name
        exec str

    def send(self):
        if self.method == 'POST':
            request = webapp2.Request.blank(self.endpoint, POST=self.params)
        #GET, PUT, DELETE methods here
        else:
            endpoint_with_params = self.endpoint + "?"
            prefix = ""
            for key,value in self.params.items():
                endpoint_with_params += prefix + key + "=" + value
                prefix = "&"
            request = webapp2.Request.blank(endpoint_with_params)
            request.method = self.method

        if APP is None:
            raise SyrupConfigException("Need to select app in config")
        self.response = request.get_response(APP)

        try:
            self.response_data = json.loads(self.response.body)
        except ValueError:
            self.response_data = {}

    def expect_resp_code(self, code):
        self.assertEqual(self.response.status_int, code)

    def expect_resp_param(self, name, value=None):
        if value is None:
            self.assertIsNotNone(self.response_data[name])
        else:
            self.assertEqual(self.response_data[name], value)

    def expect_resp_conforms(self, contract):
        APIUtils.check_contract_conforms(contract, self.response_data, self.assertTrue)


# Consistency Test class guarantees that we are viewing the datastore with full eventual consistency
# This means that it will test that our strong consistency assumptions are correct
class SyrupConsistencyTest(SyrupTest):
    def setUp(self):
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=0)
        super(SyrupConsistencyTest, self).setUp()
