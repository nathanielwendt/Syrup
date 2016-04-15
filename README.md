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
Syrup is developed with the mindset that each backend endpoint should define some input contract and some output view-model.  Additionally, the backend should be documented in a way that the internal documentation should automatically drive some external generation of API docs for the backend system (called Syrup Bottling).  The image below shows a general outline of what Syrup does.

![Syrup Model](http://www.nathanielwendt.com/content/images/2016/04/Screen-Shot-2016-04-15-at-5-09-32-PM.png)

* Input Contract

  The input contract is a set of expected parameters provided by the clients that should conform to some specifications (i.e. list of phone numbers, email, etc.).  If the contract doesn't conform, errors or warnings should be propagated to the user as well as appropriate HTTP response codes.
  
  Contracts are defined as dictionaries with:
  
        { 
            parameter_name: [ type, required/optional ] 
        }
  
  Required - "\*",  Optional - "\+"
  
  Available types can be found in validation.py:

        self.filters["bool"] = validators.StringBoolean()
        self.filters["url"] = validators.URL()
        self.filters["id"] = validators.String()
        self.filters["num"] = validators.Int()
        self.filters["geo"] = validators.String()
        self.filters["varchar"] = validators.String()
        self.filters["timestamp"] = validators.String()
        self.filters["email"] = validators.Email()
        self.filters["password"] = validators.String()
        self.filters["json"] = CustomValidators.JSON()
        
   This file also includes an example of the CustomValidators class in which you can extend to create your own parameter types for which to validate.
  
* Output View-Model

  The output view-model defines the expected response of the handler.  It is important to log internal errors/warnings/information if this expected view-model does not conform to its expectation.

* Syrup Bottler (Documentation)

  The syrup bottler is a utility that generates your api documentation.  Simply run the syrup bottler cap from within your /doc or /wiki directory and it will examine all properly formatted SyrupHandlers and generate handlers for each resource type in markdown syntax. You can see an example of the generated documentation by viewing the Message-API.md file in the root of this project.
 
## Example
There is an example under example.py that gives a sample hello world application implementing the three primary components of syrup as discussed above.

## Roadmap
1) Clean up the validators

2) Publish the currently commented web handlers

3) Create a separate example repo that contains the necessary appengine_config and yaml files to run out-of-the-box

  
