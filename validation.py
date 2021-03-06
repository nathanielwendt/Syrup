from lib.formencode import validators, Invalid
import urllib
from syrup_utils import APIUtils
import json

#Custom validation items
class CustomValidators(object):
    # this is simply an adapter that wraps the phone number validator after stripping the country code
    class CustomPhoneNumber(object):
        def to_python(self, entry):
            # perform some initial processing on the phone number
            validator = validators.PhoneNumber()
            return validator.to_python(entry)

    class JSON(object):
        def to_python(self, entry):
            try:
                as_json = json.loads(entry)
                return as_json
            except ValueError:
                raise Invalid("not valid json", entry, "json validator")


class CustomValidatorException(BaseException):
    def __init__(self, message):
        self.message = message

#does not maintain state of values checked
#simply maintains a list of warnings and violations for checked values
class Filter():
    #TODO: improve validation strength
    # GEO - check if coordinates make sense
    # timestamp - check if time can possibly be in that range
    def __init__(self):
        self.violations = {}
        self.warnings = {}
        self.filters = {}
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

    #Use to add a filter item
    def add_filter(self, name, filter_func):
        self.filters[name] = filter_func

    def validate(self, name, value, filter_type, required):
        #exception check here is for Nonetype values
        try:
            value = urllib.unquote(value)
        except:
            if required and name not in self.violations:
                self.violations[name] = filter_type + ", missing"
            elif not required and name not in self.warnings:
                self.warnings[name] = filter_type + ", missing"
            return

        entries = []
        if "list" in filter_type:
            index = filter_type.find("_")
            filter_type = filter_type[0:index]
            entries = json.loads(value)
            for entry in entries:
                self.check_value(name, filter_type, entry, required)
            return json.loads(value)
        # elif "tuple" in filter_type:
        #     index = filter_type.find("_")
        #     filter_type = filter_type[0:index]
        else:
            return self.check_value(name, filter_type, value, required)

        # Loop through items in case it is a list
        # for entry in entries:
        #     try:
        #         return self.filters[filter_type].to_python(entry)
        #     except lib.formencode.Invalid, e:
        #         if required and name not in self.violations:
        #             self.violations[name] = filter_type
        #         elif not required and name not in self.warnings:
        #             self.warnings[name] = filter_type
        #         return None

    def check_value(self, name, filter_type, entry, required):
        try:
            if required:
                if entry is None or entry == "":
                    raise Invalid("entry was included, but empty", None, None)
            return self.filters[filter_type].to_python(entry)
        except Invalid, e:
            if required and name not in self.violations:
                self.violations[name] = filter_type
            elif not required and name not in self.warnings:
                self.warnings[name] = filter_type
            return None