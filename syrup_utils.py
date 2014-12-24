import urllib
import urllib2
import json
import webapp2

from config import DEBUG, LOGGER


class SyrupConfigException(BaseException):
    pass


class Common(object):
    @staticmethod
    def debug_print(content):
        if DEBUG:
            print content

class Log(object):
    @staticmethod
    def create_entry(tag, message):
        if LOGGER is None:
            print tag + " >> " + message
        else:
            LOGGER(tag, message)


class APIUtils(object):

    class MetaData(object):
        def __init__(self):
            self.exists = False
            self.general = ""
            self.params = {}

        def form(self):
            vals = {
                "has_meta_data": self.exists,
                "meta_data": {
                    "params": self.params,
                    "general": self.general
                }
            }
            return vals

    class InternalRequest(object):
        def __init__(self, method='GET', endpoint_name='', base_uri='', uri_args={}):
            if endpoint_name == '':
                self.endpoint = "/"
            else:
                self.endpoint = webapp2.uri_for(endpoint_name, **uri_args)
            self.method = method
            self.base_uri = base_uri
            self.response = ''
            self.params = {}
            self.response_data = ''

        def send(self):
            if self.method == 'POST':
                data = urllib.urlencode(self.params)
                req = urllib2.Request(self.base_uri + self.endpoint, data)
            else:
                endpoint_with_params = self.base_uri + self.endpoint + "?"
                prefix = ""
                for key,value in self.params.items():
                    endpoint_with_params += prefix + key + "=" + value
                    prefix = "&"
                req = endpoint_with_params

            try:
                resp = urllib2.urlopen(req)
                return json.loads(resp.read())
            except urllib2.HTTPError as e:
                self.response_code = e.code
                self.response_data = e.read()
                return None


    @staticmethod
    def check_contract_conforms(contract, data, verify_true_action):
        for c_key, c_value in contract.items():
            # recursively follow subdirectories, contract follows down a level as well
            if isinstance(c_value, dict):
                try:
                    APIUtils.check_contract_conforms(c_value, data[c_key], verify_true_action)
                except KeyError:
                    APIUtils.check_partial_for_requires(c_value, verify_true_action)
            else:
                if c_value == "*" and isinstance(c_value, basestring):
                    pass
                elif isinstance(c_value, list):
                    sub_contract = c_value[0]
                    data_value = data[c_key]
                    #check for empty list, or empty list str representation (from json), or check for wildcard as second
                    #argument on list indicating that an empty list is ok
                    verify_empty_list_cond = data_value != '[]' and data_value != [] or c_value[1] == "*"
                    verify_true_action(verify_empty_list_cond, c_key + " is an empty list and it is required")

                    if isinstance(sub_contract, dict):
                        for item in data_value:
                            APIUtils.check_contract_conforms(sub_contract, item, verify_true_action)
                    else:
                        for item in data_value:
                            APIUtils.check_contract_conforms({c_key: sub_contract}, {c_key: item}, verify_true_action)
                elif c_value == "!" and isinstance(c_value, basestring):
                    try:
                        val = data[c_key]
                        verify_true_action(False, "value was included when contract excluded it")
                    except KeyError:
                        continue
                elif c_value == "+" and isinstance(c_value, basestring):
                    try:
                        data_value = data[c_key]
                        verify_none_list_cond = data_value != 'None' and data_value != None
                        verify_true_action(verify_none_list_cond, c_key + " (or a list item with " + c_key + ") is None and it is required")
                    except KeyError:
                        verify_true_action(False, "contract key '" + c_key + "' was not found")
                else:
                    verify_true_action(c_value == data[c_key], "key: '" + c_key + "' should be exactly >> " + c_value + " but is instead >> " + data[c_key])

    @staticmethod
    def check_partial_for_requires(partial, verify_true_action):
        for key, value in partial.items():
            if isinstance(value, dict):
                APIUtils.check_partial_for_requires(value, verify_true_action)
            elif isinstance(value, list):
                for list_item in value:
                    APIUtils.check_partial_for_requires(list_item, verify_true_action)
            else:
                verify_true_action(value == "*", "If data doesn't have a key for this nested element, "
                                             "all fields must be wildcard allowed")

