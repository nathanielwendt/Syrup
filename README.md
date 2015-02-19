# Syrup
Microframework built on Webapp2 for rapidly developing RESTful backends on Python AppEngine

## About
Syrup is a project born from my experience developing several Python AppEngine backends from scratch.  I wanted a faster way to create endpoints that validated inputs and outpus and could generate documentation automatically. 

## Use
Clone the repo into some /libs directory in your AppEngine project.  Syrup will be ready to go with a simple import such as

    from lib.syrup.syrup_handlers import SyrupSecureAPIHandler

    class MyHandler(SyrupSecureAPIHandler):
        def post(self):
          #handler code here just as you would do with Webapp2

## Philosophy
Syrup is developed with the mindset that each backend endpoint should define some input contract and some output view-model.  Additionally, the backend should be documented in a way that the internal documentation should automatically drive some external generation of API docs for the backend system (called Syrup Bottling).

* Input Contract

  The input contract is a set of expected parameters provided by the clients that should conform to some specifications (i.e. list of phone numbers, email, etc.).  If the contract doesn't conform, errors or warnings should be propagated to the user as well as appropriate HTTP response codes.
  
* Output View-Model

  The output view-model defines the expected response of the handler.  It is important to log internal errors/warnings/information if this expected view-model does not conform to its expectation.

* Syrup Bottler

  The syrup bottler is a utility that resides in your documentation or /wiki folder representating your api documentation.  Simply run the bottler and it will examine all properly formatted SyrupHandlers and generate handlers for each resource type.
  

  
