import json
from lib.oauthlib.common import Request as OAuth1Request
from lib.oauthlib.oauth1 import Client,SIGNATURE_TYPE_BODY
#from appengine_config import jinja_environment
from webapp2_extras import jinja2
import validation
import webapp2
from syrup_utils import APIUtils
import config
from config import OAUTH_ENABLED, DEFAULT_VIEW_MODEL


class SyrupAPIHandler(webapp2.RequestHandler):
    def __init__(self, request, response):
        self.initialize(request, response)
        self.api_response = {}
        self.resp_code = '400'
        self.meta_data = APIUtils.MetaData()
        self.view_model = {}
        self.safe_params = {}
        self.param_violations = []
        self.param_violations = []

    def set_response_code(self, code):
        self.resp_code = code

    def set_meta_data(self, meta_data):
        self.meta_data = meta_data

    def set_response_view_model(self, view_model):
        self.view_model = view_model

    # Makes the objects data uniform according the the API specs
    # All json will be formatted as follows
    # all values will be strings EXCEPT for lists
    # the values within a list will adhere to the same rules
    def uniform_output(self, object):
        for key,value in object.items():
            if isinstance(value, list):
                temp_list = []
                for item in value:
                    if isinstance(item, dict):
                        self.uniform_output(item)
                    temp_list.append(item)
                object[key] = temp_list
            elif isinstance(value, dict):
                self.uniform_output(value)
            elif not isinstance(value, basestring):
                object[key] = str(value)
            else:
                object[key] = value

    def set_default_success_response(self):
        self.api_response = config.DEFAULT_VIEW_MODEL

    def send_response(self):
        if self.view_model:
            def verify_true_action(exp, printout):
                if not exp:
                    print "Outgoing Contract [" + self.__class__.__name__ + "]", printout
                    #APIUtils.Log.create_entry("Outgoing Contract [" + self.__class__.__name__ + "]", printout)

            APIUtils.check_contract_conforms(self.view_model, self.api_response, verify_true_action)

        if self.meta_data.exists:
            meta_data = self.meta_data.form()
            self.final_response = dict(self.api_response.items() + meta_data.items())
        else:
            self.final_response = self.api_response

        self.uniform_output(self.final_response)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(self.final_response))

    def get_param(self, param, safe=True):
        try:
            if safe and self.safe_params:
                #if param is being retrieved, actually exists, and is malformed
                #should treat the param as a required param and throw an error
                if self.meta_data.params.get(param) is not None and\
                            self.safe_params[param] is not None:
                    self.abort(400, "optional param: " + param + " was included and malformed >> "
                               +self.meta_data.params.get(param))

                return self.safe_params[param]
            else:
                return self.request.params[param]
        except KeyError, e:
            return None

    def check_params_conform(self, contract):
        filter = validation.Filter()
        for key, value in contract.items():
            if value[1] == "+":
                param = self.get_param(key, safe=False)
                safe_param = filter.validate(key, param, value[0], True)
                self.safe_params[key] = safe_param
            elif value[1] == "*":
                try:
                    param = self.get_param(key, safe=False)
                    filter.validate(key, param, value[0], False)
                    self.safe_params[key] = param
                except:
                    self.safe_params[key] = None
                    continue

        if filter.warnings:
            self.meta_data.exists = True
            self.meta_data.general = "Optional parameter(s) were not formatted properly, will be omitted"
            self.meta_data.params = {}
            for violation, filter_type in filter.warnings.items():
                self.meta_data.params[violation] = "not formatted according to " + filter_type

        if filter.violations:
            self.response.status_int = 400
            self.meta_data.exists = True
            self.meta_data.general = "Required parameter(s) were not formatted properly"
            self.meta_data.params = {}
            for violation, filter_type in filter.violations.items():
                self.meta_data.params[violation] = "not formatted according to " + filter_type
            self.send_response()
            raise SyrupAPIException()


class SyrupSecureAPIHandler(SyrupAPIHandler):
    def abort(self, code, *args, **kwargs):
        print code, " >> ", args[0]
        super(SyrupAPIHandler, self).abort(code, *args, **kwargs)

    def dispatch(self):
        if OAUTH_ENABLED:
            method = self.request.method
            url = self.request.url
            headers = self.request.headers
            body = self.request.body
            cand_signature = self.request.params["oauth_signature"]
            req = OAuth1Request(uri=url,http_method=method,body=body,headers=headers,encoding='utf-8')

            consumer_key = self.request.params["oauth_consumer_key"]
            consumer_secret = self.get_consumer_secret(consumer_key)

            if consumer_secret is None:
                print "cant find consumer"
                self.abort(403)

            client_key = consumer_key
            client_secret = consumer_secret
            client = Client(client_key=client_key,client_secret=client_secret,signature_type=SIGNATURE_TYPE_BODY)
            actual_signature = client.get_oauth_signature(req)

            print actual_signature
            print cand_signature

            if actual_signature == cand_signature:
                print "success!"
                super(SyrupSecureAPIHandler, self).dispatch()
            else:
                print "failure"
                self.abort(403)
        else:
            super(SyrupSecureAPIHandler, self).dispatch()

    #Override this method to provide the consumer secret
    def get_consumer_secret(self, consumer_key):
        return None

# class SyrupWebHandler(webapp2.RequestHandler):
#
#     def __init__(self, request, response):
#         self.initialize(request, response)
#         self.data = {}
#
#         paths = {
#             "home": self.request.application_url,
#         }
#         self.data["paths"] = paths
#         self.base_uri = self.request.application_url
#
#         self.data["resources"] = {
#             "js": [],
#             "css": []
#         }
#
#     @webapp2.cached_property
#     def jinja2(self):
#         return jinja2.get_jinja2(app=self.app)
#
#     def render_template(self, filename, context):
#         template = jinja_environment.get_template(filename)
#         self.response.out.write(template.render(context))
#
#     def redirect_template(self, uri, data):
#         self.render_template(uri, data)
#
#     def get(self, **kwargs):
#         try:
#             self.handle_get(**kwargs)
#         except SyrupWebException, e:
#             self.data["error"] = e.data
#             print self.data
#             self.redirect_template(e.redirect_uri, self.data)
#
#     def post(self, **kwargs):
#         try:
#             self.handle_post(**kwargs)
#         except SyrupWebException, e:
#             self.data["error"] = e.data
#             self.redirect_template(e.redirect_uri, self.data)
#
#     def handle_get(self, **kwargs):
#         self.abort(405)
#
#     def handle_post(self, **kwargs):
#         self.abort(405)
#
#     def get_param(self, param, required=True):
#         try:
#             return self.request.params[param]
#         except KeyError, e:
#             if required:
#                 self.abort(400)
#             else:
#                 return ""
#
#     #convenience method that automatically includes self.request.application_url in creating request
#     def get_internal_api_request(self, method, endpoint_name, uri_args={}):
#         return APIUtils.InternalRequest(method, endpoint_name, self.request.application_url, uri_args)



#Dummy exception to indicate that handler needs to return since error has
#been set and send_response has been called
class SyrupAPIException(BaseException):
    pass

class SyrupWebException(BaseException):
    def __init__(self, redirect, message):
        # Call the base class constructor with the parameters it needs
        super(SyrupWebException, self).__init__(message)
        self.data = message
        self.redirect_uri = redirect