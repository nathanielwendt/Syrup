import webapp2
from syrup_handlers import SyrupSecureAPIHandler, SyrupAPIException

# Definition of view models.  This is typically defined in a view_models.py file
# The view_models class here simply represents the module specification you would
# have from separating it to another file.
class view_models():
    class Message(object):
        @staticmethod
        def view_contract():
            return {
                "message": "+"
            }

        @staticmethod
        def form_view(message):
            return {
                "message": message,
            }

    class Default(object):
        @staticmethod
        def view_contract():
            return {
                "status": "success"
            }


class MessageHelloHandler(SyrupSecureAPIHandler):
    def get(self):
        """
        This handler returns a welcome message to someone's name
        :param name: name to address in message
        """

        # Input contract is defined and checked, required fields will throw an exception
        # and set the response code and values so simply returning from the handler is sufficient
        contract = {
            "name": ["varchar","*"]
        }
        try:
            self.check_params_conform(contract)
        except SyrupAPIException:
            return

        message = "Hello, world to you: " + self.get_param("name")

        # View-model output is defined, populated, and sent
        self.set_response_view_model(view_models.Message.view_contract())
        self.api_response = view_models.Message.form_view(message)
        self.send_response()


# Definition of the routes and server config.  This should typically be done in a separate server.py file
# V1 is just demonstrating good design of api versioning
v1_routes = [
    #The name attribute of the Route class is important for the Syrup Bottler to identify resource and handler types
    # Format >> Resource-HandlerName
    webapp2.Route(r'/v1/message/hello', handler=MessageHelloHandler, name="Message-Hello"),
]
app = webapp2.WSGIApplication(routes = v1_routes, debug=True)

# Setup the syrup settings here
##### Syrup Settings #####
import config
config.DEBUG = True
config.OAUTH_ENABLED = False
# config.LOGGER =  // set your logging function here
config.APP = app
config.DEFAULT_VIEW_MODEL = view_models.Default


